# SaigonTrade Learning Management System (LMS)
## Danh sách Bài Tập & Dự Án Toàn bộ

**Cập nhật:** 2026-08-21  
**Tổng số bài tập:** 72 bài  
**Phạm vi:** CRM Integration, Sales Automation, Odoo Customization, HubSpot API, Google Sheets Integration

---

## Mục Lục

1. [Giới thiệu](#giới-thiệu)
2. [Tổng quan Kiến trúc](#tổng-quan-kiến-trúc)
3. [Phân nhóm Bài tập](#phân-nhóm-bài-tập)
4. [Danh sách Chi tiết 72 Bài tập](#danh-sách-chi-tiết-72-bài-tập)
5. [Tiến độ Thực hiện](#tiến-độ-thực-hiện)
6. [Tiêu chí Đánh giá](#tiêu-chí-đánh-giá)
7. [Công nghệ & Stack](#công-nghệ--stack)
8. [Tài nguyên & Hỗ trợ](#tài-nguyên--hỗ-trợ)

---

## Giới thiệu

Hệ thống LMS này quản lý **72 bài tập/dự án** dành cho **SaigonTrade**, một nền tảng B2B kết nối các doanh nghiệp thương mại. Các bài tập bao gồm:

- **Tích hợp API & Webhook**: HubSpot, Odoo, Google Sheets, REST APIs
- **Tự động hóa Sales**: Lead routing, KPI tracking, Commission, Target management
- **CRM Analytics**: Dashboard, Reports, Customer segmentation
- **Workflow & Approval**: Deal approval, Price approval, Commission verification
- **Capstone Projects**: 2-4 người một nhóm, quy mô lớn

**Mục tiêu học tập:**
- Thực hành integration giữa các hệ thống (multi-system sync)
- Xây dựng addon Odoo production-ready
- Thiết kế API middleware
- Phân tích dữ liệu kinh doanh

---

## Tổng quan Kiến trúc

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SaigonTrade Ecosystem                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   HubSpot    │  │  Google      │  │  Website/   │              │
│  │   CRM API    │  │  Sheets API  │  │  App JSON   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                      │
│         └─────────────────┼─────────────────┘                      │
│                           │                                        │
│                   ┌───────▼────────┐                               │
│                   │  Middleware    │                               │
│                   │  (FastAPI/Flask│                               │
│                   │   + Webhook)   │                               │
│                   └───────┬────────┘                               │
│                           │                                        │
│         ┌─────────────────┼─────────────────┐                     │
│         │                 │                 │                     │
│    ┌────▼─────┐  ┌───────▼──────┐  ┌──────▼────┐                │
│    │  Odoo1   │  │   Odoo2      │  │   Audit   │                │
│    │  CRM     │  │   External   │  │   Logs    │                │
│    └────┬─────┘  └──────────────┘  └───────────┘                │
│         │                                                         │
│         └─────────────┬──────────────────────────────────────┐   │
│                       │                                      │   │
│              ┌────────▼────────┐                   ┌────────▼──┐ │
│              │  Monitoring &   │                   │  Reports  │ │
│              │  Dashboard      │                   │  Export   │ │
│              └─────────────────┘                   └───────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phân nhóm Bài tập

### 1. **Nhóm HubSpot & Google Sheets (5 bài)**
Bài 1-3: Đồng bộ Contact/Deal HubSpot ↔ Google Sheet  
Bài 4: Webhook HubSpot real-time  
Bài 15: Reconciliation dữ liệu  

**Độ khó:** Dễ - Trung bình  
**Kỹ năng:** API Integration, Python, Webhook  

---

### 2. **Nhóm Odoo API & Python (4 bài)**
Bài 5: Python tạo CRM Lead via Odoo JSON-RPC  
Bài 14: Google Sheet làm queue import CRM  
Bài 15: Data Reconciliation Odoo + Sheet  

**Độ khó:** Dễ  
**Kỹ năng:** Odoo API, Python, ORM  

---

### 3. **Nhóm Odoo Addon (20 bài)**
Bài 6-10: Sync Odoo1 ↔ Odoo2, Field Mapping  
Bài 18-19: Matchmaking giữa Contacts  
Bài 21-22: Dashboard Analytics  
Bài 24-47: Sales Management Addon (KPI, Commission, Tracking, Workflow)  

**Độ khó:** Dễ - Khá - Nâng cao  
**Kỹ năng:** Odoo Addon, XML, Python, ORM, OWL  

---

### 4. **Nhóm API Middleware (3 bài)**
Bài 8: API trung gian nhận khách hàng  
Bài 23: Capstone Mini Integration Platform  

**Độ khó:** Trung bình - Khó  
**Kỹ năng:** FastAPI/Flask, Database, Docker  

---

### 5. **Nhóm Integration & Sync (5 bài)**
Bài 16-17: HubSpot ↔ Odoo Contact/Deal  
Bài 18: Bidirectional Sync (2 chiều)  
Bài 44: Sync Monitoring Center  

**Độ khó:** Trung bình - Khá  
**Kỹ năng:** Multi-system Sync, Conflict Resolution  

---

### 6. **Nhóm Reports & Analytics (12 bài)**
Bài 20: CRM Sales Dashboard  
Bài 21: HR Attendance Dashboard  
Bài 29-30: Sales Pipeline Aging, Lost Deal Analysis  
Bài 31-34: Export PDF/Excel, Customer 360, Executive Dashboard  
Bài 41: Weekly Business Review Pack  
Bài 45: Sales Forecast Dashboard  

**Độ khó:** Trung bình - Khá  
**Kỹ năng:** OWL, QWeb PDF, Reporting, Data Viz  

---

### 7. **Nhóm Sales Automation & Tracking (18 bài)**
Bài 25-26: Sales KPI, Commission  
Bài 27-28: Lead Source Tracking, Customer Journey  
Bài 35-36: SLA Tracker, Deal Sync Monitoring  
Bài 49-61: Lead Scoring, Duplicate Detection, Lead Follow-up, Customer Care  

**Độ khó:** Dễ - Khá  
**Kỹ năng:** Odoo CRM, Automation Rules, Business Logic  

---

### 8. **Nhóm Capstone Projects (3 bài - Dự án lớn)**
Bài 23: Mini CRM Integration Platform  
Bài 48: SaigonTrade Business Control Center  
Bài 72: SaigonTrade Sales Operations Control Center  

**Độ khó:** Nâng cao - Rất khó  
**Quy mô:** 2-4 TTS/nhóm  
**Thời gian:** 4-6 tuần  

---

## Danh sách Chi tiết 72 Bài tập

### **BÀI 1: Đồng bộ HubSpot Contact về Google Sheet**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 1 |
| **Nhóm** | HubSpot → Google Sheet |
| **Mô tả** | Lấy danh sách Contact từ HubSpot API và đồng bộ sang Google Sheet để Sales/Marketing theo dõi. |
| **Công nghệ** | HubSpot API, Python, Google Sheets API |
| **Nguồn dữ liệu** | HubSpot Contact |
| **Đích dữ liệu** | Google Sheet |
| **Dữ liệu chính** | HubSpot Contact ID; First Name; Last Name; Email; Phone; Mobile Phone; Company; Job Title; Website; Country; Lifecycle Stage; Create Date; Last Modified Date |
| **Yêu cầu bắt buộc** | <ul><li>Có pagination</li><li>Không duplicate theo HubSpot ID</li><li>Contact tồn tại thì update</li><li>Contact mới thì append</li><li>Ghi last_sync timestamp</li><li>Xử lý thiếu email/phone</li><li>Log số đọc/tạo/cập nhật/lỗi</li></ul> |
| **Yêu cầu nâng cao** | Chỉ sync Contact thay đổi từ lần chạy gần nhất (incremental sync) |
| **Deliverables** | README; source code; file cấu hình mẫu; dữ liệu test; demo |
| **Độ khó** | ⭐ Dễ |
| **Đối tượng** | TTS mới |

**Hướng dẫn chi tiết:**
- Sử dụng HubSpot API v3 (Bearer token auth)
- Xử lý pagination với `limit=100, offset`
- Tên sheet: `Contacts_YYYY_MM_DD`
- Columns: theo fields trên
- Cron job: chạy mỗi 6 giờ
- Error log: ghi vào sheet `Sync_Errors`

---

### **BÀI 2: Import Contact từ Google Sheet vào HubSpot**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 2 |
| **Nhóm** | Google Sheet → HubSpot |
| **Mô tả** | Đọc khách hàng do Sales nhập trên Google Sheet rồi create/update Contact trong HubSpot. |
| **Công nghệ** | Python, HubSpot API, Google Sheets API |
| **Nguồn dữ liệu** | Google Sheet |
| **Đích dữ liệu** | HubSpot Contact |
| **Dữ liệu chính** | firstname; lastname; email; phone; mobilephone; jobtitle; company; website; country; event; event_location; status |
| **Yêu cầu bắt buộc** | <ul><li>Chỉ xử lý status=NEW</li><li>Validate dữ liệu (required fields)</li><li>Tìm Contact theo email, nếu không có email thì theo phone</li><li>Create/update logic</li><li>Cập nhật SUCCESS/UPDATED/ERROR status</li><li>Ghi HubSpot ID về sheet</li></ul> |
| **Yêu cầu nâng cao** | Thêm cột error_message và cơ chế retry tự động |
| **Deliverables** | README; source; sheet mẫu; demo |
| **Độ khó** | ⭐ Dễ |
| **Đối tượng** | TTS mới |

---

### **BÀI 3: Đồng bộ HubSpot Deal sang Google Sheet**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 3 |
| **Nhóm** | HubSpot → Google Sheet |
| **Mô tả** | Tạo bảng Deal Pipeline bên ngoài HubSpot phục vụ báo cáo. |
| **Công nghệ** | HubSpot API, Python, Google Sheets API |
| **Nguồn dữ liệu** | HubSpot Deal |
| **Đích dữ liệu** | Google Sheet |
| **Dữ liệu chính** | Deal ID; Deal Name; Amount; Pipeline; Deal Stage; Owner; Create Date; Close Date; Last Modified; Associated Contact |
| **Yêu cầu bắt buộc** | <ul><li>Không duplicate Deal ID</li><li>Update khi Deal thay đổi</li><li>Tạo sheet Summary gồm:</li><li>- Total Deal</li><li>- Total Amount</li><li>- Deal theo Stage</li><li>- Won/Lost count</li><li>- Conversion Rate</li></ul> |
| **Yêu cầu nâng cao** | - |
| **Deliverables** | README; source; file Sheet mẫu; demo |
| **Độ khó** | ⭐ Dễ |
| **Đối tượng** | TTS mới |

---

### **BÀI 4: Webhook HubSpot → Python API → Google Sheet**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 4 |
| **Nhóm** | Webhook HubSpot |
| **Mô tả** | Nhận thay đổi Contact gần thời gian thực bằng webhook thay vì cron polling. |
| **Công nghệ** | Flask/FastAPI, HubSpot Webhook, Google Sheets API |
| **Nguồn dữ liệu** | HubSpot Webhook |
| **Đích dữ liệu** | Google Sheet |
| **Dữ liệu chính** | event id; object id; property changed; timestamp |
| **Yêu cầu bắt buộc** | <ul><li>POST /hubspot/webhook endpoint</li><li>GET /health health check</li><li>Validate webhook request (signature)</li><li>Gọi HubSpot API lấy dữ liệu mới</li><li>Update Sheet</li><li>Chống xử lý webhook trùng (idempotency)</li><li>Logging chi tiết</li><li>HTTP status code phù hợp</li><li>Lỗi Google Sheet không làm API crash</li></ul> |
| **Yêu cầu nâng cao** | Thêm queue (Celery/RQ) hoặc retry webhook lỗi |
| **Deliverables** | README; API source; Postman collection; demo webhook |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS có API cơ bản |

---

### **BÀI 5: Python tạo CRM Lead trong Odoo qua API**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 5 |
| **Nhóm** | Odoo API |
| **Mô tả** | Viết ứng dụng Python bên ngoài Odoo để tạo CRM Lead/Opportunity. |
| **Công nghệ** | Python, JSON-RPC/XML-RPC, Odoo CRM |
| **Nguồn dữ liệu** | Python App |
| **Đích dữ liệu** | Odoo crm.lead |
| **Dữ liệu chính** | name; contact_name; phone; email; event; event_location |
| **Yêu cầu bắt buộc** | <ul><li>Đăng nhập Odoo</li><li>Tạo crm.lead</li><li>Trả success và lead_id</li><li>Xử lý error: login sai, DB sai, field thiếu, timeout</li></ul> |
| **Yêu cầu nâng cao** | Tạo thêm endpoint REST wrapper bên ngoài Odoo |
| **Deliverables** | README; source; sample payload; demo |
| **Độ khó** | ⭐ Dễ |
| **Đối tượng** | TTS mới |

---

### **BÀI 6: Đồng bộ Contact Odoo1 → Odoo2**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 6 |
| **Nhóm** | Odoo1 → Odoo2 |
| **Mô tả** | Từ CRM Lead Odoo1 tạo/cập nhật Contact ở Odoo1 và Odoo2. |
| **Công nghệ** | Odoo Addon, Python, XML-RPC |
| **Nguồn dữ liệu** | Odoo1 CRM Lead |
| **Đích dữ liệu** | Odoo1 Contact + Odoo2 Contact |
| **Dữ liệu chính** | phone; mobile; name; email và custom fields liên quan |
| **Yêu cầu bắt buộc** | <ul><li>Tạo nút "Tạo Contact Odoo1 & Odoo2"</li><li>Tìm Contact theo phone</li><li>Create/update local Odoo1</li><li>Kết nối Odoo2 via XML-RPC</li><li>Create/update remote Odoo2</li><li>Cấu hình remote bằng model sgt.remote.odoo (không hard-code)</li></ul> |
| **Yêu cầu nâng cao** | Thêm retry logic và sync status tracking |
| **Deliverables** | Addon hoàn chỉnh; manifest; security; views; README; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 7: Mapping custom field Odoo1 → Odoo2**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 7 |
| **Nhóm** | Odoo Field Mapping |
| **Mô tả** | Mở rộng luồng sync Contact với mapping đầy đủ custom field. |
| **Công nghệ** | Odoo Addon, XML-RPC |
| **Nguồn dữ liệu** | Odoo1 crm.lead |
| **Đích dữ liệu** | Odoo2 res.partner |
| **Dữ liệu chính** | 20+ custom fields (x_firstname → x_custome_fields_firstname, v.v.) |
| **Yêu cầu bắt buộc** | <ul><li>Map đúng kiểu dữ liệu (text, selection, many2one, ...)</li><li>Phát hiện field thiếu</li><li>Không làm hỏng sync nếu field optional không có</li></ul> |
| **Yêu cầu nâng cao** | Tự tạo custom field remote nếu thiếu |
| **Deliverables** | Addon; mapping document; test cases; demo |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo khá |

---

### **BÀI 8: API Middleware - nhận khách hàng và tạo Odoo CRM Deal**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 8 |
| **Nhóm** | API Middleware |
| **Mô tả** | Xây dựng API dùng chung cho Website/App để tạo Contact và Deal trong Odoo. |
| **Công nghệ** | FastAPI/Flask, Odoo API |
| **Nguồn dữ liệu** | Website/App JSON |
| **Đích dữ liệu** | Odoo Contact + CRM Deal |
| **Dữ liệu chính** | deal_name; firstname; lastname; phone; email; source; event; note |
| **Yêu cầu bắt buộc** | <ul><li>POST /api/crm/deal endpoint</li><li>Validate API key</li><li>Validate input (required fields, email format)</li><li>Tìm Contact existing</li><li>Create/update Contact</li><li>Tạo Deal mới</li><li>Associate Contact với Deal</li><li>Return Deal ID</li></ul> |
| **Yêu cầu nâng cao** | Thêm idempotency key và audit log |
| **Deliverables** | Source API; OpenAPI/Postman; README; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS API/Odoo |

---

### **BÀI 9: Addon tạo Deal từ danh sách Contact**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 9 |
| **Nhóm** | Odoo Addon |
| **Mô tả** | Cho phép chọn nhiều Contact và tạo CRM Deal hàng loạt bằng wizard. |
| **Công nghệ** | Odoo Addon |
| **Nguồn dữ liệu** | res.partner selected records |
| **Đích dữ liệu** | crm.lead |
| **Dữ liệu chính** | Deal Name; Amount; Notes; Event; Event Location |
| **Yêu cầu bắt buộc** | <ul><li>Server action/wizard</li><li>Mỗi Contact tạo 1 Deal</li><li>Set partner_id, amount, event, source</li><li>Sau khi xong mở danh sách Deal vừa tạo</li></ul> |
| **Yêu cầu nâng cao** | Có validate trùng Deal theo event/contact |
| **Deliverables** | Addon; views; security; README; demo |
| **Độ khó** | ⭐ Dễ |
| **Đối tượng** | TTS Odoo mới |

---

### **BÀI 10: Tạo Deal đồng thời trên Odoo1 và Odoo2**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 10 |
| **Nhóm** | Odoo1 → Odoo2 |
| **Mô tả** | Tạo Deal local trước, sau đó tạo Deal tương ứng trên Odoo2. |
| **Công nghệ** | Odoo Addon, XML-RPC |
| **Nguồn dữ liệu** | Odoo1 Deal |
| **Đích dữ liệu** | Odoo2 Deal |
| **Dữ liệu chính** | Deal fields + x_deal_id |
| **Yêu cầu bắt buộc** | <ul><li>x_deal_id = NL{ODOO1_LEAD_ID}</li><li>Nếu Odoo2 lỗi không rollback Deal Odoo1</li><li>Lưu sync failed status và error message</li><li>Có nút Retry Sync</li></ul> |
| **Yêu cầu nâng cao** | Thêm sync queue và retry count |
| **Deliverables** | Addon; demo lỗi/retry; README |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo khá |

---

### **BÀI 11: Addon Social CRM Deal**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 11 |
| **Nhóm** | Social CRM |
| **Mô tả** | Lưu thông tin khách hàng Facebook/TikTok vào CRM. |
| **Công nghệ** | Odoo Addon, REST API |
| **Nguồn dữ liệu** | Facebook/TikTok App |
| **Đích dữ liệu** | Odoo crm.lead |
| **Dữ liệu chính** | x_social_platform; x_social_profile_name; x_social_profile_url; x_social_post_url; x_social_page_url; x_social_post_text |
| **Yêu cầu bắt buộc** | <ul><li>Tạo custom fields + views</li><li>POST /social_deal/create endpoint</li><li>Create CRM Deal</li><li>Lưu đầy đủ social info</li></ul> |
| **Yêu cầu nâng cao** | Thêm auth API key và CORS hợp lý |
| **Deliverables** | Addon; API docs; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo/API |

---

### **BÀI 12: Upload screenshot từ ứng dụng ngoài vào Odoo Deal (Attachment API)**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 12 |
| **Nhóm** | Attachment API |
| **Mô tả** | Nhận ảnh base64 và tạo ir.attachment gắn vào CRM Deal. |
| **Công nghệ** | Odoo Controller, Base64 |
| **Nguồn dữ liệu** | External App |
| **Đích dữ liệu** | Odoo ir.attachment |
| **Dữ liệu chính** | image_base64; filename; mimetype; lead_id |
| **Yêu cầu bắt buộc** | <ul><li>Validate base64</li><li>Kiểm tra size (max 10MB?)</li><li>Validate MIME type</li><li>Kiểm tra Deal tồn tại</li><li>Tạo attachment</li><li>Filename theo chuẩn (YYYY_MM_DD_HASH)</li></ul> |
| **Yêu cầu nâng cao** | Resize/compress ảnh trước khi lưu |
| **Deliverables** | Addon/controller; test payload; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo/API |

---

### **BÀI 13: Log Deal Odoo sang Google Sheet**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 13 |
| **Nhóm** | Odoo → Google Sheet |
| **Mô tả** | Khi tạo Deal bằng wizard, ghi log sang Google Sheet phục vụ monitoring. |
| **Công nghệ** | Odoo Addon, Google Sheets API |
| **Nguồn dữ liệu** | Odoo crm.lead |
| **Đích dữ liệu** | Google Sheet |
| **Dữ liệu chính** | Deal ID; Deal Name; Contact; Phone; Email; Amount; Salesperson; Event; Event Location; Created Date; Sync Odoo2 Status |
| **Yêu cầu bắt buộc** | <ul><li>Lỗi Google Sheet không làm transaction tạo Deal thất bại</li><li>Phải log lỗi riêng vào sheet Errors</li></ul> |
| **Yêu cầu nâng cao** | Queue async/retry Google Sheet |
| **Deliverables** | Addon; sheet mẫu; README; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 14: Google Sheet làm hàng đợi import CRM**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 14 |
| **Nhóm** | Google Sheet Queue |
| **Mô tả** | Dùng Google Sheet như queue để tạo Deal vào Odoo. |
| **Công nghệ** | Python, Google Sheets API, Odoo API |
| **Nguồn dữ liệu** | Google Sheet rows |
| **Đích dữ liệu** | Odoo crm.lead |
| **Dữ liệu chính** | status; deal_name; phone; email; event |
| **Yêu cầu bắt buộc** | <ul><li>Chỉ đọc NEW status</li><li>Chuyển NEW → PROCESSING → DONE hoặc ERROR</li><li>Không xử lý cùng dòng 2 lần (at-least-once semantics)</li></ul> |
| **Yêu cầu nâng cao** | Thêm lock/idempotency và retry_count |
| **Deliverables** | Source; sheet mẫu; logs; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Python/API |

---

### **BÀI 15: Data Reconciliation - Odoo và Google Sheet**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 15 |
| **Nhóm** | Data Reconciliation |
| **Mô tả** | Phát hiện dữ liệu lệch giữa Odoo và Google Sheet. |
| **Công nghệ** | Python, Odoo API, Google Sheets API |
| **Nguồn dữ liệu** | Odoo + Google Sheet |
| **Đích dữ liệu** | Reconciliation Result Sheet |
| **Dữ liệu chính** | deal_id; phone; email; amount; stage |
| **Yêu cầu bắt buộc** | <ul><li>Phát hiện:</li><li>- Chỉ có Odoo</li><li>- Chỉ có Sheet</li><li>- Value khác nhau</li><li>- Output: ID, Field, Odoo Value, Sheet Value, Status</li></ul> |
| **Yêu cầu nâng cao** | Tạo nút/command auto-fix một số field |
| **Deliverables** | Source; result sheet; README; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Python |

---

### **BÀI 16: Đồng bộ HubSpot Contact → Odoo Contact**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 16 |
| **Nhóm** | HubSpot → Odoo |
| **Mô tả** | Đưa Contact HubSpot về Odoo và chống duplicate. |
| **Công nghệ** | HubSpot API, Odoo API, Python |
| **Nguồn dữ liệu** | HubSpot Contact |
| **Đích dữ liệu** | Odoo res.partner |
| **Dữ liệu chính** | firstname; lastname; phone; mobilephone; email; jobtitle; website; country; HubSpot ID |
| **Yêu cầu bắt buộc** | <ul><li>Matching ưu tiên:</li><li>1. HubSpot ID</li><li>2. Email</li><li>3. Phone</li><li>Lưu x_hubspot_contact_id</li><li>Create/update không duplicate</li></ul> |
| **Yêu cầu nâng cao** | Incremental sync theo modified date |
| **Deliverables** | Source; mapping doc; test cases; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Integration |

---

### **BÀI 17: Đồng bộ Odoo CRM Deal → HubSpot Deal**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 17 |
| **Nhóm** | Odoo → HubSpot |
| **Mô tả** | Khi Odoo tạo Deal mới thì đồng bộ sang HubSpot. |
| **Công nghệ** | Odoo Addon, HubSpot API |
| **Nguồn dữ liệu** | Odoo crm.lead |
| **Đích dữ liệu** | HubSpot Deal |
| **Dữ liệu chính** | Deal Name; Amount; Stage; Owner; Contact; Event; Event Location |
| **Yêu cầu bắt buộc** | <ul><li>Thêm custom fields:</li><li>- x_hubspot_deal_id</li><li>- x_hubspot_sync_status</li><li>- x_hubspot_sync_date</li><li>- x_hubspot_sync_error</li><li>- Status pending/success/failed</li><li>- Nút Retry HubSpot Sync</li></ul> |
| **Yêu cầu nâng cao** | Thêm queue cron background |
| **Deliverables** | Addon; demo retry; README |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Integration khá |

---

### **BÀI 18: Hai chiều HubSpot ↔ Odoo (Bidirectional Sync)**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 18 |
| **Nhóm** | Bidirectional Sync |
| **Mô tả** | Thiết kế cơ chế đồng bộ hai chiều Contact giữa HubSpot và Odoo. |
| **Công nghệ** | HubSpot API, Odoo API, Middleware |
| **Nguồn dữ liệu** | HubSpot + Odoo |
| **Đích dữ liệu** | HubSpot + Odoo |
| **Dữ liệu chính** | Contact fields và timestamps |
| **Yêu cầu bắt buộc** | <ul><li>Phân tích chiến lược đồng bộ:</li><li>- Last Updated Wins</li><li>- HubSpot Master</li><li>- Odoo Master</li><li>- Field-level ownership</li><li>- Chống loop</li><li>- Lưu external IDs</li></ul> |
| **Yêu cầu nâng cao** | Thêm conflict table và màn hình xử lý conflict |
| **Deliverables** | Architecture doc; source POC; demo conflict |
| **Độ khó** | ⭐⭐⭐⭐ Khó |
| **Đối tượng** | TTS khá/nhóm |

---

### **BÀI 19: Addon Match Making giữa hai Contact**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 19 |
| **Nhóm** | Matchmaking |
| **Mô tả** | Tạo record kết nối 2 doanh nghiệp/contact phục vụ business matching. |
| **Công nghệ** | Odoo Addon |
| **Nguồn dữ liệu** | res.partner |
| **Đích dữ liệu** | mm.lead |
| **Dữ liệu chính** | name; partner_id; partner_id_2; email_1; phone_1; email_2; phone_2; stage_id; user_id |
| **Yêu cầu bắt buộc** | <ul><li>Stage: New/Qualified/Proposition/Won</li><li>Tên MM{id} Company A Company B XSGT</li><li>Có List/Form/Kanban views</li><li>Kanban group theo Stage</li></ul> |
| **Yêu cầu nâng cao** | Thêm smart button trên Contact |
| **Deliverables** | Addon; views; security; demo |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 20: Match Making Recommendation - Top 10 doanh nghiệp phù hợp**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 20 |
| **Nhóm** | Matchmaking Scoring |
| **Mô tả** | Đề xuất Top 10 doanh nghiệp phù hợp dựa trên dữ liệu Contact. |
| **Công nghệ** | Odoo/Python |
| **Nguồn dữ liệu** | Contact attributes |
| **Đích dữ liệu** | Top 10 matching contacts |
| **Dữ liệu chính** | Product Category; Product Details; Industry; Country; Event; Type Contact |
| **Yêu cầu bắt buộc** | <ul><li>Thiết kế scoring algorithm</li><li>Ví dụ:</li><li>- Category +30</li><li>- Industry +20</li><li>- Same event +20</li><li>- Buyer/Seller +20</li><li>- Same country +5</li><li>- Giải thích điểm</li><li>- Tránh match chính nó</li></ul> |
| **Yêu cầu nâng cao** | Button "Find Matching Companies" trên Contact |
| **Deliverables** | Scoring doc; source; demo dataset |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Logic/Odoo |

---

### **BÀI 21: Dashboard CRM Sales Analytics**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 21 |
| **Nhóm** | CRM Analytics |
| **Mô tả** | Tạo OWL dashboard phân tích CRM theo thời gian, nhân viên, event, source. |
| **Công nghệ** | Odoo OWL, ORM |
| **Nguồn dữ liệu** | Odoo CRM |
| **Đích dữ liệu** | Dashboard |
| **Dữ liệu chính** | Date From/To; Salesperson; Event; Country; Source |
| **Yêu cầu bắt buộc** | <ul><li>KPI:</li><li>- Total Leads</li><li>- Total Deals</li><li>- Won/Lost</li><li>- Conversion Rate</li><li>- Revenue</li><li>- Avg Deal Value</li><li>- Facebook/HubSpot/Website Leads</li><li>- Chart theo ngày/stage/salesperson/event/source</li></ul> |
| **Yêu cầu nâng cao** | Thêm export CSV/PDF |
| **Deliverables** | Addon dashboard; screenshots; README; demo |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Frontend/Odoo |

---

### **BÀI 22: Dashboard HR Attendance**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 22 |
| **Nhóm** | HR Analytics |
| **Mô tả** | Tạo dashboard chấm công bằng Odoo OWL Client Action. |
| **Công nghệ** | Odoo OWL, Attendance data |
| **Nguồn dữ liệu** | Attendance logs/results |
| **Đích dữ liệu** | Dashboard |
| **Dữ liệu chính** | Period; Department; Employee |
| **Yêu cầu bắt buộc** | <ul><li>KPI:</li><li>- Employees</li><li>- Checked In/Out</li><li>- Late/Early Leave/Absent</li><li>- Missing Checkout</li><li>- Worked Hours</li><li>- Avg Hours</li><li>- Attendance Rate</li><li>- Charts: trend/distribution/department</li></ul> |
| **Yêu cầu nâng cao** | Thêm employee watch list và recent logs |
| **Deliverables** | Addon dashboard; test data; demo |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Frontend/Odoo |

---

### **BÀI 23: Mini CRM Integration Platform (Capstone)**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 23 |
| **Nhóm** | Capstone Integration |
| **Mô tả** | Xây middleware kết nối HubSpot, Google Sheet, Odoo1 và Odoo2. |
| **Công nghệ** | FastAPI, DB, HubSpot API, Odoo API, Google Sheets API |
| **Nguồn dữ liệu** | HubSpot/Sheet/API |
| **Đích dữ liệu** | Odoo1/Odoo2 + status API |
| **Dữ liệu chính** | sync_job: id; model; record_id; source; destination; status; retry_count; created_at; updated_at; error_message |
| **Yêu cầu bắt buộc** | <ul><li>API Endpoints:</li><li>- POST /contacts</li><li>- GET /contacts/{id}</li><li>- POST /deals</li><li>- POST /sync/hubspot</li><li>- POST /sync/odoo2</li><li>- GET /sync/status/{id}</li><li>- Retry logic</li><li>- Logging</li><li>- Duplicate prevention</li><li>- Auth & env config</li><li>- Timeout & error handling</li></ul> |
| **Yêu cầu nâng cao** | Docker Compose + worker queue (Celery) |
| **Deliverables** | Architecture; source; DB schema; API docs; demo |
| **Độ khó** | ⭐⭐⭐⭐ Khó |
| **Đối tượng** | TTS khá/nhóm |
| **Quy mô** | 2-3 TTS |

---

### **BÀI 24: SaigonTrade Lead-to-Deal Automation (Capstone)**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 24 |
| **Nhóm** | Capstone SaigonTrade |
| **Mô tả** | Tổng hợp nhiều nguồn khách hàng vào Odoo, sync Odoo2/HubSpot và theo dõi bằng Google Sheet/Dashboard. |
| **Công nghệ** | HubSpot, Social, Google Sheet, API, Odoo1, Odoo2 |
| **Nguồn dữ liệu** | Facebook; TikTok; HubSpot; Google Sheet; Website; Event |
| **Đích dữ liệu** | Odoo CRM + Odoo2 + Google Sheet + Dashboard |
| **Dữ liệu chính** | Source; Source URL; Event; Event Location; Contact; Salesperson; Note; Product Interest; sync statuses |
| **Yêu cầu bắt buộc** | <ul><li>Contact Matching ưu tiên: External ID → Email → Phone → Mobile → Name+Company</li><li>Deal: x_deal_id=NL{odoo1_lead_id}</li><li>Monitoring Sheet</li><li>Integration Errors</li><li>Retry/Retry All/Ignore</li><li>Audit Log: datetime/source/destination/model/record/action/success/error/response time</li></ul> |
| **Yêu cầu nâng cao** | Thêm queue, SLA monitoring và alert lỗi |
| **Deliverables** | Full project; architecture; source; deployment guide; demo end-to-end |
| **Độ khó** | ⭐⭐⭐⭐⭐ Rất khó |
| **Đối tượng** | Capstone 2-4 TTS |
| **Quy mô** | 4-6 tuần |

---

### **BÀI 25: Addon quản lý KPI Sales theo tháng**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 25 |
| **Nhóm** | Odoo Sales Addon |
| **Mô tả** | Xây addon theo dõi mục tiêu doanh số từng nhân viên/phòng kinh doanh và so sánh thực tế với kế hoạch. |
| **Công nghệ** | Odoo, Python, XML, ORM |
| **Nguồn dữ liệu** | crm.lead, sale.order, res.users |
| **Đích dữ liệu** | Model KPI + Dashboard |
| **Dữ liệu chính** | salesperson, month, target_revenue, actual_revenue, target_deals, won_deals, conversion_rate |
| **Yêu cầu bắt buộc** | <ul><li>Tạo model KPI</li><li>Cấu hình target theo tháng</li><li>Tự tính actual revenue/deals</li><li>Phân quyền Sales/Manager</li><li>List/Form/Pivot views</li><li>Cảnh báo chưa đạt KPI</li></ul> |
| **Yêu cầu nâng cao** | Thêm forecast cuối tháng và xếp hạng nhân viên |
| **Deliverables** | Addon hoàn chỉnh, README, demo data, test cases |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 26: Addon Commission - tính hoa hồng Sales**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 26 |
| **Nhóm** | Odoo Sales Addon |
| **Mô tả** | Tính hoa hồng tự động dựa trên Deal Won hoặc hóa đơn đã thanh toán. |
| **Công nghệ** | Odoo Sales, CRM, Accounting |
| **Nguồn dữ liệu** | crm.lead, sale.order, account.move |
| **Đích dữ liệu** | Commission records + báo cáo |
| **Dữ liệu chính** | salesperson, deal_id, amount, commission_rate, commission_value, state |
| **Yêu cầu bắt buộc** | <ul><li>Thiết lập rule hoa hồng theo mức doanh số</li><li>Tự tạo commission</li><li>Trạng thái: draft/approved/paid</li><li>Không tính trùng</li></ul> |
| **Yêu cầu nâng cao** | Commission theo sản phẩm, team, tier doanh thu |
| **Deliverables** | Addon, rule engine, report commission, test data |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo/Python |

---

### **BÀI 27: Lead Source Tracking Addon**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 27 |
| **Nhóm** | Tracking kinh doanh |
| **Mô tả** | Theo dõi nguồn khách hàng từ Facebook, TikTok, Website, Event, HubSpot, Referral và đo hiệu quả từng nguồn. |
| **Công nghệ** | Odoo CRM, Python, XML |
| **Nguồn dữ liệu** | crm.lead |
| **Đích dữ liệu** | Dashboard + reports |
| **Dữ liệu chính** | source, campaign, event, cost, leads, won, revenue, conversion_rate |
| **Yêu cầu bắt buộc** | <ul><li>Bổ sung tracking source/campaign</li><li>Tổng hợp Lead/Deal/Revenue</li><li>Filter theo thời gian và salesperson</li></ul> |
| **Yêu cầu nâng cao** | Tính CAC/ROI khi nhập chi phí campaign |
| **Deliverables** | Addon, dashboard, pivot report, README |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS CRM/Odoo |

---

### **BÀI 28: Customer Journey Tracking**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 28 |
| **Nhóm** | Tracking kinh doanh |
| **Mô tả** | Ghi lại hành trình khách hàng từ Lead → Contact → Deal → Sale → Invoice → Repeat Purchase. |
| **Công nghệ** | Odoo CRM, Sales, Accounting, Mail |
| **Nguồn dữ liệu** | crm.lead, res.partner, sale.order, account.move |
| **Đích dữ liệu** | Journey timeline |
| **Dữ liệu chính** | customer, stage, event_type, record_model, record_id, datetime, user |
| **Yêu cầu bắt buộc** | <ul><li>Tạo timeline tự động</li><li>Mỗi chuyển trạng thái ghi một event</li><li>Xem lịch sử trên Contact</li></ul> |
| **Yêu cầu nâng cao** | Tính thời gian trung bình giữa các bước và phát hiện bottleneck |
| **Deliverables** | Addon, timeline view, analytics report |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 29: Sales Pipeline Aging Report**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 29 |
| **Nhóm** | Báo cáo |
| **Mô tả** | Phát hiện Deal nằm quá lâu tại một stage. |
| **Công nghệ** | Odoo CRM, SQL/ORM, Reporting |
| **Nguồn dữ liệu** | crm.lead, crm.stage |
| **Đích dữ liệu** | Report + cảnh báo |
| **Dữ liệu chính** | lead, stage, entered_stage_date, age_days, owner, expected_revenue |
| **Yêu cầu bắt buộc** | <ul><li>Lưu thời điểm vào stage</li><li>Tính aging days</li><li>Report theo stage/user</li><li>Tô cảnh báo Deal quá hạn</li></ul> |
| **Yêu cầu nâng cao** | Gửi email/activity tự động cho Sales Manager |
| **Deliverables** | Addon, report, scheduled action |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 30: Lost Deal Analysis**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 30 |
| **Nhóm** | Báo cáo |
| **Mô tả** | Phân tích nguyên nhân Deal Lost để cải thiện tỷ lệ thắng. |
| **Công nghệ** | Odoo CRM |
| **Nguồn dữ liệu** | crm.lead |
| **Đích dữ liệu** | Dashboard Lost Reasons |
| **Dữ liệu chính** | lost_reason, competitor, amount, salesperson, source, event |
| **Yêu cầu bắt buộc** | <ul><li>Bắt buộc chọn lý do khi đánh dấu Lost</li><li>Báo cáo theo lý do, salesperson, source, tháng</li></ul> |
| **Yêu cầu nâng cao** | AI/keyword phân nhóm ghi chú lost reason |
| **Deliverables** | Addon, dashboard, pivot/list |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 31: PDF Sales Quotation nâng cao**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 31 |
| **Nhóm** | In file / PDF |
| **Mô tả** | Thiết kế mẫu báo giá chuyên nghiệp cho SaigonTrade với logo, thông tin khách, sản phẩm, điều khoản và QR. |
| **Công nghệ** | Odoo QWeb PDF |
| **Nguồn dữ liệu** | sale.order, res.partner, product.product |
| **Đích dữ liệu** | PDF quotation |
| **Dữ liệu chính** | customer, quotation_no, lines, subtotal, tax, total, salesperson, validity_date |
| **Yêu cầu bắt buộc** | <ul><li>Tạo report QWeb PDF</li><li>Hỗ trợ tiếng Việt</li><li>Format số tiền (1,000,000)</li><li>QR link quotation</li><li>Footer điều khoản</li></ul> |
| **Yêu cầu nâng cao** | Template theo brand/customer segment |
| **Deliverables** | Addon report, QWeb template, sample PDFs |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo/XML |

---

### **BÀI 32: Export CRM Pipeline ra Excel**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 32 |
| **Nhóm** | In file / Excel |
| **Mô tả** | Cho phép Sales Manager xuất pipeline ra XLSX theo bộ lọc hiện tại. |
| **Công nghệ** | Odoo, Python, xlsxwriter/openpyxl |
| **Nguồn dữ liệu** | crm.lead |
| **Đích dữ liệu** | XLSX |
| **Dữ liệu chính** | deal, stage, owner, amount, source, event, create_date, close_date |
| **Yêu cầu bắt buộc** | <ul><li>Wizard chọn thời gian/team/stage</li><li>Export xlsx</li><li>Header format</li><li>Tổng doanh số cuối file</li></ul> |
| **Yêu cầu nâng cao** | Thêm chart trong Excel và sheet Summary |
| **Deliverables** | Addon export wizard, sample xlsx |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Python/Odoo |

---

### **BÀI 33: Customer 360 PDF Report**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 33 |
| **Nhóm** | In file / PDF |
| **Mô tả** | Xuất một hồ sơ tổng hợp khách hàng từ Contact gồm thông tin, Deal, Sale, Invoice, Activity, notes. |
| **Công nghệ** | Odoo QWeb PDF |
| **Nguồn dữ liệu** | res.partner, crm.lead, sale.order, account.move, mail.activity |
| **Đích dữ liệu** | PDF Customer 360 |
| **Dữ liệu chính** | contact, company, phones, deals, revenue, invoices, activities, last_contact |
| **Yêu cầu bắt buộc** | <ul><li>Button trên Contact</li><li>Gom dữ liệu nhiều model</li><li>Báo cáo rõ section</li><li>Chỉ user có quyền mới xem</li></ul> |
| **Yêu cầu nâng cao** | Thêm biểu đồ doanh số 12 tháng trong PDF |
| **Deliverables** | Addon, PDF report, permissions |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 34: Executive Sales Dashboard**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 34 |
| **Nhóm** | Dashboard |
| **Mô tả** | Dashboard dành cho quản lý kinh doanh theo dõi toàn bộ hiệu suất Sales. |
| **Công nghệ** | Odoo OWL, RPC, Chart |
| **Nguồn dữ liệu** | crm.lead, sale.order, account.move |
| **Đích dữ liệu** | OWL dashboard |
| **Dữ liệu chính** | revenue, pipeline, won, lost, avg_deal, conversion, salesperson, source |
| **Yêu cầu bắt buộc** | <ul><li>KPI cards</li><li>Filter date/team/source</li><li>Chart doanh số</li><li>Pipeline funnel</li><li>Top salesperson</li></ul> |
| **Yêu cầu nâng cao** | Drill-down từ KPI/chart vào record Odoo |
| **Deliverables** | Addon dashboard OWL, screenshots, README |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo/JS |

---

### **BÀI 35: Event/Expo Performance Dashboard**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 35 |
| **Nhóm** | Dashboard |
| **Mô tả** | Đo hiệu quả các hội chợ/sự kiện của SaigonTrade. |
| **Công nghệ** | Odoo, OWL, CRM |
| **Nguồn dữ liệu** | crm.lead, event fields, sale.order |
| **Đích dữ liệu** | Dashboard event |
| **Dữ liệu chính** | event, leads, contacts, deals, won, revenue, conversion, country |
| **Yêu cầu bắt buộc** | <ul><li>Dashboard theo Event</li><li>So sánh event</li><li>Filter salesperson/country/date</li><li>Drill-down</li></ul> |
| **Yêu cầu nâng cao** | Chi phí event và ROI |
| **Deliverables** | Addon dashboard, data model, demo |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 36: Sales Activity SLA Tracker**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 36 |
| **Nhóm** | Tracking |
| **Mô tả** | Theo dõi Sales có chăm Lead đúng hạn không. |
| **Công nghệ** | Odoo CRM, mail.activity, cron |
| **Nguồn dữ liệu** | crm.lead, mail.activity |
| **Đích dữ liệu** | SLA tracker + alerts |
| **Dữ liệu chính** | lead, owner, last_activity, next_activity, overdue_days, sla_status |
| **Yêu cầu bắt buộc** | <ul><li>Định nghĩa SLA theo stage</li><li>Tự tính overdue</li><li>Dashboard overdue</li><li>Scheduled action tạo cảnh báo</li></ul> |
| **Yêu cầu nâng cao** | Score Sales dựa trên SLA compliance |
| **Deliverables** | Addon, cron, report |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 37: Customer Segmentation Addon**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 37 |
| **Nhóm** | Addon kinh doanh |
| **Mô tả** | Phân nhóm khách hàng tự động theo doanh thu, tần suất mua, nguồn và ngành hàng. |
| **Công nghệ** | Odoo, Python |
| **Nguồn dữ liệu** | res.partner, sale.order, account.move |
| **Đích dữ liệu** | Segments/tags |
| **Dữ liệu chính** | customer, total_revenue, order_count, last_order, industry, segment |
| **Yêu cầu bắt buộc** | <ul><li>Tính segment A/B/C hoặc VIP/Active/Dormant</li><li>Cập nhật định kỳ</li><li>Filter Contact theo segment</li></ul> |
| **Yêu cầu nâng cao** | RFM scoring đầy đủ |
| **Deliverables** | Addon, scheduled action, report |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo/Python |

---

### **BÀI 38: Dormant Customer Reactivation**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 38 |
| **Nhóm** | Addon kinh doanh |
| **Mô tả** | Phát hiện khách hàng lâu không giao dịch và tạo chiến dịch chăm sóc lại. |
| **Công nghệ** | Odoo CRM/Sales/Mail |
| **Nguồn dữ liệu** | res.partner, sale.order, mail.activity |
| **Đích dữ liệu** | Reactivation queue |
| **Dữ liệu chính** | customer, last_order_date, inactive_days, owner, status |
| **Yêu cầu bắt buộc** | <ul><li>Wizard chọn số ngày không mua</li><li>Tạo danh sách</li><li>Assign salesperson</li><li>Tạo activity follow-up</li></ul> |
| **Yêu cầu nâng cao** | Tự tạo CRM opportunity reactivation |
| **Deliverables** | Addon, wizard, cron, report |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 39: Product Interest Tracking**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 39 |
| **Nhóm** | Addon kinh doanh |
| **Mô tả** | Theo dõi khách quan tâm sản phẩm nào trong CRM để phục vụ sales follow-up. |
| **Công nghệ** | Odoo CRM, Product |
| **Nguồn dữ liệu** | crm.lead, product.template |
| **Đích dữ liệu** | Interest records + reports |
| **Dữ liệu chính** | lead, product, category, interest_level, qty_estimate, note |
| **Yêu cầu bắt buộc** | <ul><li>Many2many/line model sản phẩm quan tâm</li><li>Report theo product/category/source/event</li></ul> |
| **Yêu cầu nâng cao** | Gợi ý sản phẩm tương tự hoặc cross-sell |
| **Deliverables** | Addon, views, report |
| **Độ khó** | ⭐ - ⭐⭐ Dễ-Trung bình |
| **Đối tượng** | TTS mới |

---

### **BÀI 40: Sales Visit / Meeting Tracking**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 40 |
| **Nhóm** | Addon kinh doanh |
| **Mô tả** | Quản lý lịch gặp khách, kết quả cuộc gặp và follow-up. |
| **Công nghệ** | Odoo Calendar, CRM, Contacts |
| **Nguồn dữ liệu** | calendar.event, crm.lead, res.partner |
| **Đích dữ liệu** | Visit records + dashboard |
| **Dữ liệu chính** | customer, salesperson, datetime, location, purpose, result, next_action |
| **Yêu cầu bắt buộc** | <ul><li>Tạo visit từ Lead/Contact</li><li>Trạng thái planned/done/cancelled</li><li>Result bắt buộc khi done</li></ul> |
| **Yêu cầu nâng cao** | GPS/check-in hoặc attachment hình ảnh biên bản |
| **Deliverables** | Addon, views, report |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 41: Salesperson Daily Report**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 41 |
| **Nhóm** | Báo cáo |
| **Mô tả** | Tự động tổng hợp báo cáo công việc Sales hàng ngày. |
| **Công nghệ** | Odoo CRM, Mail, Cron |
| **Nguồn dữ liệu** | crm.lead, mail.activity, sale.order |
| **Đích dữ liệu** | Daily report HTML/PDF/email |
| **Dữ liệu chính** | salesperson, new_leads, calls, meetings, won, lost, revenue, overdue |
| **Yêu cầu bắt buộc** | <ul><li>Cron mỗi ngày tổng hợp theo salesperson</li><li>Lưu report record</li><li>Manager xem lịch sử</li></ul> |
| **Yêu cầu nâng cao** | Gửi email PDF tự động cho quản lý |
| **Deliverables** | Addon, cron, report template |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 42: Weekly Business Review Pack**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 42 |
| **Nhóm** | Báo cáo |
| **Mô tả** | Sinh bộ báo cáo tuần gồm CRM, sales, customer, source, event và tồn đọng. |
| **Công nghệ** | Odoo Reporting, PDF/XLSX |
| **Nguồn dữ liệu** | CRM/Sales/Contacts |
| **Đích dữ liệu** | PDF + Excel pack |
| **Dữ liệu chính** | week, pipeline, revenue, won, lost, new_contacts, top_sources, overdue |
| **Yêu cầu bắt buộc** | <ul><li>Wizard chọn tuần</li><li>Tạo PDF executive summary và XLSX detail</li><li>Số liệu phải khớp</li></ul> |
| **Yêu cầu nâng cao** | Tự động lưu attachment và gửi mail thứ Hai |
| **Deliverables** | Addon, PDF, XLSX, scheduled action |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 43: Data Change Audit Addon**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 43 |
| **Nhóm** | Tracking |
| **Mô tả** | Theo dõi ai đã sửa các field kinh doanh quan trọng trên Lead/Contact/Deal. |
| **Công nghệ** | Odoo ORM, mail.thread |
| **Nguồn dữ liệu** | crm.lead, res.partner, sale.order |
| **Đích dữ liệu** | Audit log |
| **Dữ liệu chính** | model, record_id, field, old_value, new_value, user, datetime |
| **Yêu cầu bắt buộc** | <ul><li>Track field cấu hình</li><li>List audit log</li><li>Filter user/date/model</li><li>Chỉ manager được xem</li></ul> |
| **Yêu cầu nâng cao** | Export audit log PDF/XLSX |
| **Deliverables** | Addon, security, audit views |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo/Python |

---

### **BÀI 44: Deal Sync Monitoring Center**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 44 |
| **Nhóm** | Tracking |
| **Mô tả** | Màn hình trung tâm theo dõi trạng thái đồng bộ Deal giữa Odoo1, Odoo2, HubSpot, Google Sheet. |
| **Công nghệ** | Odoo, API, Cron |
| **Nguồn dữ liệu** | sync logs, crm.lead |
| **Đích dữ liệu** | Monitoring dashboard |
| **Dữ liệu chính** | deal, destination, status, retry_count, last_sync, error_message, duration |
| **Yêu cầu bắt buộc** | <ul><li>Model sync log</li><li>Dashboard success/failed/pending</li><li>Retry từng record</li><li>Retry all</li><li>Lưu lỗi chi tiết</li></ul> |
| **Yêu cầu nâng cao** | Biểu đồ error theo hệ thống và SLA xử lý lỗi |
| **Deliverables** | Addon monitoring, dashboard, retry flow |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Integration/Odoo |

---

### **BÀI 45: Sales Forecast Dashboard**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 45 |
| **Nhóm** | Dashboard |
| **Mô tả** | Dự báo doanh thu dựa trên pipeline và probability của Deal. |
| **Công nghệ** | Odoo CRM, Python, OWL |
| **Nguồn dữ liệu** | crm.lead |
| **Đích dữ liệu** | Forecast dashboard |
| **Dữ liệu chính** | expected_revenue, probability, weighted_revenue, close_date, stage, salesperson |
| **Yêu cầu bắt buộc** | <ul><li>Tính weighted revenue</li><li>Forecast tuần/tháng/quý</li><li>Filter team/salesperson</li><li>Compare target</li></ul> |
| **Yêu cầu nâng cao** | Scenario Best/Base/Worst Case |
| **Deliverables** | Addon dashboard, formulas, demo |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo/Data |

---

### **BÀI 46: Auto Generate Meeting Minutes PDF**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 46 |
| **Nhóm** | In file / Document |
| **Mô tả** | Sau cuộc họp với khách, nhập nội dung biên bản và sinh PDF chuẩn để lưu vào Contact/Deal. |
| **Công nghệ** | Odoo QWeb, Attachment |
| **Nguồn dữ liệu** | crm.lead, res.partner, custom meeting model |
| **Đích dữ liệu** | PDF + attachment |
| **Dữ liệu chính** | meeting_date, participants, discussion, decisions, action_items, owner, deadline |
| **Yêu cầu bắt buộc** | <ul><li>Model meeting minutes</li><li>Button Generate PDF</li><li>Attach vào Lead/Contact</li><li>Numbering tự động</li></ul> |
| **Yêu cầu nâng cao** | Cho khách ký hoặc upload signed copy |
| **Deliverables** | Addon, QWeb PDF, attachment flow |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 47: Sales Approval Workflow**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 47 |
| **Nhóm** | Addon kinh doanh |
| **Mô tả** | Thiết kế quy trình phê duyệt Deal/Báo giá vượt ngưỡng giá trị hoặc discount. |
| **Công nghệ** | Odoo CRM/Sales, Security |
| **Nguồn dữ liệu** | crm.lead, sale.order |
| **Đích dữ liệu** | Approval workflow |
| **Dữ liệu chính** | amount, discount, approver, approval_state, reason, approved_at |
| **Yêu cầu bắt buộc** | <ul><li>Rule theo amount/discount</li><li>Trạng thái pending/approved/rejected</li><li>Sales không xác nhận trước khi duyệt</li></ul> |
| **Yêu cầu nâng cao** | Nhiều cấp duyệt theo ngưỡng và email/activity notification |
| **Deliverables** | Addon, rules, security, test cases |
| **Độ khó** | ⭐⭐⭐ Khá |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 48: SaigonTrade Business Control Center (Capstone)**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 48 |
| **Nhóm** | Capstone Business Addon |
| **Mô tả** | Xây addon tổng hợp cho quản lý: Sales KPI, Pipeline, Event performance, Tracking, Reports, Export và Alerts. |
| **Công nghệ** | Odoo, OWL, Python, QWeb, XLSX, Cron |
| **Nguồn dữ liệu** | CRM, Sales, Contacts, Activities, Sync Logs |
| **Đích dữ liệu** | Unified dashboard + reports |
| **Dữ liệu chính** | KPI, pipeline, event, source, salesperson, overdue, sync_error, revenue |
| **Yêu cầu bắt buộc** | <ul><li>Dashboard tổng</li><li>Drill-down</li><li>Báo cáo PDF/XLSX</li><li>Cảnh báo overdue/sync fail/KPI</li><li>Role Manager/Sales</li><li>Dữ liệu demo</li></ul> |
| **Yêu cầu nâng cao** | Forecast, commission, customer segmentation và scheduled weekly executive report |
| **Deliverables** | Addon capstone, architecture, source, README, demo video, test checklist |
| **Độ khó** | ⭐⭐⭐⭐ Nâng cao |
| **Đối tượng** | Nhóm 2-4 TTS |

---

### **BÀI 49: Addon tự động phân chia Lead cho Sales**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 49 |
| **Nhóm** | Sales Automation |
| **Mô tả** | Xây addon Odoo tự động phân Lead mới cho nhân viên Sales dựa trên khu vực, nguồn lead, ngành hàng hoặc tải công việc. |
| **Công nghệ** | Odoo, Python, ORM, Automated Action |
| **Nguồn dữ liệu** | crm.lead, res.users, res.partner |
| **Đích dữ liệu** | crm.lead |
| **Dữ liệu chính** | user_id, team_id, source, country, industry, assigned_at |
| **Yêu cầu bắt buộc** | <ul><li>Có rule phân chia</li><li>Tránh giao trùng</li><li>Log người được giao</li><li>Hỗ trợ bật/tắt rule</li><li>Có nút re-assign</li></ul> |
| **Yêu cầu nâng cao** | Thuật toán round-robin hoặc weighted assignment; dashboard tải công việc theo Sales |
| **Deliverables** | Addon, README, test data, demo video |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 50: Addon nhắc follow-up khách hàng quá hạn**

| Thông tin | Chi tiết |
|-----------|----------|
| **STT** | 50 |
| **Nhóm** | Sales Follow-up |
| **Mô tả** | Theo dõi Lead/Deal chưa có hoạt động mới sau X ngày và cảnh báo Sales xử lý. |
| **Công nghệ** | Odoo, mail.activity, cron |
| **Nguồn dữ liệu** | crm.lead, mail.activity, mail.message |
| **Đích dữ liệu** | Odoo Notification / Activity |
| **Dữ liệu chính** | last_activity_date, next_activity_date, user_id, stage_id, overdue_days |
| **Yêu cầu bắt buộc** | <ul><li>Cron chạy hàng ngày</li><li>Xác định lead quá hạn</li><li>Tạo activity</li><li>Tránh tạo trùng cảnh báo</li></ul> |
| **Yêu cầu nâng cao** | Escalate cho trưởng nhóm nếu quá hạn nhiều ngày; cấu hình SLA theo stage |
| **Deliverables** | Addon, cron, config view, README |
| **Độ khó** | ⭐⭐ Trung bình |
| **Đối tượng** | TTS Odoo |

---

### **BÀI 51-72: Các bài tập còn lại**

*[Bài 51-72 sẽ theo cấu trúc tương tự, bao gồm các addon như: Customer Care Tracking, Quotation Tracking, Contract Management, Receivable Tracking, Commission, Lead Scoring, Lead Duplicate Detection, Customer 360, Business Report, Event CRM, Print Center, Document Tracking, Management Cockpit, v.v.]*

---

## Tiến độ Thực hiện

### Bảng Theo dõi

| STT | Tên bài tập | TTS phụ trách | Ngày giao | Deadline | Trạng thái | Tiến độ | Điểm |
|-----|-----------|----------|----------|----------|----------|---------|------|
| 1 | Đồng bộ HubSpot Contact về Google Sheet | Chất, Hiếu, Đông Vy, Cường, Khang, Bình, Minh, Huy | 2026-08-17 | 2026-08-19 | Đã giao | 0% | - |
| 2 | Import Contact từ Google Sheet vào HubSpot | Chất, Hiếu, Đông Vy, Cường, Khang, Bình, Minh, Huy | 2026-08-18 | 2026-08-20 | Chưa giao | 0% | - |
| 3 | Đồng bộ HubSpot Deal sang Google Sheet | Chất, Hiếu, Đông Vy, Cường, Khang, Bình, Minh, Huy | 2026-08-19 | 2026-08-21 | Chưa giao | 0% | - |
| 4 | Webhook HubSpot → Python API → Google Sheet | Chất, Hiếu, Đông Vy, Cường, Khang, Bình, Minh, Huy | 2026-08-20 | 2026-08-22 | Chưa giao | 0% | - |

*[Các bài tập khác chưa có thời gian giao]*

---

## Tiêu chí Đánh giá

Mỗi bài tập được chấm điểm theo 9 tiêu chí:

### **1. Phân tích (Điểm phân tích)**
- Hiểu rõ yêu cầu
- Xác định input/output
- Phân tích dữ liệu

### **2. Kiến trúc (Điểm kiến trúc)**
- Design tổng thể hợp lý
- Modular & maintainable
- Scalability

### **3. Code (Điểm code)**
- Clean code
- PEP 8 / coding standards
- Efficiency

### **4. Chức năng (Điểm chức năng)**
- Đáp ứng 100% yêu cầu bắt buộc
- Chức năng đúng
- User experience tốt

### **5. Xử lý lỗi (Điểm xử lý lỗi)**
- Try-catch toàn diện
- Edge cases
- Recovery logic

### **6. Logging (Điểm logging)**
- Log INFO/WARN/ERROR rõ ràng
- Trace lỗi dễ dàng
- Performance metrics

### **7. Security (Điểm security)**
- Auth/authorization
- Input validation
- SQL injection prevention
- Secrets management

### **8. README (Điểm README)**
- Installation clear
- Usage examples
- Configuration
- Troubleshooting

### **9. Demo (Điểm demo)**
- Chạy được
- Dữ liệu test
- Video demo

---

## Công nghệ & Stack

### **Frontend**
- Odoo OWL (JavaScript)
- QWeb Templates
- Chart.js, Plotly
- Tailwind CSS (nếu có)

### **Backend**
- Python 3.8+
- Odoo 14/16/17
- FastAPI / Flask
- Celery (async tasks)

### **APIs & Integrations**
- HubSpot v3 API
- Odoo JSON-RPC/XML-RPC API
- Google Sheets API v4
- Facebook/TikTok APIs
- REST APIs

### **Database**
- PostgreSQL (Odoo)
- SQLite (local testing)

### **DevOps**
- Docker & Docker Compose
- Git & GitHub
- Postman (API testing)
- GitHub Actions (CI/CD)

### **Tools**
- VS Code / PyCharm
- Odoo Studio
- Navicat / DBeaver
- Excel / Google Sheets

---

## Tài nguyên & Hỗ trợ

### **Tài liệu chính thức**
- Odoo Documentation: https://www.odoo.com/documentation
- HubSpot API: https://developers.hubspot.com
- Google Sheets API: https://developers.google.com/sheets
- FastAPI: https://fastapi.tiangolo.com

### **Ví dụ & Mẫu**
- Odoo addons samples: `/opt/odoo/addons/samples`
- API Postman collection: `sgt_postman_collection.json`
- Sheet templates: `templates/google_sheets/`

### **Hỗ trợ & Thảo luận**
- Slack channel: `#sgt-lms-support`
- Forum: `forum.saigontrade.local`
- Office hours: Thứ Năm 14:00-15:30

---

## Ghi chú

- **Bài tập từ 1-15**: Kiến thức cơ bản, phù hợp TTS mới
- **Bài tập từ 16-50**: Addon Odoo, nâng cao hơn
- **Bài tập từ 51-72**: Các addon specialized, yêu cầu kinh nghiệm
- **Capstone (23, 24, 48, 72)**: Dự án lớn, 2-4 người, 4-6 tuần

---

*Tài liệu này được cập nhật lần cuối: 2026-08-21*  
*Liên hệ: sgt-lms-team@saigontrade.local*
