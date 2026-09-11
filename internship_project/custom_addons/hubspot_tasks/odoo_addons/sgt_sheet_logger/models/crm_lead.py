import os
import logging
import requests
from datetime import datetime
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

def load_env_vars():
    env_vars = {}
    for candidate in ["/var/lib/odoo/.env", "/etc/odoo/.env", "/.env", "./.env"]:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_vars[k.strip()] = v.strip().strip('"\'')
            except Exception:
                pass
            if env_vars:
                break
    return env_vars

class CrmLead(models.Model):
    # =========================================================================
    # TASK 15 NÂNG CAO: TỰ ĐỘNG KHẮC PHỤC SAI LỆCH DỮ LIỆU (AUTO-FIX)
    # =========================================================================
    @api.model
    def action_auto_fix_reconciliation(self):
        env_vars = load_env_vars()
        sheet_id = os.getenv("SPREADSHEET_ID") or env_vars.get("SPREADSHEET_ID")
        creds_file = "/var/lib/odoo/credentials.json"
        if not os.path.exists(creds_file):
            creds_file = "credentials.json"

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
            client = gspread.authorize(creds)
            doc = client.open_by_key(sheet_id) if sheet_id else client.open("HubSpot_Data_Sync")
            ws_recon = doc.worksheet("Reconciliation")
            ws_deals = doc.worksheet("Deals")

            rows = ws_recon.get_all_values()
            fixed_count = 0
            for idx, r in enumerate(rows[1:], start=2):
                entity_id_str = r[0]
                field_name = r[1]
                odoo_val = r[2]
                status = r[4]

                if "Deal Name" in field_name and "Lệch" in status:
                    clean_id = entity_id_str.replace("Deal #", "").strip()
                    cell = ws_deals.find(clean_id, in_column=1)
                    if cell:
                        ws_deals.update_cell(cell.row, 2, odoo_val)
                        ws_recon.update_cell(idx, 5, "ĐÃ TỰ ĐỘNG SỬA (AUTO-FIXED)")
                        fixed_count += 1
                elif "Chỉ có trên Odoo" in status:
                    clean_id = entity_id_str.replace("Deal #", "").strip()
                    ws_deals.append_row([clean_id, odoo_val, "0", "default", "New", "", datetime.now().strftime("%Y-%m-%d"), "", "", ""])
                    ws_recon.update_cell(idx, 5, "ĐÃ BỔ SUNG SANG SHEET")
                    fixed_count += 1

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Auto-Fix Thành Công",
                    "message": f"Đã tự động sửa và chuẩn hóa {fixed_count} bản ghi lệch dữ liệu giữa Odoo và Sheet!",
                    "type": "success",
                    "sticky": False
                }
            }
        except Exception as e:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Lỗi Auto-Fix", "message": str(e), "type": "danger", "sticky": True}
            }

    _inherit = "crm.lead"

    # =========================================================================
    # 1. TASK 15: ĐỐI SOÁT ODOO <-> GOOGLE SHEET (NỘI TẠI ODOO)
    # =========================================================================
    @api.model
    def action_run_reconciliation_now(self):
        env_vars = load_env_vars()
        sheet_id = os.getenv("SPREADSHEET_ID") or env_vars.get("SPREADSHEET_ID")
        creds_file = "/var/lib/odoo/credentials.json"
        if not os.path.exists(creds_file):
            creds_file = "credentials.json"

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
            client = gspread.authorize(creds)
            doc = client.open_by_key(sheet_id) if sheet_id else client.open("HubSpot_Data_Sync")

            # 1. Đọc dữ liệu Odoo
            odoo_leads = self.search_read(
                [("type", "=", "opportunity")],
                ["id", "name", "phone", "email_from", "expected_revenue"]
            )
            odoo_map = {str(d["id"]): d for d in odoo_leads}

            # 2. Đọc dữ liệu Sheet
            try:
                ws_deals = doc.worksheet("Deals")
                sheet_rows = ws_deals.get_all_values()
            except Exception:
                ws_deals = doc.worksheet("Queue")
                sheet_rows = ws_deals.get_all_values()

            sheet_map = {}
            if len(sheet_rows) > 1:
                headers = [h.strip() for h in sheet_rows[0]]
                id_idx = -1
                for cand in ["Deal ID", "Odoo Deal ID", "ID"]:
                    if cand in headers:
                        id_idx = headers.index(cand)
                        break
                if id_idx != -1:
                    for r in sheet_rows[1:]:
                        if len(r) > id_idx and r[id_idx].strip():
                            sheet_map[str(r[id_idx]).strip()] = r

            # 3. So sánh dữ liệu
            discrepancies = []
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for o_id, o_data in odoo_map.items():
                if o_id not in sheet_map:
                    discrepancies.append([f"Deal #{o_id}", "Existence", o_data.get("name"), "Chưa có trên Sheet", "Chỉ có trên Odoo", now_str])
                else:
                    s_row = sheet_map[o_id]
                    s_name = s_row[1] if len(s_row) > 1 else ""
                    if o_data.get("name") and s_name and o_data.get("name").strip() != s_name.strip():
                        discrepancies.append([f"Deal #{o_id}", "Deal Name", o_data.get("name"), s_name, "Lệch thông tin", now_str])

            for s_id, s_row in sheet_map.items():
                if s_id not in odoo_map and s_id.isdigit():
                    s_name = s_row[1] if len(s_row) > 1 else ""
                    discrepancies.append([f"Deal #{s_id}", "Existence", "Không tìm thấy trong Odoo", s_name, "Chỉ có trên Sheet", now_str])

            try:
                ws_recon = doc.worksheet("Reconciliation")
            except gspread.WorksheetNotFound:
                ws_recon = doc.add_worksheet(title="Reconciliation", rows=100, cols=10)

            recon_headers = ["Đối tượng / ID", "Trường đối soát", "Giá trị Odoo", "Giá trị Sheet", "Trạng thái lệch", "Thời gian quét"]
            ws_recon.clear()
            ws_recon.append_row(recon_headers)

            if not discrepancies:
                ws_recon.append_row(["Tất cả", "Toàn bộ dữ liệu", "Khớp 100%", "Khớp 100%", "ĐỒNG BỘ HOÀN HẢO", now_str])
                msg = "Dữ liệu Odoo và Google Sheet khớp 100%!"
            else:
                for row in discrepancies:
                    ws_recon.append_row(row)
                msg = f"Đã phát hiện {len(discrepancies)} điểm lệch và ghi nhận vào tab Reconciliation!"

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Đối soát thành công", "message": msg, "type": "success", "sticky": False}
            }
        except Exception as e:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Lỗi đối soát", "message": str(e), "type": "danger", "sticky": True}
            }

    # =========================================================================
    # 2. TASK 16 & 18: ĐỒNG BỘ HUBSPOT 2 CHIỀU & CHỐNG LOOP (NỘI TẠI ODOO)
    # =========================================================================
    @api.model
    def action_run_hubspot_bidirectional_sync(self):
        env_vars = load_env_vars()
        hs_token = os.getenv("HUBSPOT_ACCESS_TOKEN") or env_vars.get("HUBSPOT_ACCESS_TOKEN")

        if not hs_token:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Thiếu cấu hình", "message": "Chưa tìm thấy HUBSPOT_ACCESS_TOKEN trong file .env!", "type": "danger", "sticky": True}
            }

        headers = {"Authorization": f"Bearer {hs_token}", "Content-Type": "application/json"}
        created_cnt, updated_cnt = 0, 0

        try:
            # 1. Chiều HubSpot -> Odoo
            url_hs = "https://api.hubapi.com/crm/v3/objects/contacts"
            res = requests.get(url_hs, headers=headers, params={"limit": 25, "properties": "firstname,lastname,email,phone"}, timeout=15)
            
            if res.status_code == 200:
                for c in res.json().get("results", []):
                    hs_id = str(c["id"])
                    p = c.get("properties", {})
                    email = (p.get("email") or "").strip()
                    phone = (p.get("phone") or "").strip()
                    name = f"{p.get('firstname') or ''} {p.get('lastname') or ''}".strip() or email or f"HubSpot Contact {hs_id}"

                    domain = ["|", ("x_hubspot_contact_id", "=", hs_id), ("email", "=", email)] if email else [("x_hubspot_contact_id", "=", hs_id)]
                    partner = self.env["res.partner"].search(domain, limit=1)

                    if partner:
                        if partner.x_hubspot_contact_id == hs_id and partner.name == name:
                            continue
                        partner.write({"name": name, "x_hubspot_contact_id": hs_id})
                        updated_cnt += 1
                    else:
                        self.env["res.partner"].create({
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "x_hubspot_contact_id": hs_id
                        })
                        created_cnt += 1

            # 2. Chiều Odoo -> HubSpot
            local_contacts = self.env["res.partner"].search([
                ("x_hubspot_contact_id", "=", False),
                ("email", "!=", False)
            ], limit=10)

            for lp in local_contacts:
                parts = (lp.name or "").split(" ", 1)
                fname = parts[0]
                lname = parts[1] if len(parts) > 1 else ""

                payload = {
                    "properties": {
                        "email": lp.email,
                        "firstname": fname,
                        "lastname": lname,
                        "phone": lp.phone or ""
                    }
                }
                h_res = requests.post("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, json=payload, timeout=10)
                if h_res.status_code in [200, 201]:
                    new_id = h_res.json().get("id")
                    lp.write({"x_hubspot_contact_id": str(new_id)})
                    created_cnt += 1
                elif h_res.status_code == 409:
                    err_msg = h_res.json().get("message", "")
                    if "Existing ID:" in err_msg:
                        existing_id = err_msg.split("Existing ID:")[1].strip().split(" ")[0]
                        lp.write({"x_hubspot_contact_id": str(existing_id)})

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Đồng bộ thành công",
                    "message": f"Chu kỳ đồng bộ 2 chiều hoàn tất! Đã cập nhật: {updated_cnt} | Tạo mới: {created_cnt} Contact.",
                    "type": "success",
                    "sticky": False
                }
            }
        except Exception as e:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Lỗi đồng bộ HubSpot", "message": str(e), "type": "danger", "sticky": True}
            }

    # =========================================================================
    # 3. TASK 14: IMPORT TỪ GOOGLE SHEET QUEUE
    # =========================================================================
    @api.model
    def action_sync_from_google_sheet_queue(self):
        env_vars = load_env_vars()
        sheet_id = os.getenv("SPREADSHEET_ID") or env_vars.get("SPREADSHEET_ID")
        creds_file = "/var/lib/odoo/credentials.json"
        if not os.path.exists(creds_file):
            creds_file = "credentials.json"

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
            client = gspread.authorize(creds)
            doc = client.open_by_key(sheet_id) if sheet_id else client.open("HubSpot_Data_Sync")
            ws = doc.worksheet("Queue")

            rows = ws.get_all_values()
            if len(rows) <= 1:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {"title": "Thông báo", "message": "Tab Queue trên Sheet hiện không có dòng nào!", "type": "warning"}
                }

            headers = rows[0]
            col_map = {h: idx + 1 for idx, h in enumerate(headers)}
            status_col = col_map.get("Status", 1)
            odoo_id_col = col_map.get("Odoo Deal ID")
            updated_col = col_map.get("Updated At")

            count = 0
            for idx, row in enumerate(rows[1:], start=2):
                st = str(row[status_col - 1]).strip().upper()
                if st != "NEW":
                    continue

                deal_name = row[col_map["Deal Name"] - 1] if "Deal Name" in col_map else f"Deal Queue #{idx}"
                contact_name = row[col_map["Contact Name"] - 1] if "Contact Name" in col_map else ""
                email = row[col_map["Email"] - 1] if "Email" in col_map else ""
                phone = row[col_map["Phone"] - 1] if "Phone" in col_map else ""

                new_lead = self.create({
                    "name": deal_name,
                    "contact_name": contact_name,
                    "email_from": email,
                    "phone": phone,
                })

                ws.update_cell(idx, status_col, "DONE")
                if odoo_id_col:
                    ws.update_cell(idx, odoo_id_col, str(new_lead.id))
                if updated_col:
                    ws.update_cell(idx, updated_col, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                count += 1

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Thành công",
                    "message": f"Đã đồng bộ thành công {count} Deal từ Google Sheet Queue vào Odoo CRM!",
                    "type": "success",
                    "sticky": False,
                }
            }
        except Exception as e:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Lỗi đồng bộ Sheet", "message": str(e), "type": "danger", "sticky": True}
            }
