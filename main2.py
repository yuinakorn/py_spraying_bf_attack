import requests
from bs4 import BeautifulSoup

# 1. กำหนด URL
base_url = "https://smartoffice.chiangmaihealth.go.th"
login_url = f"{base_url}/login"

# 2. เริ่ม session เพื่อเก็บ cookies
session = requests.Session()

# 3. โหลดหน้า login เพื่อนำ CSRF Token
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')

# 4. ดึง CSRF Token จาก input hidden
csrf_token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
print(f"CSRF Token ที่ได้: {csrf_token}")

# 5. สร้าง mockup login_data 2 อัน
mockup_data = [
    {
        'fname': 'นคร',
        'lname': 'มงคลโชติญาดา',
        'password': 'Yuijbii'
    },
    {
        'fname': 'สมชาย',
        'lname': 'ศรีสุข',
        'password': '123456'
    }
]

# 6. วนลูปทดสอบ mockup data
for i, data in enumerate(mockup_data, 1):
    print(f"\n🔍 ทดสอบครั้งที่ {i}: {data['fname']} {data['lname']} / {data['password']}")
    
    # เตรียมข้อมูลสำหรับ POST
    login_data = {
        '__RequestVerificationToken': csrf_token,
        'fname': data['fname'],
        'lname': data['lname'],
        'password': data['password']
    }
    
    # ส่ง POST ไปยังฟอร์ม login
    post_response = session.post(login_url, data=login_data)
    
    # ตรวจสอบผลลัพธ์
    if post_response.text.strip().lower() == "true":
        print("✅ Login สำเร็จ (ระบบตอบ true)")
    else:
        print("❌ Login ล้มเหลว (ระบบตอบ false)")
    
    print("-" * 30)

print("\n🎯 การทดสอบเสร็จสิ้น!")