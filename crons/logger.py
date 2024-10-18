from logtail import LogtailHandler
import requests
import logging

# Initialize the logger (global)
logger = logging.getLogger('filing_scraper')
logger.setLevel(logging.DEBUG)

# Function to configure the logger with a dynamic log file path
def configure_logger(log_filename):

    # Create file handler using the provided log filename
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the file handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Attach both Logtail and file handler to the logger
    logtail_handler = LogtailHandler(source_token='CJ1xunGEMgN8618aoKDUVtXT')
    logtail_handler.setLevel(logging.DEBUG)
    logtail_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(logtail_handler)

# Function to log messages
def log(level, message):
    if level.lower() == 'debug': 
        logger.debug(message)
        # log_telebot("DEBUG\n\n" + message)
    elif level.lower() == 'info': 
        logger.info(message)
        # log_telebot("INFO\n\n" + message)
    elif level.lower() == 'warning': 
        logger.warning(message)
        # log_telebot("WARNING\n\n" + message)
    elif level.lower() == 'error': 
        logger.error(message)
        log_telebot("ERROR\n\n" + message)
    else: 
        logger.critical(message)
        log_telebot("CRITICAL\n\n" + message)

# Function to send log messages to Telegram
def log_telebot(message):
    chat_id = '-4506773539'
    bot_id = "7770656451:AAFxWbl8thravZhmk4OBCDkvDBb0yDrGwl4"
    for i in range(0, len(message), 4000):
        chunk = message[i:i + 4000]
        requests.post(f"https://api.telegram.org/bot{bot_id}/sendMessage", data={'chat_id': chat_id, 'text': chunk})
