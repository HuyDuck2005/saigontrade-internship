# 🚀 Dự án Quản lý Thực tập sinh — Intern Work Management

> **Custom Odoo Module hỗ trợ quản lý công việc, báo cáo, thuyết trình và đánh giá thực tập sinh**

**Người phát triển:** Vũ Huy Đức
**Đơn vị:** Đại học Quản lý và Công nghệ TP.HCM (UMT)
**Môi trường phát triển:** WSL Ubuntu, Docker, Odoo 17
**Container:** `odoo-app`
**Repository:** `saigontrade-internship`

---

## 📌 1. Tổng quan dự án

**Intern Work Management** là một Custom Module được xây dựng trên **Odoo 17**, nhằm hỗ trợ doanh nghiệp quản lý quá trình làm việc của thực tập sinh một cách tập trung.

Hệ thống tập trung vào ba hoạt động chính:

1. Ghi nhận công việc và kết quả làm việc hằng ngày.
2. Quản lý báo cáo, thuyết trình và đánh giá định kỳ.
3. Hỗ trợ người quản lý theo dõi tiến độ, duyệt báo cáo và đánh giá thực tập sinh.

Module được tích hợp với các thành phần có sẵn của Odoo như:

* **Project** — quản lý Project và Task.
* **Employees** — quản lý thông tin thực tập sinh.
* **Discuss** — thông báo và trao đổi.
* **Users & Security** — quản lý tài khoản và phân quyền.
* **Scheduled Actions / Cron** — tự động hóa các công việc định kỳ.

---

## 🎯 2. Mục tiêu hệ thống

### Đối với thực tập sinh

* Ghi nhận công việc đã thực hiện mỗi ngày.
* Mô tả vấn đề gặp phải và cách giải quyết.
* Liên kết báo cáo với Task thực tế.
* Theo dõi trạng thái báo cáo.
* Chuẩn bị nội dung cho các buổi thuyết trình.
* Xem nhận xét và yêu cầu chỉnh sửa từ người quản lý.

### Đối với người quản lý

* Theo dõi tiến độ của từng thực tập sinh.
* Kiểm tra báo cáo hằng ngày.
* Duyệt hoặc yêu cầu chỉnh sửa báo cáo.
* Đánh giá kết quả làm việc.
* Theo dõi Task hoàn thành.
* Quản lý lịch thuyết trình.
* Xem Dashboard tổng quan.
* Phát hiện những trường hợp chưa nộp báo cáo.

### Đối với Admin

* Quản lý người dùng và phân quyền.
* Quản lý Project và Task.
* Quản lý toàn bộ báo cáo.
* Duyệt hàng loạt báo cáo/thuyết trình.
* Theo dõi dữ liệu tổng hợp.
* Quản lý cấu hình hệ thống.

---

# 🏗️ 3. Kiến trúc tổng thể

```text
                    ┌─────────────────────────┐
                    │       Odoo 17           │
                    │     Intern Work         │
                    │      Management         │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
      ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
      │ Daily Report│     │Weekly Report│     │ Presentation│
      └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │ Odoo Project     │
                       │ Project / Task   │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Dashboard / KPI  │
                       └──────────────────┘
```

---

# 📁 4. Cấu trúc thư mục

Cấu trúc module được tổ chức theo chuẩn Custom Module của Odoo:

```text
intern_work_management/
│
├── __init__.py
├── __manifest__.py
│
├── models/
│   ├── __init__.py
│   ├── daily_report.py
│   ├── weekly_report.py
│   ├── task_presentation.py
│   └── project_project.py
│
├── views/
│   ├── daily_report_views.xml
│   ├── weekly_report_views.xml
│   ├── task_presentation_views.xml
│   ├── dashboard_views.xml
│   └── project_views.xml
│
├── security/
│   ├── security_groups.xml
│   └── ir.model.access.csv
│
├── data/
│   └── ir_cron.xml
│
└── static/
    └── description/
        └── icon.png
```

## 4.1. `__manifest__.py`

File khai báo thông tin của module:

* Tên module.
* Phiên bản.
* Mô tả.
* Dependencies.
* Danh sách XML/CSV cần load.
* Category.
* Application.

Ví dụ:

