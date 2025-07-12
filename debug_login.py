import requests
from bs4 import BeautifulSoup
import json

def debug_login_page():
    """ตรวจสอบโครงสร้างของหน้า login และหา CSRF Token"""
    
    # ลอง URL หลายแบบ
    urls_to_try = [
        "https://smartoffice.chiangmaihealth.go.th/login",
        "https://smartoffice.chiangmaihealth.go.th/Login",
        "https://smartoffice.chiangmaihealth.go.th/Account/Login",
        "https://smartoffice.chiangmaihealth.go.th/account/login",
        "https://smartoffice.chiangmaihealth.go.th/",
        "https://smartoffice.chiangmaihealth.go.th"
    ]
    
    # เริ่ม session
    session = requests.Session()
    
    # ตั้งค่า headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    for url in urls_to_try:
        print(f"🔍 ทดสอบ URL: {url}")
        print("-" * 50)
        
        try:
            # โหลดหน้า
            print("📡 กำลังโหลดหน้า...")
            response = session.get(url, allow_redirects=True)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📏 Content Length: {len(response.text)} characters")
            print(f"📍 Final URL: {response.url}")
            
            # ตรวจสอบ response headers
            print("📋 Response Headers:")
            for key, value in response.headers.items():
                if key.lower() in ['content-type', 'location', 'set-cookie']:
                    print(f"   {key}: {value}")
            print("-" * 30)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ตรวจสอบ title
            title = soup.find('title')
            if title:
                print(f"📄 Title: {title.text.strip()}")
            else:
                print("❌ ไม่พบ title")
            
            # ตรวจสอบ input fields ทั้งหมด
            inputs = soup.find_all('input')
            print(f"🔍 พบ input fields จำนวน: {len(inputs)}")
            
            if inputs:
                for i, input_field in enumerate(inputs, 1):
                    input_type = input_field.get('type', 'text')
                    input_name = input_field.get('name', 'ไม่มีชื่อ')
                    input_id = input_field.get('id', 'ไม่มี ID')
                    input_value = input_field.get('value', 'ไม่มีค่า')
                    
                    print(f"   {i}. Type: {input_type}, Name: {input_name}, ID: {input_id}")
                    if input_value:
                        print(f"      Value: {input_value[:50]}{'...' if len(input_value) > 50 else ''}")
            
            # ตรวจสอบ form
            forms = soup.find_all('form')
            print(f"📝 พบ form จำนวน: {len(forms)}")
            
            if forms:
                for i, form in enumerate(forms, 1):
                    form_action = form.get('action', 'ไม่มี action')
                    form_method = form.get('method', 'GET')
                    print(f"   {i}. Action: {form_action}, Method: {form_method}")
            
            # ตรวจสอบ CSRF Token
            csrf_names = [
                '__RequestVerificationToken',
                'csrf_token',
                'csrf',
                '_token',
                'token',
                'antiforgery',
                '__RequestVerificationToken__'
            ]
            
            csrf_found = False
            for csrf_name in csrf_names:
                csrf_input = soup.find('input', {'name': csrf_name})
                if csrf_input:
                    print(f"✅ พบ CSRF Token: {csrf_name}")
                    print(f"   Value: {csrf_input.get('value', 'ไม่มีค่า')}")
                    csrf_found = True
                    break
            
            if not csrf_found:
                # ตรวจสอบ input ที่มีคำว่า token หรือ csrf
                token_inputs = soup.find_all('input', {'name': lambda x: x and ('token' in x.lower() or 'csrf' in x.lower())})
                if token_inputs:
                    print("🔍 พบ input ที่อาจเป็น CSRF Token:")
                    for token_input in token_inputs:
                        print(f"   Name: {token_input.get('name')}, Value: {token_input.get('value', 'ไม่มีค่า')}")
            
            # ตรวจสอบ meta tags
            meta_tags = soup.find_all('meta')
            print(f"🔍 พบ meta tags จำนวน: {len(meta_tags)}")
            
            # ตรวจสอบ script tags
            script_tags = soup.find_all('script')
            print(f"🔍 พบ script tags จำนวน: {len(script_tags)}")
            
            if script_tags:
                print("📜 Script tags ที่พบ:")
                for i, script in enumerate(script_tags[:5], 1):  # แสดงแค่ 5 อันแรก
                    src = script.get('src', 'ไม่มี src')
                    script_type = script.get('type', 'ไม่มี type')
                    print(f"   {i}. Type: {script_type}, Src: {src}")
                    if not src and script.string:
                        content = script.string.strip()[:100]
                        print(f"      Content: {content}...")
            
            # บันทึก HTML ลงไฟล์
            filename = f"debug_page_{url.replace('://', '_').replace('/', '_').replace('.', '_')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 บันทึก HTML ลงไฟล์ {filename} แล้ว")
            
            # ถ้าพบ input fields หรือ forms ให้หยุด
            if inputs or forms:
                print("✅ พบข้อมูลที่ต้องการแล้ว!")
                break
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
        
        print("=" * 80)
        print()

if __name__ == "__main__":
    debug_login_page() 