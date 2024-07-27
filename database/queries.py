import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def insert_property(address, type):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "INSERT INTO properties (address, type) VALUES (%s, %s)"
        cursor.execute(query, (address, type))
        connection.commit()
        print("Property inserted successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_owner(property_id, fio, birth_date, share):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "INSERT INTO owners (property_id, fio, birth_date, share) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (property_id, fio, birth_date, share))
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
            query = "SELECT owner_id FROM owners WHERE property_id = %s"
            cursor.execute(query, (property_id,))
            owner_ids = cursor.fetchall()

            for oid in owner_ids:
                query = "INSERT INTO comments (owner_id, property_id, comment, is_general) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (oid[0], property_id, comment, is_general))
        else:
            query = "INSERT INTO comments (owner_id, property_id, comment, is_general) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (owner_id, property_id, comment, is_general))

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
        return properties
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
        return properties
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
        return comments
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
