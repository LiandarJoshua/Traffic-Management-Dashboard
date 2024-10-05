import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('traffic_analysis.db')
cursor = conn.cursor()

# Function to fetch and display the table contents
def check_table(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if len(rows) == 0:
        print(f"No data found in the {table_name} table.")
    else:
        print(f"Data in the {table_name} table:")
        for row in rows:
            print(row)

# List of table names to check
table_names = ['traffic_data', 'traffic_summary', 'traffic_incidents', 'video_processing_status']

# Check each table
for table_name in table_names:
    print(f"\n--- {table_name.upper()} ---")
    check_table(table_name)

# Close the database connection
conn.close()
