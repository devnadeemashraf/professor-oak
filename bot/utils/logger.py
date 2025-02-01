import logging
from config.config import config

def setup_logger():
    logger = logging.getLogger(config.LOGGER_NAME)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(filename=config.LOGGER_FILE_NAME, encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger