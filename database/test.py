import mysql.connector

# Create a connection
connection = mysql.connector.connect(
    host="your_host",
    user="your_user",
    password="your_password",
    database="your_database",
    ssl_ca="path_to_ca_certificate"
)

cursor = connection.cursor()

# Execute the first query
cursor.execute("SELECT * FROM your_table WHERE id = 46")

# Fetch all results
result = cursor.fetchall()

# Ensure all results are processed before moving to the next query
if result:
    for row in result:
        # Process each row
        print(row)

# Close the cursor
cursor.close()

# If needed, create a new cursor for the next query
cursor = connection.cursor()

# Execute another query
cursor.execute("SELECT * FROM another_table WHERE some_condition")

# Fetch and process results as needed
another_result = cursor.fetchall()
if another_result:
    for row in another_result:
        # Process each row
        print(row)

# Close the cursor and connection after use
cursor.close()
connection.close()
