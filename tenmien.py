import requests
from bs4 import BeautifulSoup
from googlesearch import search
import time
import datetime
import matplotlib.pyplot as plt
from flask import Flask, render_template
import mysql.connector

# User-Agent giả mạo để giúp tránh chặn
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
}

# Kết nối đến cơ sở dữ liệu MySQL
conn = mysql.connector.connect(
    host="your_mysql_host",
    user="your_mysql_user",
    password="your_mysql_password",
    database="your_mysql_database"
)
cursor = conn.cursor()

# Tạo ứng dụng Flask
app = Flask(__name__)

def create_database():
    # Tạo bảng để lưu trữ dữ liệu về thứ hạng từ khóa
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keyword_rankings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        keyword VARCHAR(255),
        domain VARCHAR(255),
        position INT,
        date DATE
    )
    ''')

    # Lưu thay đổi
    conn.commit()

def update_database(domain, keywords_to_check, max_results=10):
    # Trong vòng lặp khi kiểm tra từ khóa
    for keyword in keywords_to_check:
        keyword_found = False

        # Lặp qua các kết quả tìm kiếm
        for i, result in enumerate(search(f"{domain} {keyword}", num=max_results, stop=max_results, pause=2)):
            try:
                response = requests.get(result, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Kiểm tra xem từ khóa có trong nội dung trang web hay không
                if keyword in text:
                    position = i+1
                    keyword_found = True
                    break
            except Exception as e:
                print(f"Không thể truy cập {result}: {e}")

        if keyword_found:
            # Lưu thứ hạng từ khóa và ngày tương ứng vào cơ sở dữ liệu
            date = datetime.date.today()
            cursor.execute("INSERT INTO keyword_rankings (keyword, domain, position, date) VALUES (%s, %s, %s, %s)", (keyword, domain, position, date))
            conn.commit()
        else:
            # Nếu không tìm thấy, lưu 'Không tìm thấy'
            date = datetime.date.today()
            cursor.execute("INSERT INTO keyword_rankings (keyword, domain, position, date) VALUES (%s, %s, %s, %s)", (keyword, domain, "Không tìm thấy", date))
            conn.commit()

def plot_keyword_rankings(keyword):
    # Truy vấn dữ liệu từ cơ sở dữ liệu cho từ khóa cụ thể
    cursor.execute("SELECT date, position FROM keyword_rankings WHERE keyword=%s", (keyword,))
    data = cursor.fetchall()

    if not data:
        print(f"Không có dữ liệu cho từ khóa '{keyword}'")
        return

    # Tạo danh sách ngày và thứ hạng tương ứng
    dates = [row[0] for row in data]
    positions = [row[1] if row[1] != 'Không tìm thấy' else 0 for row in data]

    # Vẽ biểu đồ
    plt.plot(dates, positions)
    plt.xlabel('Ngày')
    plt.ylabel('Thứ hạng')
    plt.title(f'Biểu đồ thứ hạng từ khóa "{keyword}" theo ngày')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Hiển thị biểu đồ
    plt.show()

@app.route('/')
def index():
    # Đọc cặp tên miền và danh sách từ khóa từ tệp tin config.txt
    with open('config.txt', 'r') as file:
        lines = file.read().splitlines()
    pairs = [line.split(',') for line in lines]

    # Bước 1: Tạo cơ sở dữ liệu nếu chưa tồn tại
    create_database()

    # Bước 2: Duyệt qua từng cặp tên miền và danh sách từ khóa
    for pair in pairs:
        domain = pair[0]
        keywords_to_check = pair[1:]
        
        # Cập nhật và lưu dữ liệu vào cơ sở dữ liệu cho tên miền và danh sách từ khóa hiện tại
        update_database(domain, keywords_to_check)

        # Vẽ biểu đồ thứ hạng từ khóa cho từng từ khóa của tên miền hiện tại
        for keyword in keywords_to_check:
            plot_keyword_rankings(keyword)

if __name__ == "__main__":
    app.run(debug=True)
