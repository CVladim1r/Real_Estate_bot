import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import string
import random
import threading
import logging

from config import config_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    return mysql.connector.connect(
        host=config_data.DB_HOST,
        user=config_data.DB_USER,
        password=config_data.DB_PASSWORD,
        database=config_data.DB_NAME
    )
    
def execute_query(query, params=None, fetchone=False):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        connection.commit()
        return result
    except Error as e:
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

def save_active_property_id_db(user_id, property_id):
    query = """
    INSERT INTO active_properties (user_id, property_id)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE property_id = VALUES(property_id);
    """
    execute_query(query, (user_id, property_id))

def load_active_property_id_db(user_id):
    query = "SELECT property_id FROM active_properties WHERE user_id = %s;"
    result = execute_query(query, (user_id,), fetchone=True)
    if result:
        return user_id, result['property_id']
    return None, None

def update_user_state(user_id, last_house_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO user_state (user_id, last_house_id) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE last_house_id = %s
        """
        values = (user_id, last_house_id, last_house_id)

        cursor.execute(query, values)
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_last_house(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = "SELECT last_house_id FROM user_state WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result:
            last_house_id = result[0]
            return last_house_id
        else:
            return None
    except Error as e:
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def generate_token():
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(8))
    return token

def add_user_token(user_id, token):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO user_tokens (user_id, token)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE token = VALUES(token);
        """
        cursor.execute(query, (user_id, token))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

            
def get_user_token(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = "SELECT token FROM user_tokens WHERE user_id = %s AND expires_at > NOW()"
        cursor.execute(query, (user_id,))
        token_info = cursor.fetchone()

        if token_info:
            token = token_info[0]
            return token
        else:
            return None
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def check_user_token(user_id, token):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        query = "SELECT * FROM user_tokens WHERE user_id = %s AND token = %s AND expires_at > NOW()"
        cursor.execute(query, (user_id, token))
        token_info = cursor.fetchone()
        
        if token_info:
            print("Token is valid.")
            return True
        else:
            print("Token is invalid or expired.")
            return False
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_house(address):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "INSERT INTO houses (address) VALUES (%s)"
        cursor.execute(query, (address,))
        connection.commit()
        print("House inserted successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_property(house_id, number, area, type, ownership_form, cadastral_number, ownership_doc, general_comment):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
        INSERT INTO properties (house_id, number, area, type, ownership_form, cadastral_number, ownership_doc, general_comment) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (house_id, number, area, type, ownership_form, cadastral_number, ownership_doc, general_comment))
        connection.commit()
        print("Property inserted successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_owner(property_id, fio, birth_date, share, comment):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "INSERT INTO owners (property_id, fio, birth_date, share, comment) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (property_id, fio, birth_date, share, comment))
        connection.commit()
        print("Owner inserted successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_general_comment_by_property_id(property_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT general_comment FROM properties WHERE id = %s"
        cursor.execute(query, (property_id,))
        result = cursor.fetchone()
        
        if result:
            return result.get('general_comment', 'Отсутствует')
        else:
            return 'Отсутствует'
    except Error as e:
        logger.error(f"Error: {e}")
        return 'Отсутствует'
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
def insert_general_comment(property_id, new_comment):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT general_comment FROM properties WHERE id = %s", (property_id,))
        result = cursor.fetchone()
        
        existing_comment = result[0] if result else ""
        
        if existing_comment:
            updated_comment = existing_comment + ", " + new_comment
        else:
            updated_comment = new_comment
        
        query = """
        UPDATE properties
        SET general_comment = %s
        WHERE id = %s
        """
        cursor.execute(query, (updated_comment, property_id))
        connection.commit()

        logger.info("General comment updated successfully.")
    except Error as e:
        logger.error(f"Error in insert_general_comment: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def insert_comment(owner_id, property_id, new_comment, is_general):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        if is_general:
            insert_general_comment(property_id, new_comment)
        else:
            cursor.execute("SELECT comment FROM owners WHERE id = %s", (owner_id,))
            result = cursor.fetchone()
            
            existing_comment = result[0] if result else ""
            
            if existing_comment:
                updated_comment = existing_comment + ", " + new_comment
            else:
                updated_comment = new_comment
            
            query = "UPDATE owners SET comment = %s WHERE id = %s"
            cursor.execute(query, (updated_comment, owner_id))
            connection.commit()

            if cursor.rowcount == 0:
                logger.warning("No rows were affected by the update.")
            else:
                logger.info("Comment updated successfully.")
    except Error as e:
        logger.error(f"Error in insert_comment: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
def get_all_houses():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM houses"
        cursor.execute(query)
        houses = cursor.fetchall()
        print(f"Fetched houses: {houses}")
        return houses
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_properties_by_house_id(house_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM properties WHERE house_id = %s"
        cursor.execute(query, (house_id,))
        properties = cursor.fetchall()
        print(f"Fetched properties for house_id {house_id}: {properties}")
        return properties
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_property_id_by_number_and_house(property_number, house_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id 
        FROM properties 
        WHERE number = %s AND house_id = %s;
        """
        cursor.execute(query, (property_number, house_id))
        result = cursor.fetchone()
        
        return result['id'] if result else None
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_property_by_number(property_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT p.id, p.number, p.area, p.type, p.ownership_form, p.cadastral_number, 
               p.ownership_doc, p.general_comment, GROUP_CONCAT(
                   CONCAT(o.fio, '|', IFNULL(o.birth_date, 'неизвестно'), '|', o.share, '|', IFNULL(o.comment, 'Отсутсвует'))
                   SEPARATOR ';'
               ) AS owners
        FROM properties p
        LEFT JOIN owners o ON p.id = o.property_id
        WHERE p.id = %s
        GROUP BY p.id;
        """
        cursor.execute(query, (property_id,))
        result = cursor.fetchone()

        if result:
            owners = []
            if result['owners']:
                owner_entries = result['owners'].split(';')
                for entry in owner_entries:
                    fio, birth_date, share, comment = entry.split('|')
                    owners.append({
                        'fio': fio,
                        'birth_date': birth_date if birth_date == 'неизвестно' else datetime.strptime(birth_date, '%Y-%m-%d').date(),
                        'share': float(share),
                        'comment': comment
                    })
            result['owners'] = owners
            result['cadastral_number'] = result['cadastral_number'] if result['cadastral_number'] else "Не указано"
            result['ownership_doc'] = result['ownership_doc'] if result['ownership_doc'] else "Не указано"
            result['general_comment'] = result['general_comment'] if result['general_comment'] else "Отсутсвует"
            
            return result
        else:
            return None
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_property_by_id(property_id):
    logger.debug(f"Запрос информации о квартире с ID: {property_id}")

    try:    
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            SELECT p.id, p.number, p.area, p.type, p.ownership_form, p.cadastral_number, p.ownership_doc, p.general_comment
            FROM properties p
            WHERE p.id = :property_id
            """      
        result = cursor.execute(query, {'property_id': property_id}).fetchone()
        if result:
            property_info = dict(result)
            logger.debug(f"Информация о квартире: {property_info}")
            return property_info
        else:
            logger.debug(f"Квартира с ID: {property_id} не найдена")
            return None
    except Exception as e:
            logger.error(f"Ошибка при запросе информации о квартире с ID: {property_id}: {e}")
            return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_owners_by_property_id(property_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM owners WHERE property_id = %s"
        cursor.execute(query, (property_id,))
        owners = cursor.fetchall()
        print(f"Fetched owners for property_id {property_id}: {owners}")
        return owners
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_comments_by_owner_id(owner_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM comments WHERE owner_id = %s"
        cursor.execute(query, (owner_id,))
        comments = cursor.fetchall()
        print(f"Fetched comments for owner_id {owner_id}: {comments}")
        return comments
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_comments_by_property_id(property_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT comment_text FROM comments WHERE property_id = %s", (property_id,))
        results = cursor.fetchall()
        return [row[0] for row in results]
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_all_properties():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM properties LIMIT 10"
        cursor.execute(query)
        properties = cursor.fetchall()
        print(f"Fetched properties: {properties}")
        return properties
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_properties_by_type(property_type):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM properties WHERE type = %s"
        cursor.execute(query, (property_type,))
        properties = cursor.fetchall()
        print(f"Fetched properties of type {property_type}: {properties}")
        return properties
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_properties_by_user_id(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT property_id
        FROM active_properties
        WHERE user_id = %s;
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result:
            return result['property_id']
        else:
            return None
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def save_properties_by_user_id(user_id, property_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO active_properties (user_id, property_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE property_id = VALUES(property_id);
        """
        cursor.execute(query, (user_id, property_id))
        connection.commit()

        print(f"Property ID {property_id} saved for user ID {user_id}.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            

def save_active_owner_id_db(user_id, last_owner_id):
    query = """
    INSERT INTO user_last_owner (user_id, last_owner_id)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE last_owner_id = VALUES(last_owner_id);
    """
    logger.debug(f"Executing query to save owner ID: {query} with params {user_id}, {last_owner_id}")
    execute_query(query, (user_id, last_owner_id))

def load_active_owner_id_db(user_id):
    query = "SELECT last_owner_id FROM user_last_owner WHERE user_id = %s;"
    result = execute_query(query, (user_id,), fetchone=True)
    if result:
        return result['last_owner_id']
    return None
