import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from datetime import datetime, timedelta
import string
import random
import threading

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    

def token_cleanup():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        query = "DELETE FROM user_tokens WHERE expires_at < NOW()"
        cursor.execute(query)
        connection.commit()
        print("Expired tokens cleaned up.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    threading.Timer(86400, token_cleanup).start()

token_cleanup()

def generate_token():
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(8))
    return token

def add_user_token(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        token = generate_token()
        expires_at = datetime.now() + timedelta(days=30)
        
        query = "INSERT INTO user_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, token, expires_at))
        connection.commit()
        print("Token added successfully.")
    except Error as e:
        print(f"Error: {e}")
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

def insert_comment(owner_id, property_id, comment, is_general):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        if is_general:
            query = "UPDATE properties SET general_comment = %s WHERE id = %s"
            cursor.execute(query, (comment, property_id))
        else:
            query = "UPDATE owners SET comment = %s WHERE id = %s"
            cursor.execute(query, (comment, owner_id))

        connection.commit()
        print("Comment inserted successfully.")
    except Error as e:
        print(f"Error: {e}")
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

def get_property_by_number(property_number):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Fetch property information
        query = "SELECT * FROM properties WHERE id = %s"
        cursor.execute(query, (property_number,))
        property_info = cursor.fetchone()
        print(f"Property fetch query: {query} with params: {property_number}")
        print(f"Fetched property info: {property_info}")

        if property_info:
            # Fetch all remaining rows to ensure no unread results
            cursor.fetchall()

            # Fetch owners for the property
            query = "SELECT * FROM owners WHERE property_id = %s"
            cursor.execute(query, (property_info[0],))
            owners = cursor.fetchall()
            print(f"Fetched owners for property {property_info[0]}: {owners}")

            return {
                'id': property_info[0],  # Use correct index for 'id'
                'area': property_info[3],
                'type': property_info[4],
                'ownership_form': property_info[5],
                'cadastral_number': property_info[6],
                'ownership_doc': property_info[7],
                'general_comment': property_info[8],
                'owners': [
                    {'fio': owner[2], 'birth_date': owner[3], 'share': owner[4], 'comment': owner[5]}
                    for owner in owners
                ]
            }
        return None
    except Error as e:
        print(f"Error: {e}")
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
        query = "SELECT * FROM comments WHERE property_id = %s"
        cursor.execute(query, (property_id,))
        comments = cursor.fetchall()
        print(f"Fetched comments for property_id {property_id}: {comments}")
        return comments
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