```python
{
    "name": "Intern Work Management",
    "version": "17.0.1.0.0",
    "category": "Project",
    "summary": "Quản lý công việc và báo cáo thực tập sinh",
    "depends": [
        "base",
        "project",
        "hr",
        "mail",
    ],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",

        "views/daily_report_views.xml",
        "views/weekly_report_views.xml",
        "views/task_presentation_views.xml",
        "views/project_views.xml",
        "views/dashboard_views.xml",
    ],
    "installable": True,
    "application": True,
}
```

---

## 4.2. `models/`

Chứa toàn bộ Python Model của module.

### `daily_report.py`

Quản lý báo cáo công việc cuối ngày.

Các thông tin chính có thể bao gồm:

* Thực tập sinh.
* Ngày báo cáo.
* Công việc đã thực hiện.
* Kết quả đạt được.
* Vấn đề gặp phải.
* Cách giải quyết.
* Task liên quan.
* Trạng thái.
* Nhận xét của quản lý.
* Điểm đánh giá.

Luồng trạng thái:

```text
Draft
  │
  ▼
Submitted
  │
  ▼
Reviewed
```

---

### `weekly_report.py`

Quản lý báo cáo tổng hợp theo tuần.

Mục đích:

* Tổng hợp công việc trong tuần.
* Tổng hợp Task đã hoàn thành.
* Tổng hợp vấn đề.
* Chuẩn bị nội dung báo cáo.
* Hỗ trợ đánh giá theo tuần.

---

### `task_presentation.py`

Quản lý lịch và nội dung thuyết trình.

Thông tin có thể bao gồm:

* Người trình bày.
* Chủ đề.
* Ngày thuyết trình.
* Task được trình bày.
* Nội dung.
* Trạng thái.
* Nhận xét.
* Điểm đánh giá.

---

### `project_project.py`

Kế thừa model:

```python
project.project
```

Mục đích là tự động thiết lập cấu trúc Kanban cho Project mới.

Ví dụ:

```text
To Do
   ↓
In Progress
   ↓
Done
```

Có thể sử dụng:

```python
@api.model_create_multi
```

để xử lý việc khởi tạo khi tạo Project.

---

# 🖥️ 5. Các tính năng chính

## 5.1. Daily Report

Thực tập sinh thực hiện báo cáo vào cuối mỗi ngày.

Một báo cáo có thể bao gồm:

| Trường          | Mô tả                  |
| --------------- | ---------------------- |
| Intern          | Người thực hiện        |
| Date            | Ngày báo cáo           |
| Work Done       | Công việc đã thực hiện |
| Result          | Kết quả                |
| Problem         | Vấn đề gặp phải        |
| Solution        | Cách giải quyết        |
| Tasks           | Task liên quan         |
| Status          | Trạng thái             |
| Manager Comment | Nhận xét               |
| Rating          | Đánh giá               |

---

## 5.2. Weekly Report

Weekly Report dùng để tổng hợp kết quả làm việc trong tuần.

Ví dụ:

```text
Tuần 1
├── Daily Report 01
├── Daily Report 02
├── Daily Report 03
├── Daily Report 04
└── Daily Report 05
```

Từ đó người quản lý có thể theo dõi:

* Tổng số ngày đã báo cáo.
* Tổng số Task.
* Task đã hoàn thành.
* Task đang thực hiện.
* Các vấn đề phát sinh.
* Nội dung đã học được.

---

## 5.3. Task Presentation

Module hỗ trợ quản lý các buổi trình bày/thuyết trình.

Quy trình:

```text
Tạo lịch
    ↓
Chuẩn bị nội dung
    ↓
Trình bày
    ↓
Manager Review
    ↓
Đánh giá
```

Lịch trình được thiết kế phù hợp với hoạt động của nhóm:

* **Thứ 3:** họp / trình bày.
* **Thứ 5:** họp / trình bày.
* **Cuối mỗi ngày:** thực tập sinh nộp Daily Report.

---

# 🔗 6. Mapping Report với Project Task

Một trong những chức năng quan trọng của module là liên kết báo cáo với Task.

Quan hệ:

```text
Daily Report
      │
      │ Many2many
      ▼
Project Task
```

Ví dụ:

```text
Daily Report: 03/09/2026

Công việc:
- Xử lý lỗi Odoo XML
- Tạo Dashboard
- Kiểm tra phân quyền

Tasks:
├── Fix XML View
├── Build Dashboard
└── Security Configuration
```

Việc mapping giúp dữ liệu báo cáo phản ánh trực tiếp công việc thực tế.

---

# 🔐 7. Phân quyền & Bảo mật

Hệ thống phân chia quyền theo vai trò.

