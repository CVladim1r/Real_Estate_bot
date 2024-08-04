import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ACTIVE_PROPERTY_FILE = os.path.join(os.path.dirname(__file__), 'active_property.json')

def save_active_property_id(user_id, property_id):
    """Сохранение ID активной квартиры в файл."""
    data = {'user_id': user_id, 'property_id': property_id}
    try:
        with open(ACTIVE_PROPERTY_FILE, 'w') as f:
            json.dump(data, f)
        logger.info(f"Active property ID saved: {property_id} for user: {user_id}")
    except IOError as e:
        logger.error(f"Error writing to file {ACTIVE_PROPERTY_FILE}: {e}")

def load_active_property_id():
    """Загрузка ID активной квартиры из файла."""
    logger.info(f"Attempting to load active property ID from {ACTIVE_PROPERTY_FILE}")
    
    if not os.path.isfile(ACTIVE_PROPERTY_FILE):
        logger.info("File does not exist.")
        return None, None

    try:
        with open(ACTIVE_PROPERTY_FILE, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded active property ID: {data.get('property_id')}")
        return data.get('user_id'), data.get('property_id')
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error reading file {ACTIVE_PROPERTY_FILE}: {e}")
        return None, None
