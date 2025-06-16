import sqlite3

def get_all_users():
    conn = sqlite3.connect("my_bot_data/users.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users