## 7.1. Intern / User

Có quyền:

* Xem báo cáo của mình.
* Tạo báo cáo.
* Chỉnh sửa báo cáo chưa gửi.
* Gửi báo cáo.
* Xem Task được giao.
* Xem nhận xét của quản lý.

Không được:

* Xóa báo cáo đã gửi.
* Chốt điểm.
* Duyệt báo cáo của người khác.
* Thay đổi dữ liệu của người khác.

---

## 7.2. Manager / Admin

Có quyền:

* Xem báo cáo.
* Review báo cáo.
* Yêu cầu chỉnh sửa.
* Đánh giá.
* Chốt điểm.
* Quản lý Task.
* Quản lý lịch thuyết trình.
* Xem Dashboard.

---

## 7.3. Access Control

File:

```text
security/ir.model.access.csv
```

Ví dụ quyền cơ bản:

```text
Read  | Write | Create | Delete
  1   |   1   |   1    |   0
```

Đối với báo cáo, ưu tiên sử dụng **Archive / Soft Delete** thay vì xóa dữ liệu vĩnh viễn.

---

# 🔎 8. Domain Filter

Thực tập sinh chỉ nên nhìn thấy những Task được giao cho mình.

Ví dụ domain:

```python
[('user_ids', 'in', uid)]
```

Mục đích:

```text
User A
   ↓
Chỉ nhìn thấy Task của User A

User B
   ↓
Chỉ nhìn thấy Task của User B
```

Điều này giúp hạn chế việc thực tập sinh xem hoặc báo cáo dựa trên công việc của người khác.

---

# 📊 9. Dashboard

Dashboard cung cấp cái nhìn tổng quan cho người quản lý.

Các chỉ số có thể bao gồm:

```text
┌──────────────────┐
│ Tổng thực tập    │
│       15         │
└──────────────────┘

┌──────────────────┐
│ Báo cáo hôm nay  │
│       12         │
└──────────────────┘

┌──────────────────┐
│ Task hoàn thành  │
│       38         │
└──────────────────┘

┌──────────────────┐
│ Chưa nộp báo cáo │
│        3         │
└──────────────────┘
```

Dashboard hỗ trợ:

* KPI.
* Group By.
* Filter.
* Lọc theo thời gian.
* Theo dõi trạng thái.
* So sánh thực tập sinh.
* Phát hiện báo cáo chưa nộp.
* Theo dõi tiến độ Task.

---

# 🤖 10. Tự động hóa bằng Cron Job

Hệ thống sử dụng **Scheduled Action / `ir.cron`** để tự động kiểm tra báo cáo.

## Quy trình

```text
17:00 mỗi ngày
       ↓
Cron Job chạy
       ↓
Kiểm tra danh sách Intern
       ↓
Kiểm tra Daily Report
       ↓
Có báo cáo?
   ┌───┴───┐
  Có      Không
   │        │
   ▼        ▼
Tiếp tục   Gửi cảnh báo
```

Mục đích:

* Nhắc thực tập sinh chưa nộp báo cáo.
* Giảm công việc kiểm tra thủ công.
* Hạn chế tình trạng quên báo cáo.

---

# 🔔 11. Notification & Mention

Khi quản lý yêu cầu sửa báo cáo:

```text
Manager
   ↓
Request Revision
   ↓
Notification
   ↓
Intern
```

Khi báo cáo được review:

```text
Daily Report
     ↓
Manager Review
     ↓
Comment + Rating
     ↓
Intern receives notification
```

Điều này giúp người thực tập sinh biết chính xác:

* Báo cáo nào cần sửa.
* Lý do cần sửa.
* Nhận xét của quản lý.
* Kết quả đánh giá.

---

# ⚙️ 12. Batch Approve

Admin có thể duyệt nhiều bản ghi cùng lúc từ List View.

Ví dụ:

```text
☑ Report #001
☑ Report #002
☑ Report #003
☑ Report #004

        ↓

Batch Approve

        ↓

All → Reviewed
```

Chức năng này giúp giảm thời gian thao tác khi số lượng báo cáo lớn.

---

# 📅 13. Nhật ký phát triển

## Giai đoạn 1 — Cấu trúc & giao diện

Đã thực hiện:

* Khởi tạo Custom Module Odoo.
* Xây dựng cấu trúc `models`, `views`, `security`, `data`.
* Xây dựng `daily.report`.
* Xây dựng `weekly.report`.
* Xây dựng `task.presentation`.
* Thiết kế Form View.
* Thiết kế Tree/List View.
* Thiết kế Search View.
* Xây dựng Dashboard.
* Thiết lập workflow:

