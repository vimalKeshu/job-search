import os
import json
import random
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import Dataset, DataLoader, random_split
from torch.utils.data.distributed import DistributedSampler
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import T5Tokenizer, T5ForConditionalGeneration, AdamW
from huggingface_hub import HfApi, Repository
import hydra
from omegaconf import DictConfig, OmegaConf
from pathlib import Path
import wandb
from datasets import load_dataset
import numpy as np
from tqdm import tqdm

os.environ["TORCH_DISTRIBUTED_DEBUG"] = "DETAIL"  # or "DETAIL" for even more detailed logs
current_directory = os.path.dirname(os.path.abspath(__file__))

try:
    from torch.cuda.amp import autocast, GradScaler
except:
    from torch.amp import autocast, GradScaler

def set_seed(seed):
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    # Ensures deterministic behavior for CuDNN backend. 
    # this may slow down training.
    # torch.backends.cudnn.deterministic = True
    # torch.backends.cudnn.benchmark = False

class JobDataset(Dataset):
    def __init__(self, samples, tokenizer, max_input_length=2048, max_output_length=512):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        example = self.samples[idx]
        input_text = "Extract job details: " + example['source_text']
        job_json = json.loads(example['target_text'])
        job_json = {
            'role': job_json['title'],
            'company': job_json['company'],
            'location': job_json.get('location', ''),
            'salary': job_json.get('salary', '')
        }
        target_text = json.dumps(job_json)
        inputs = self.tokenizer(
            input_text, max_length=self.max_input_length, truncation=True,
            padding='max_length', return_tensors="pt"
        )
        targets = self.tokenizer(
            target_text, max_length=self.max_output_length, truncation=True,
            padding='max_length', return_tensors="pt"
        )
        return {
            "input_ids": inputs["input_ids"].squeeze(),
            "attention_mask": inputs["attention_mask"].squeeze(),
            "labels": targets["input_ids"].squeeze()
        }

def train(rank, world_size, cfg):
    print(f"Process {rank} is starting training.")    
    
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"

    # Set seed for reproducibility (all processes use the same seed)
    set_seed(cfg.training.seed)

    # Initialize distributed training and device
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)
    device = torch.device(f"cuda:{rank}")
    print(f"Running on device: {device}")
    torch.cuda.memory_summary(device, abbreviated=False)

    if rank == 0:
        wandb.init(project=cfg.wandb.project, name=cfg.wandb.run_name)
        wandb.config.update(OmegaConf.to_container(cfg, resolve=True)) # Convert Hydra DictConfig to a standard dictionary for wandb

    # Load tokenizer & model
    tokenizer = T5Tokenizer.from_pretrained(cfg.model.name)
    model = T5ForConditionalGeneration.from_pretrained(cfg.model.name).to(device)
    model = DDP(model, device_ids=[rank], output_device=rank) # wrap model in DDP
    
    # Load and split dataset
    raw_dataset = load_dataset(cfg.dataset.name)["train"]
    dataset = JobDataset(raw_dataset, tokenizer)
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_sampler = DistributedSampler(train_dataset, num_replicas=world_size, rank=rank)
    val_sampler = DistributedSampler(val_dataset, num_replicas=world_size, rank=rank)
    
    train_loader = DataLoader(train_dataset, batch_size=cfg.training.batch_size, sampler=train_sampler, num_workers=world_size)
    val_loader = DataLoader(val_dataset, batch_size=cfg.validation.batch_size, sampler=val_sampler, num_workers=world_size)
    
    optimizer = AdamW(model.parameters(), lr=cfg.training.lr)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.training.epochs)
    scaler = GradScaler()
    initial_epoch = 0
    
    checkpoint_path = os.path.join(current_directory, cfg.training.checkpoint_dir_name, 'checkpoint.pt')
    if os.path.exists(checkpoint_path):
        print(f"Loading checkpoint from {checkpoint_path}")
        state = torch.load(checkpoint_path, map_location=device)
        model.module.load_state_dict(state['model_state_dict'])
        optimizer.load_state_dict(state['optimizer_state_dict'])
        scheduler.load_state_dict(state['scheduler_state_dict'])
        initial_epoch = state['epoch'] + 1
    else:
        print('No model to preload, starting from scratch')


    dist.barrier() # wait for all processes to finish
    
    print(f'start training for {device}')
    for epoch in range(initial_epoch, cfg.training.epochs):
        train_sampler.set_epoch(epoch)

        # training
        model.train()
        total_loss = 0.0
        optimizer.zero_grad()
        for i, batch in enumerate(tqdm(train_loader, desc=f"Epoch {epoch+1}")):
            print(f'{i}th batch for {device}')
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()
            with autocast():
                outputs = model(**batch)
                loss = outputs.loss
                total_loss += loss.item()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()            
            optimizer.zero_grad(set_to_none=True)
            print('Updated the weights parameters...')

        avg_loss = total_loss / len(train_loader)
        scheduler.step()  # update LR per epoch
        print(f'completed {i}th batch for {device}')

        # Logging (only on rank 0)
        if rank == 0:
            # Validation
            model.eval()
            total_val_loss = 0.0
            with torch.no_grad():
                for batch in val_loader:
                    outputs = model(**batch)
                    total_val_loss += outputs.loss.item()
            avg_val_loss = total_val_loss / len(val_loader)
            print(f'validation for {device}')

            print(f"Epoch {epoch}, Train Loss: {avg_loss}, Validation Loss: {avg_val_loss}")
            grad_norm = torch.nn.utils.clip_grad_norm_(model.module.parameters(), max_norm=1.0)
            wandb.log({
                "epoch": epoch, 
                "train_loss": avg_loss, 
                "val_loss": avg_val_loss,
                "learning_rate": scheduler.get_last_lr()[0],
                "grad_norm": grad_norm,
                "gpu_memory": torch.cuda.max_memory_allocated() / 1e9,
            })
            
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.module.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict()
            }, checkpoint_path)

            print(f"Model checkpoint saved at {checkpoint_path}")
    
    # Save final model (only on rank 0)
    if rank == 0:
        model_dir = os.path.join(current_directory, cfg.training.save_path)
        tokenizer.save_pretrained(model_dir)
        model.module.save_pretrained(model_dir)
        repo = Repository(local_dir=model_dir, clone_from=cfg.huggingface.repo_name, use_auth_token=True)
        repo.push_to_hub(commit_message="final trained job parser model upload")
        wandb.finish()
    
    dist.destroy_process_group()

@hydra.main(config_path=".", config_name="config", version_base=None)
def main(cfg: DictConfig):
    # create model save directory
    save_path = os.path.join(current_directory, cfg.training.save_path)
    Path(save_path).mkdir(parents=True, exist_ok=True)    
    
    # create checkpoint directory
    checkpoint_path = os.path.join(current_directory, cfg.training.checkpoint_dir_name)
    Path(checkpoint_path).mkdir(parents=True, exist_ok=True)

    world_size = torch.cuda.device_count()
    mp.spawn(train, args=(world_size, cfg), nprocs=world_size, join=True)

if __name__ == "__main__":
    wandb.login()
    main()
