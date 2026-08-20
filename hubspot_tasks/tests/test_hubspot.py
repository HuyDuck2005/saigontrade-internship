import os
import requests
from dotenv import load_dotenv

# Tải biến môi trường từ .env
load_dotenv()

TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Gọi thử API lấy danh sách Contact
url = "https://api.hubapi.com/crm/v3/objects/contacts?limit=5"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("✅ Kết nối HubSpot API thành công!")
    print(f"Tổng số contacts lấy được: {len(data.get('results', []))}")
    for contact in data.get('results', []):
        props = contact.get('properties', {})
        print(f"- {props.get('firstname', '')} {props.get('lastname', '')} ({props.get('email', 'No email')})")
else:
    print(f"❌ Kết nối thất bại (Mã lỗi {response.status_code}):")
    print(response.text)
