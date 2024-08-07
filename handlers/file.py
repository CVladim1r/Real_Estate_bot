import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ACTIVE_PROPERTY_FILE = os.path.join(os.path.dirname(__file__), 'active_property.json')


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def log_message(message):
    logger.info(f"Message from {message.from_user.id}: {message.text}")

def log_callback_query(callback_query):
    logger.info(f"Callback query from {callback_query.from_user.id}: {callback_query.data}")
