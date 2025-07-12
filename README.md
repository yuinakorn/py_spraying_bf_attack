# Python Brute Force Login Tool

เครื่องมือสำหรับทดสอบการเข้าสู่ระบบด้วยการ brute force

## การติดตั้ง

1. สร้าง virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# หรือ
venv\Scripts\activate     # Windows
```

2. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

## การใช้งาน

1. เตรียมไฟล์ข้อมูล:
   - `fname.txt` - รายชื่อ (บรรทัดละ 1 ชื่อ)
   - `lname.txt` - รายนามสกุล (บรรทัดละ 1 นามสกุล)
   - `password.txt` - รายรหัสผ่าน (บรรทัดละ 1 รหัสผ่าน)

2. รันโปรแกรม:
```bash
python main.py
```

## ฟีเจอร์

- ✅ อ่านข้อมูลจากไฟล์
- ✅ วนลูปทดสอบทุกชุดข้อมูล
- ✅ แสดงผลการทดสอบแบบ real-time
- ✅ สรุปผลการทดสอบ
- ✅ **การหน่วงเวลาแบบสุ่ม** (2-5 วินาที) เพื่อหลีกเลี่ยงการตรวจจับ
- ✅ **หยุดพักนาน** ทุก 10 ครั้ง (10 วินาที)
- ✅ **จำลอง User-Agent** แบบสุ่ม
- ✅ **บันทึกผลลัพธ์** ลงไฟล์
- ✅ จัดการ error และ exception

## โครงสร้างไฟล์

```
py_brute_force/
├── main.py                    # โปรแกรมหลัก
├── fname.txt                  # ไฟล์รายชื่อ
├── lname.txt                  # ไฟล์รายนามสกุล
├── password.txt               # ไฟล์รายรหัสผ่าน
├── requirements.txt           # Dependencies
├── brute_force_results.txt    # ผลลัพธ์การทดสอบ (สร้างอัตโนมัติ)
├── successful_logins.txt      # ข้อมูลที่ login สำเร็จ (สร้างอัตโนมัติ)
└── README.md                 # คู่มือการใช้งาน
```

## หมายเหตุ

⚠️ **คำเตือน**: โปรแกรมนี้ใช้สำหรับการทดสอบความปลอดภัยเท่านั้น กรุณาใช้อย่างรับผิดชอบและได้รับอนุญาตก่อนใช้งาน # py_spraying_bf_attack
