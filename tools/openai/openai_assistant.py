import json
import os
import sqlite3
from datetime import datetime
from openai import OpenAI

OPENAI_CONFIG = {
    'API_KEY': os.getenv("OPENAI_API_KEY"),
    'BASE_URL': "https://api.openai.com/v1",
    'MODEL': "gpt-4o-mini",
    # 'MODEL': "gpt-4o-mini-2024-07-18",
    
    'COUNT_LIMIT': 100,
    'ASSISTANT_ID': 'asst_YpC99r5sp9We0UpEmZhngiHx'
    # 'SYSTEM_PROMPT': SYSTEM_PROMPT["1"]
}

class AssistantV2:
    def __init__(self, client, config):
        self.client = client
        self.assistant_id = config['ASSISTANT_ID']
        self.database_path = 'conversation_history_v2.db'
        self._initialize_database()
        
        # Tạo thread mới
        self.thread = None

    def _initialize_database(self):
        """Tạo cơ sở dữ liệu và bảng nếu chưa tồn tại."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_to_database(self, user_message, assistant_response):
        """Lưu lịch sử hội thoại vào cơ sở dữ liệu."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_history (user_message, assistant_response)
            VALUES (?, ?)
        ''', (user_message, assistant_response))
        conn.commit()
        conn.close()

    def fetch_history(self, limit=100):
        """Lấy lịch sử hội thoại từ cơ sở dữ liệu."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message, assistant_response FROM conversation_history
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"message": row[0], "response": row[1]} for row in rows[::-1]]  # Đảo ngược thứ tự

    def delete_all_history(self):
        """Xóa toàn bộ lịch sử hội thoại từ cơ sở dữ liệu."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversation_history')
        conn.commit()
        conn.close()
        print("Đã xóa toàn bộ lịch sử hội thoại.")

    def generate_response(self, user_message):
        """Tạo phản hồi dựa trên tin nhắn người dùng."""
        try:
            # conversation_history = self.fetch_history()
            # for conv in conversation_history:
            #     # Gửi tin nhắn vào thread
            #     self.client.beta.threads.messages.create(
            #         thread_id=self.thread.id,
            #         role="user",
            #         content=conv['message']
            #     )

            #     # Gửi tin nhắn vào thread
            #     self.client.beta.threads.messages.create(
            #         thread_id=self.thread.id,
            #         role="assistant",
            #         content=conv['response']
            #     )

            # Gửi tin nhắn vào thread
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=user_message
            )

            # Thực thi thread và chờ kết quả
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id
            )

            if run.status == 'completed':
                # Lấy danh sách tin nhắn từ thread
                messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
                
                assistant_message_raw = messages.data[0].content[0].text.value
                # Xử lý nội dung trả về
                cleaned_string = assistant_message_raw.strip("```json").strip("```").strip()
                assistant_message = json.loads(cleaned_string)

                # Lưu lịch sử hội thoại
                self.save_to_database(user_message, json.dumps(assistant_message, ensure_ascii=False))

                return assistant_message
            else:
                print(f"Run status: {run.status}")
                return None
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None

    def start_chat(self):
        self.thread = self.client.beta.threads.create()
        """Bắt đầu vòng lặp hội thoại."""
        while True:
            user_message = input("User: ")
            if user_message.lower() == "exit":
                break
            start_time = datetime.now()
            response = self.generate_response(user_message)
            end_time = datetime.now()
            print(f"Time elapsed: {end_time - start_time}")
            print(f"Assistant: {response}")

if __name__ == "__main__":
    """
        Menu với các chức năng:
        1. Bắt đầu chat với AssistantV2.
        2. Xem lịch sử hội thoại.
        3. Xóa toàn bộ lịch sử hội thoại.
    """
    

    openai_client = OpenAI(api_key=OPENAI_CONFIG['API_KEY'], base_url=OPENAI_CONFIG['BASE_URL'])

    assistant = AssistantV2(client=openai_client, config=OPENAI_CONFIG)

    print("Chào mừng đến với AssistantV2!")
    print("Chọn chức năng:")
    print("1. Bắt đầu chat với AssistantV2.")
    print("2. Xem lịch sử hội thoại.")
    print("3. Xóa toàn bộ lịch sử hội thoại.")
    print("0. Thoát.")

    choice = input("Chọn chức năng (1/2/3/0): ")

    if choice == "1":
        assistant.start_chat()
    elif choice == "2":
        history = assistant.fetch_history(100)
        for i, conv in enumerate(history):
            print(f"Conversation {i + 1}:")
            print(f"User: {conv['message']}")
            print(f"Assistant: {conv['response']}")
            print()
    elif choice == "3":
        assistant.delete_all_history()
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Chức năng không hợp lệ.")
