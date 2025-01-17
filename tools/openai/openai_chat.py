from openai import OpenAI
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
import os
import pytz
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

load_dotenv()

SYSTEM_PROMPT = {
    "0": """
        You are a helpful AI assistant for IMWS website. 
        ONLY RESPONSE JSON FORMAT IS ALLOWED.
        Json format: {"response": "Your response here", "key": "key_value"} with key_value is the keywords important in the user's message which will help search, statistical,...
        
        Please help the user with their questions.
        
        """,
    "1": 
        """
        Bạn là trợ lý cho trang web IMWS (Intelligent Management Workflow System) thuộc công ty GKSoftware. IMWS là hệ thống quản lý công việc dành cho doanh nghiệp và cá nhân, bao gồm các module lớn sau:

            Quản lý dự án (id: 'project_manager'): Quản lý chào giá, hợp đồng, đơn mua, hoá đơn,… trong một công ty cụ thể.
            Các ứng dụng công khai (id: 'public_apps') trong một công ty cụ thể:
            Giấy tờ hành chính: Giấy nghỉ phép, giấy đi công tác, giấy nghỉ thai sản, giấy đi muộn, giấy xin nghỉ việc, v.v.
            Tạm ứng/Hoàn ứng/Thanh toán: Chức năng như tên gọi.
            Thông báo: Tạo thông báo trong công ty cho nhân viên.
            Quản lý công việc (id: 'work_manager'): Giao việc cho cấp dưới, báo cáo công việc với cấp trên. Có thể chia sẻ công việc ra ngoài phạm vi công ty để cá nhân bên ngoài tham gia làm việc và báo cáo.
            Hồ sơ lưu trữ (id: 'archive'): Lưu trữ file đám mây cho công ty.
            Chào giá (id: 'quotation_requests'): Người dùng công ty có thể đăng bài cần mua hàng hoá, bài này xuất hiện công khai để bất kỳ ai cũng có thể xem và trao đổi riêng với công ty đó.
            Tuyển dụng (id: 'job_posting'): Người dùng công ty đăng bài tuyển dụng, bài này công khai để cá nhân nộp CV ứng tuyển.
        Bạn sẽ nhận được tin nhắn từ người dùng và cần phản hồi dưới dạng JSON với các quy tắc sau:

            'module': ID của module tương ứng nếu liên quan đến một module cụ thể. Nếu không liên quan đến hệ thống hoặc chỉ là câu hỏi vu vơ, đặt giá trị là 'None.'
            'keywords': Các từ khoá quan trọng trong tin nhắn của người dùng, phục vụ mục đích tìm kiếm và thống kê sau này.
            'type':
                'assist': Dành cho các yêu cầu không cần tương tác với database, bao gồm câu hỏi thông tin hoặc hướng dẫn.
                'advance_assist': Chỉ sử dụng khi PHẢI thực hiện thao tác đọc/ghi dữ liệu vào database (ví dụ: tạo giấy tờ, giao việc, tìm kiếm dữ liệu trong hệ thống).
            'response': Câu trả lời trực tiếp nếu 'type' là 'assist.' Nếu type là "advance_assist" thì xác thực hỏi lại người dùng có chắc chắn muốn tạo với thông tin này hay không, nếu bấm nút xác nhận, hệ thống sẽ tự tạo tài liệu tương ứng.
            'action': Hành động cụ thể cần thực hiện nếu cần tương tác với database. Để trống nếu 'type' là 'assist.'
        Phản hồi của bạn phải ngắn gọn, chính xác, và tuân thủ đúng định dạng JSON. TUYỆT ĐỐI KHÔNG ĐƯỢC TRẢ LỜI BẰNG NGÔN NGỮ TỰ NHIÊN, KHÔNG THÊM COMMENT ```JSON``` VÀO PHẢN HỒI.
        Nếu người dùng yêu cầu 1 tài liệu, hãy hỏi người dùng đầy đủ các trường với type 'assist' , sau đó khi đã đầy đủ các thông tin cần thiết, hỏi lại người dùng một lần nữa về tất cả các trường xem có muốn chỉnh sửa gì không với type "advance_assist".
        Tạm thời chỉ thực hiện hành động tại tài liệu với đơn xin nghỉ phép trong public apps, còn lại hãy phản hồi là đang bảo trì, không thể thực hiện.
        Đơn xin nghỉ phép:
            - Các trường cần thiết: 'user_fullname', 'reason', 'description' (Không bắt buộc), 'start_date', 'end_date'.
            - Action: 'create_leave_application' (Tạo).
        """,
    "2": """
        Bạn là trợ lý cho trang web IMWS.
        """
    }

