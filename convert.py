import pandas as pd
import sqlite3

# Connect to the SQLite database file
conn = sqlite3.connect('websites/data/websites.db')

# Load data from a specific table in the database
df = pd.read_sql_query('SELECT * FROM source', conn)

# Delete the image column
del df['image']

# Close the connection to the database
conn.close()

# Output the data to an Excel file
df.to_excel('websites/data/websites.xlsx')

