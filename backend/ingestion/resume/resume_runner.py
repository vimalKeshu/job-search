import os 
import sys
import time

from backend.ingestion.resume.resume_ops import *
from langchain_community.document_loaders import PyPDFLoader

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


if __name__ == '__main__':
    resume_dir = parentdir + "/storage/test/resume"

    # Iterate over files in the directory
    for filename in os.listdir(resume_dir):
        # Check if the current file is a file (not a directory)
        file = os.path.join(resume_dir, filename)
        if os.path.isfile(file):
            loader = PyPDFLoader(file)
            pages = loader.load_and_split()
            text = ''
            i = 0
            total_pages = len(pages)

            logging.debug('total_pages', total_pages)
            for page in pages:
                text = page.page_content

                embedding = get_embedding(text=text, model=EMBEDDING_MODEL)
                store_resume_data(embedding=embedding,
                                  doc=text,
                                  id=filename + '_' + str(i),
                                  metadata={'name': filename,
                                            'epoch': int(time.time()),
                                            'page': i,
                                            'pages': total_pages,
                                            'status': 'in_progress',
                                            'stage': 'resume_embedding'})
                i = i + 1
                    
    extract_and_store_resume_metadata()