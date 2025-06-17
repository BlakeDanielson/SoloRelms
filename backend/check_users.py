#!/usr/bin/env python3
import os
import psycopg2

# Set database URL
os.environ['DATABASE_URL'] = "postgresql://solorealms-db_owner:npg_bHqOy0r1CzWT@ep-shiny-lake-a8afy1ox-pooler.eastus2.azure.neon.tech/solorealms-db?sslmode=require"

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

print("🔍 CHECKING USERS IN DATABASE...")
cursor.execute('SELECT id, email, first_name, last_name FROM users')
users = cursor.fetchall()

print(f'Users in database: {len(users)}')
for user in users:
    print(f'  ID: {user[0]}')
    print(f'  Email: {user[1]}')
    print(f'  Name: {user[2]} {user[3]}')
    print()

cursor.close()
conn.close() 