```text
Draft → Submitted → Reviewed
```

---

## Giai đoạn 2 — Phân quyền & bảo mật

Đã thực hiện:

* Tạo `ir.model.access.csv`.
* Tạo Security Groups.
* Phân quyền User/Admin.
* Thiết lập Domain Filter.
* Hạn chế quyền xóa.
* Áp dụng Soft Delete / Archive.
* Xử lý lỗi Access Error.

---

## Giai đoạn 3 — Tích hợp Project

Đã thực hiện:

* Kế thừa `project.project`.
* Mapping Report với Task.
* Sử dụng quan hệ `Many2many`.
* Sử dụng `mapped()` để tổng hợp Task.
* Tự động tạo Kanban Stage cho Project mới.
* Áp dụng `@api.model_create_multi`.

---

## Giai đoạn 4 — Tự động hóa

Đã thực hiện:

* Xây dựng Cron Job.
* Kiểm tra báo cáo chưa nộp.
* Gửi cảnh báo lúc 17:00.
* Xây dựng Batch Approve.
* Tự động hóa các thao tác quản trị.

---

# 🐛 14. Troubleshooting

## Lỗi 1 — "Stumbled upon some top-secret records... baked cookies"

### Hiện tượng

Thực tập sinh không thể tạo hoặc truy cập báo cáo.

### Nguyên nhân

Có thể do:

* Thiếu `ir.model.access.csv`.
* Chưa khai báo quyền cho model.
* User đang là Portal User thay vì Internal User.
* Security Group chưa được gán.

### Khắc phục

Kiểm tra:

```text
security/ir.model.access.csv
```

Đảm bảo quyền cơ bản:

```text
Read = 1
Write = 1
Create = 1
Delete = 0
```

Sau đó kiểm tra:

```text
Settings
→ Users
→ User
→ Access Rights
```

Đảm bảo tài khoản là **Internal User**.

Cuối cùng Upgrade module.

---

# ❌ 15. Lỗi mất Menu

## Hiện tượng

Menu:

* Weekly Report.
* Task Presentation.
* Daily Report.

không xuất hiện.

## Nguyên nhân

Model chưa được khai báo quyền truy cập.

Odoo có thể không hiển thị hoặc không cho truy cập model nếu thiếu Access Control.

## Khắc phục

Kiểm tra:

```text
security/ir.model.access.csv
```

Đảm bảo có quyền cho:

```text
daily.report
weekly.report
task.presentation
```

Sau đó Upgrade Module.

---

# ❌ 16. Lỗi "Manager is not set"

## Hiện tượng

Khi sử dụng Onboarding / Launch Plan, Odoo báo:

```text
Manager is not set
```

hoặc:

```text
Linked to a user
```

## Nguyên nhân

Hồ sơ Employee chưa được liên kết đầy đủ với:

* Manager.
* User đăng nhập.

## Khắc phục

### Bước 1

Vào:

```text
Settings
→ Users
→ Users
```

Tạo hoặc kiểm tra User.

### Bước 2

Vào:

```text
Employees
→ Chọn Intern
```

Thiết lập:

```text
Manager
```

### Bước 3

Trong HR Settings:

```text
Related User
```

Chọn User tương ứng.

---

# 🔒 17. Lỗi GitHub GH013 — Push Protection

## Hiện tượng

GitHub từ chối:

```text
GH013: Repository rule violations
```

Nguyên nhân có thể do GitHub phát hiện Secret/API Key trong commit.

Ví dụ:

```text
HubSpot API Token
```

được ghi trực tiếp trong file log.

---

## Cách xử lý

### Bước 1 — Xóa Secret khỏi file

Ví dụ:

```bash
sed -i '30d' logs/24-08-2026.md
```

### Bước 2 — Commit lại

```bash
git add .
git commit --amend --no-edit
```

### Bước 3 — Push lại

```bash
git push -u origin main
```

> **Lưu ý:** Nếu API Key đã từng được commit, chỉ xóa dòng trong file hiện tại chưa chắc đã loại bỏ Secret khỏi toàn bộ Git history. Với Secret thực tế, cần **revoke/rotate key** và xử lý Git history nếu cần.

---

# 🔐 18. Nguyên tắc bảo mật

