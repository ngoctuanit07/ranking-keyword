import smtplib
from email.mime.text import MIMEText
from googlesearch import search

# Danh sách các từ khóa bạn muốn tìm kiếm
keywords = ["Áo thun SOLEIL ROOM", "Tạp hóa hà anh"]

# Số lượng kết quả tối đa bạn muốn lấy cho mỗi từ khóa
num_results = 10

# Khai báo thông tin về email
sender_email = "seowebsite0711@gmail.com"
receiver_email = "tuannguyen0719@gmail.com"

# Lặp qua từng từ khóa và tạo nội dung email
email_content = ""
for keyword in keywords:
    email_content += f"Kết quả cho từ khóa: {keyword}\n"
    for rank, result in enumerate(search(keyword, num_results=num_results), start=1):
        email_content += f"Thứ hạng {rank}: {result}\n"
    email_content += "\n"

# Tạo và gửi email
msg = MIMEText(email_content)
msg["Subject"] = "Kết quả tìm kiếm từ khóa"
msg["From"] = sender_email
msg["To"] = receiver_email

try:
    server = smtplib.SMTP("mail.smtp2go.com", 587)
    server.starttls()
    server.login("remine", "OXVkeGpoNXYxNXUw")
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("Email đã được gửi thành công.")
except Exception as e:
    print("Lỗi khi gửi email:", e)