OPENAI_CONFIG = {
    'API_KEY': os.getenv("OPENAI_API_KEY"),
    'BASE_URL': "https://api.openai.com/v1",
    # 'MODEL': "gpt-4o-mini",
    # 'MODEL': "gpt-4o-mini-2024-07-18",
    'MODEL': "ft:gpt-4o-mini-2024-07-18:gk-software-vietnam::ApAFfGzA",
    
    
    'COUNT_LIMIT': 3,
    
    'SYSTEM_PROMPT': SYSTEM_PROMPT["2"]
}

class ChatBot:
    def __init__(self, config):
        self.client = OpenAI(api_key=config['API_KEY'], base_url=config['BASE_URL'])
        self.system_prompt = config['SYSTEM_PROMPT']
        self.model = config['MODEL']
        self.count_limit = config['COUNT_LIMIT']
        self.database_path = 'conversation_history.db'
        self._initialize_database()

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

    def fetch_history(self, limit=None):
        """Lấy lịch sử hội thoại từ cơ sở dữ liệu."""
        if limit is None:
            limit = self.count_limit
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message, assistant_response FROM conversation_history
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"message": row[0], "response": row[1]} for row in rows[::-1]]  # Đảo ngược thứ tự

    def generate_response(self, user_message):
        """Tạo phản hồi dựa trên tin nhắn người dùng và lịch sử hội thoại."""
        try:
            time_now = datetime.now(vietnam_tz).strftime("%Y-%m-%d %H:%M:%S")
            conversation_history = self.fetch_history()
            messages = [{"role": "system", "content": f"{time_now}: {self.system_prompt}"}]
            
            # Thêm lịch sử hội thoại vào messages
            for conv in conversation_history:
                messages.append({"role": "user", "content": conv['message']})
                messages.append({"role": "assistant", "content": conv['response']})
            
            # Thêm tin nhắn hiện tại
            messages.append({"role": "user", "content": user_message})
            
            # Gọi API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            assistant_response = response.choices[0].message.content.strip()
            self.save_to_database(user_message, assistant_response)
            return assistant_response
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None

    def delete_all_history(self):
        """Xóa tất cả lịch sử hội thoại từ cơ sở dữ liệu."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversation_history')
        conn.commit()
        conn.close()
        print("Đã xóa toàn bộ lịch sử hội thoại.")
        
    def get_fine_tuning_jobs(self):
        jobs = self.client.fine_tuning.jobs.list()
        return jobs
    
    def start_chat(self):
        """Bắt đầu vòng lặp hội thoại."""
        while True:
            user_message = input("User: ")
            if user_message.lower() == "exit":
                break
            start_time = datetime.now()
            response = self.generate_response(user_message)
            end_time = datetime.now()
            print(f"Time elapsed: {end_time - start_time}")
            print(f"Bot: {response}")


if __name__ == "__main__":
    """
        Tạo menu với các chức năng:
        1. Bắt đầu chat với chatbot.
        2. Xem lịch sử hội thoại.
        3. Xóa toàn bộ lịch sử hội thoại.
    """
    
    print("Chào mừng đến với Chatbot của IMWS!")
    print("Chọn chức năng:")
    print("1. Bắt đầu chat với chatbot.")
    print("2. Xem lịch sử hội thoại.")
    print("3. Xóa toàn bộ lịch sử hội thoại.")
    print("4. Xem danh sách công việc fine-tuning.")
    print("0. Thoát.")
    
    choice = input("Chọn chức năng (1/2/3): ")
    
    if choice == "1":
        chatbot = ChatBot(OPENAI_CONFIG)
        chatbot.start_chat()
    elif choice == "2":
        chatbot = ChatBot(OPENAI_CONFIG)
        history = chatbot.fetch_history(100)
        for i, conv in enumerate(history):
            print(f"Conversation {i+1}:")
            print(f"User: {conv['message']}")
            print(f"Assistant: {conv['response']}")
            print()
    elif choice == "3":
        chatbot = ChatBot(OPENAI_CONFIG)
        chatbot.delete_all_history()
    elif choice == "4":
        chatbot = ChatBot(OPENAI_CONFIG)
        jobs = chatbot.get_fine_tuning_jobs()
        for job in jobs:
            print(f"Job ID: {job.id}")
            print(f"Status: {job.status}")
            print(f"Model: {job.model}")
            print(f"Created at: {job.created_at}")
            print()
    elif choice == "0" or choice == "exit":
        print("Goodbye!")
    else:
        print("Chức năng không hợp lệ.")
        