Không nên hardcode API Key, Password hoặc Token trực tiếp vào source code.

Không nên:

```python
HUBSPOT_TOKEN = "pat-xxxxxxxx"
```

Nên sử dụng:

```text
Environment Variables
```

hoặc cơ chế Secret Management.

Đồng thời nên thêm các file chứa Secret vào:

```text
.gitignore
```

Ví dụ:

```gitignore
.env
*.secret
config.local.py
```

---

# 🐳 19. Triển khai với Docker

Dự án được chạy trên:

```text
WSL Ubuntu
      ↓
Docker
      ↓
Odoo 17
      ↓
odoo-app
```

---

## 19.1. Copy module vào Container

Từ WSL:

```bash
docker cp \
/home/huyduc/saigontrade-internship_2/custom_addons/intern_work_management \
odoo-app:/mnt/extra-addons/
```

---

## 19.2. Restart Odoo

```bash
docker restart odoo-app
```

Kiểm tra container:

```bash
docker ps
```

---

## 19.3. Upgrade Module

Trên giao diện Odoo:

```text
Apps
   ↓
Intern Work Management
   ↓
⋮
   ↓
Upgrade
```

Nếu module không xuất hiện:

```text
Apps
→ Update Apps List
```

Sau đó tìm lại:

```text
Intern Work Management
```

---

# 🧪 20. Quy trình cập nhật code đề xuất

Mỗi khi chỉnh sửa source code:

```text
Sửa code
   ↓
Kiểm tra Python/XML
   ↓
Copy module vào Docker
   ↓
Restart Odoo
   ↓
Update/Upgrade Module
   ↓
Kiểm tra giao diện
   ↓
Kiểm tra quyền
   ↓
Kiểm tra log
```

Các lệnh cơ bản:

```bash
docker cp \
/home/huyduc/saigontrade-internship_2/custom_addons/intern_work_management \
odoo-app:/mnt/extra-addons/

docker restart odoo-app

docker logs --tail 100 odoo-app
```

---

# 📊 21. Giá trị thực tiễn

Module không chỉ phục vụ mục đích học tập mà còn hướng tới giải quyết các vấn đề thực tế trong quá trình quản lý thực tập sinh.

## 21.1. Truy xuất dữ liệu dễ dàng

Toàn bộ công việc được lưu trên hệ thống.

Khi kết thúc kỳ thực tập, có thể:

* Filter.
* Group By.
* Export.
* Thống kê theo ngày.
* Thống kê theo tuần.
* Thống kê theo Task.

Ví dụ:

```text
Intern
   ↓
Reports
   ↓
Group By → Week
   ↓
Task Statistics
```

Điều này giúp giảm việc phải tìm kiếm lại thông tin từ:

* Zalo.
* Messenger.
* Email.
* File Excel.
* Ghi chú cá nhân.

---

# 📈 22. Hỗ trợ đánh giá thực tập sinh

Dữ liệu đánh giá được lưu trực tiếp trên hệ thống.

Có thể theo dõi:

* Số lượng Task hoàn thành.
* Số lượng báo cáo.
* Tỷ lệ nộp báo cáo.
* Điểm đánh giá.
* Nhận xét của quản lý.
* Các vấn đề thường gặp.
* Mức độ tiến bộ theo thời gian.

Từ đó có thể xây dựng cơ sở dữ liệu phục vụ đánh giá cuối kỳ.

---

# 🎓 23. Hỗ trợ báo cáo thực tập cuối khóa

Hệ thống có thể trở thành nguồn dữ liệu thực tế phục vụ báo cáo thực tập.

Ví dụ có thể sử dụng dữ liệu để thống kê:

```text
Tổng số ngày làm việc
        ↓
Tổng số báo cáo
        ↓
Tổng số Task
        ↓
Task hoàn thành
        ↓
Các vấn đề gặp phải
        ↓
Giải pháp đã thực hiện
        ↓
Kết quả đạt được
```

Các dữ liệu này có thể được sử dụng làm:

* Bảng thống kê.
* Biểu đồ.
* Phụ lục báo cáo.
* Minh chứng quá trình thực tập.
* Cơ sở đánh giá kết quả thực tập.

---

# ⏱️ 24. Tiết kiệm thời gian quản lý

Thay vì người quản lý phải kiểm tra thủ công từng thực tập sinh:

```text
Intern 1 → Báo cáo?
Intern 2 → Báo cáo?
Intern 3 → Báo cáo?
Intern 4 → Báo cáo?
...
```

