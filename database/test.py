import mysql.connector
from queries import get_connection

connection = get_connection()
cursor = connection.cursor()
cursor.execute("SELECT * FROM your_table WHERE id = 46")

result = cursor.fetchall()

if result:
    for row in result:
        print(row)

cursor.close()
cursor = connection.cursor()
cursor.execute("SELECT * FROM another_table WHERE some_condition")

another_result = cursor.fetchall()
if another_result:
    for row in another_result:
        print(row)

cursor.close()
connection.close()
