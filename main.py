import sqlite3

# Kết nối hoặc tạo mới file SQLite database
conn = sqlite3.connect('main.db')

# Tạo con trỏ để thực thi SQL
cursor = conn.cursor()

# Tạo bảng
cursor.execute('''
        CREATE TABLE conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT NOT NULL,
        assistant_response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

print("Bảng 'conversation_history' đã được tạo thành công.")

# Đóng kết nối
conn.commit()
conn.close()
