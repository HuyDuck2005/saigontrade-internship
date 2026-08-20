import os
import logging
from datetime import datetime
import requests
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "HubSpot_Data_Sync")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

DEAL_HEADERS = [
    "Deal ID", "Deal Name", "Amount", "Pipeline", "Deal Stage",
    "Owner", "Create Date", "Close Date", "Last Modified", "Associated Contact"
]

def get_google_sheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

def fetch_all_hubspot_deals():
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    params = {
        "limit": 100,
        "properties": "dealname,amount,pipeline,dealstage,hubspot_owner_id,createdate,closedate,hs_lastmodifieddate",
        "associations": "contacts"
    }
    
    deals = []
    after = None
    
    while True:
        if after:
            params["after"] = after
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            logger.error(f"Lỗi gọi Deals API: {res.status_code} - {res.text}")
            break
            
        data = res.json()
        for item in data.get("results", []):
            props = item.get("properties", {})
            # Extract associated contacts
            associations = item.get("associations", {}).get("contacts", {}).get("results", [])
            contact_ids = ", ".join([str(c.get("id")) for c in associations])
            
            amount_val = 0.0
            try:
                if props.get("amount"):
                    amount_val = float(props.get("amount"))
            except ValueError:
                amount_val = 0.0

            deals.append({
                "Deal ID": str(item.get("id")),
                "Deal Name": props.get("dealname") or "",
                "Amount": amount_val,
                "Pipeline": props.get("pipeline") or "default",
                "Deal Stage": props.get("dealstage") or "",
                "Owner": props.get("hubspot_owner_id") or "",
                "Create Date": props.get("createdate") or "",
                "Close Date": props.get("closedate") or "",
                "Last Modified": props.get("hs_lastmodifieddate") or "",
                "Associated Contact": contact_ids
            })
            
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
            
    return deals

def generate_summary(sheet, deals):
    try:
        ws_sum = sheet.worksheet("Summary")
    except gspread.WorksheetNotFound:
        ws_sum = sheet.add_worksheet(title="Summary", rows=50, cols=10)

    ws_sum.clear()
    
    if not deals:
        ws_sum.update(values=[["Không có dữ liệu Deals để phân tích"]], range_name="A1")
        return

    df = pd.DataFrame(deals)
    
    total_deals = len(df)
    total_amount = df["Amount"].sum()
    
    won_count = df[df["Deal Stage"].str.lower().str.contains("won", na=False)].shape[0]
    lost_count = df[df["Deal Stage"].str.lower().str.contains("lost", na=False)].shape[0]
    conversion_rate = (won_count / total_deals * 100) if total_deals > 0 else 0.0

    # Summary table
    summary_data = [
        ["CHỈ SỐ TỔNG HỢP (PIPELINE SUMMARY)", ""],
        ["Tổng số Deals (Total Deals)", total_deals],
        ["Tổng giá trị (Total Amount $)", f"${total_amount:,.2f}"],
        ["Số Deal thành công (Closed Won)", won_count],
        ["Số Deal thất bại (Closed Lost)", lost_count],
        ["Tỷ lệ chốt đơn (Conversion Rate)", f"{conversion_rate:.2f}%"],
        ["Thời gian cập nhật", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["", ""],
        ["PHÂN BỔ DEALS THEO STAGE", "SỐ LƯỢNG"]
    ]

    stage_counts = df["Deal Stage"].value_counts().reset_index()
    stage_counts.columns = ["Stage", "Count"]
    for _, r in stage_counts.iterrows():
        summary_data.append([r["Stage"], int(r["Count"])])

    ws_sum.update(values=summary_data, range_name="A1")

def sync_deals():
    logger.info("Bắt đầu lấy Deals từ HubSpot...")
    deals = fetch_all_hubspot_deals()
    logger.info(f"Đã đọc {len(deals)} deals.")

    client = get_google_sheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID) if SPREADSHEET_ID else client.open(SPREADSHEET_NAME)
    
    try:
        ws = sheet.worksheet("Deals")
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Deals", rows=100, cols=15)

    if deals:
        df = pd.DataFrame(deals)
        ws.clear()
        ws.update(values=[DEAL_HEADERS] + df[DEAL_HEADERS].values.tolist(), range_name="A1")
    else:
        ws.clear()
        ws.update(values=[DEAL_HEADERS], range_name="A1")

    # Generate summary sheet
    generate_summary(sheet, deals)
    logger.info("✅ Đã đồng bộ xong Deals và tạo báo cáo tab 'Summary'!")

if __name__ == "__main__":
    sync_deals()
