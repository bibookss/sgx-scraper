import os
import logging

# Define logging format
def configure_logging(log_level='INFO'):
    '''Configure logging'''
    log_path = os.path.join(os.getcwd(), 'logs')
    log_file = os.path.join(log_path, 'sgx.log')

    # Create log directory if it doesn't exist and create log file
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        open(log_file, 'w').close()

    # Format for logging
    log_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"

    # Set log level
    log_level = getattr(logging, log_level.upper())

    # Create a logger and set its level
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a file handler and set its level and format
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Create a console handler and set its level and format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)