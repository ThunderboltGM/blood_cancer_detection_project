import sqlite3

conn = sqlite3.connect('userData.db')
tableCreation = """
create table userQuerry(name varchar(20),email varchar(70),querry varchar(300))
"""
cur = conn.cursor()
cur.execute(tableCreation)
print('table created successfully')
cur.close()
conn.close()