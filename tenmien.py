import requests
from bs4 import BeautifulSoup
from googlesearch import search
import time
import sqlite3
import datetime
import matplotlib.pyplot as plt
from flask import Flask, render_template

# User-Agent giả mạo để giúp tránh chặn
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
}

# Tạo ứng dụng Flask
app = Flask(__name__)

def create_database():
    # Tạo cơ sở dữ liệu SQLite
    conn = sqlite3.connect('keyword_rankings.db')
    cursor = conn.cursor()

    # Tạo bảng để lưu trữ dữ liệu về thứ hạng từ khóa
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keyword_rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        domain TEXT,
        position INTEGER,
        date DATE
    )
    ''')

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()

def update_database(domain, keywords_to_check, max_results=10):
    # Kết nối đến cơ sở dữ liệu SQLite
    conn = sqlite3.connect('keyword_rankings.db')
    cursor = conn.cursor()

    # Trong vòng lặp khi kiểm tra từ khóa
    for keyword in keywords_to_check:
        keyword_found = False

        # Lặp qua các kết quả tìm kiếm
        for i, result in enumerate(search(f"{domain} {keyword}", max_results)):
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
            cursor.execute("INSERT INTO keyword_rankings (keyword, domain, position, date) VALUES (?, ?, ?, ?)", (keyword, domain, position, date))
            conn.commit()
        else:
            # Nếu không tìm thấy, lưu 'Không tìm thấy'
            date = datetime.date.today()
            cursor.execute("INSERT INTO keyword_rankings (keyword, domain, position, date) VALUES (?, ?, ?, ?)", (keyword, domain, "Không tìm thấy", date))
            conn.commit()

    # Đóng kết nối
    conn.close()

def plot_keyword_rankings(keyword):
    # Kết nối đến cơ sở dữ liệu SQLite
    conn = sqlite3.connect('keyword_rankings.db')
    cursor = conn.cursor()

    # Truy vấn dữ liệu từ cơ sở dữ liệu cho từ khóa cụ thể
    cursor.execute("SELECT date, position FROM keyword_rankings WHERE keyword=?", (keyword,))
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

    # Đóng kết nối
    conn.close()

@app.route('/')
def index():
    domain = "taphoahaanh.net"  # Thay thế bằng tên miền bạn muốn theo dõi
    keywords_to_check = ["Áo thun SOLEIL ROOM", "Tạp hóa hà anh"]  # Thay thế bằng danh sách từ khóa của bạn

    # Bước 1: Tạo cơ sở dữ liệu nếu chưa tồn tại
    create_database()

    # Bước 2: Cập nhật và lưu dữ liệu vào cơ sở dữ liệu
    update_database(domain, keywords_to_check)

    # Bước 3: Vẽ biểu đồ thứ hạng từ khóa cho từng từ khóa
    for keyword in keywords_to_check:
        plot_keyword_rankings(keyword)

if __name__ == "__main__":
    app.run(debug=True)
