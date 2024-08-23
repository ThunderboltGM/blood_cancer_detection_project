import sqlite3

conn = sqlite3.connect('userData.db')
fetchQuerry = """
select * from userQuerry
"""
cur = conn.cursor()
cur.execute(fetchQuerry)
output = cur.fetchall()
i = 1
for row in output:
    print(i,' ',row)
    i += 1
cur.close()
conn.close()