Cron Job có thể tự động:

```text
17:00
  ↓
Check Reports
  ↓
Find Missing Reports
  ↓
Notify Intern
```

Dashboard giúp quản lý nhanh chóng xác định:

* Ai chưa báo cáo.
* Ai có nhiều Task.
* Ai đang bị chậm tiến độ.
* Báo cáo nào cần review.
* Task nào chưa hoàn thành.

---

# 🧩 25. Quy trình nghiệp vụ tổng thể

```text
                    INTERN
                       │
                       ▼
              ┌─────────────────┐
              │   Daily Report  │
              └────────┬────────┘
                       │
                       ▼
                  Submit Report
                       │
                       ▼
                  MANAGER REVIEW
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
          Approve             Revision
             │                   │
             │                   ▼
             │              Intern sửa
             │                   │
             │                   └──────┐
             │                          │
             ▼                          ▼
          Reviewed                  Review lại
             │
             ▼
          Rating
             │
             ▼
        Dashboard / KPI
             │
             ▼
       Weekly Summary
             │
             ▼
       Presentation
```

---

# 🚀 26. Hướng phát triển tiếp theo

Các chức năng có thể tiếp tục phát triển:

## 26.1. Dashboard nâng cao

* Biểu đồ theo ngày/tuần/tháng.
* So sánh nhiều thực tập sinh.
* Lọc theo Project.
* Lọc theo Task.
* Lọc theo khoảng thời gian tùy chọn.
* Export dữ liệu.

## 26.2. Field Mapping

Cho phép Admin ánh xạ các trường dữ liệu mà không cần sửa code.

Ví dụ:

```text
Nguồn dữ liệu
     ↓
Field Mapping
     ↓
Odoo Field
```

## 26.3. Báo cáo tự động

Có thể phát triển:

```text
Daily Summary
Weekly Summary
Monthly Summary
```

và tự động tổng hợp dữ liệu.

## 26.4. Notification nâng cao

Có thể tích hợp:

* Email.
* Odoo Discuss.
* Notification.
* Webhook.
* Các hệ thống quản lý khác.

## 26.5. Đánh giá cuối kỳ

Có thể xây dựng hệ thống Scorecard:

```text
Task Completion      30%
Daily Reports        20%
Technical Skills     20%
Presentation         15%
Problem Solving      15%
--------------------------
Total               100%
```

---

# 📝 27. Kết luận

**Intern Work Management** là một Custom Module trên Odoo 17 nhằm số hóa quy trình quản lý thực tập sinh từ lúc giao việc, thực hiện công việc, báo cáo hằng ngày, tổng hợp theo tuần cho đến thuyết trình và đánh giá.

Điểm quan trọng của hệ thống là dữ liệu công việc được liên kết trực tiếp với **Project/Task**, đồng thời kết hợp **Security, Dashboard, Notification và Cron Job** để giảm thao tác thủ công.

Hệ thống có thể tiếp tục mở rộng thành một nền tảng quản lý thực tập sinh hoàn chỉnh, phục vụ đồng thời cho:

* Thực tập sinh.
* Người hướng dẫn.
* Quản lý.
* Admin.
* Bộ phận nhân sự.

---

# 📚 28. Thông tin Repository

**Repository:**

`saigontrade-internship`

**Branch chính:**

```text
main
```

**Module:**

```text
custom_addons/intern_work_management
```

**Odoo:**

```text
Odoo 17
```

**Runtime:**

```text
Docker
```

**Development Environment:**

```text
WSL Ubuntu
```

---

# ✅ 29. Checklist triển khai

### Module

* [x] `__manifest__.py`
* [x] Models
* [x] Views
* [x] Security
* [x] Access Control
* [x] Cron Job
* [x] Project Integration
* [x] Dashboard

### Daily Workflow

* [x] Tạo Daily Report
* [x] Submit Report
* [x] Manager Review
* [x] Request Revision
* [x] Rating
* [x] Notification

### Project

* [x] Mapping Report → Task
* [x] Task Filtering
* [x] Kanban Stage
* [x] Task Statistics

### Administration

* [x] User Permission
* [x] Admin Permission
* [x] Batch Approve
* [x] Dashboard
* [x] Cron Reminder

---

## 📌 Phiên bản tài liệu

```text
Document: Intern Work Management
Version: 1.0
Platform: Odoo 17
Environment: WSL + Docker
Status: Development / Deployment
```
