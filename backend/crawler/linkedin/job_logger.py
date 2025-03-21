import logging
from datetime import datetime

def get_logger(name, dir):
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = f'app_{timestamp}.log'    

    # Create a logger object
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set the logging level to DEBUG

    # Create a console handler and set its level to INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Only show INFO and higher level logs in console

    # Create a file handler and set its level to DEBUG
    file_handler = logging.FileHandler(dir + log_filename)
    file_handler.setLevel(logging.INFO)  # Show DEBUG and higher level logs in file

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)    

    return logger