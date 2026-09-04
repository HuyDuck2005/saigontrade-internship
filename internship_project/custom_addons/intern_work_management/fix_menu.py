import io

file_path = 'views/menu_views.xml'
with io.open(file_path, 'w', encoding='utf-8') as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="menu_intern_work_root" name="Intern Work" sequence="10" web_icon="project,static/description/icon.png"/>
    
    <menuitem id="menu_intern_dashboard" name="Tổng Quan (KPI)" parent="menu_intern_work_root" action="action_intern_dashboard" sequence="5"/>
    
    <menuitem id="menu_intern_reports" name="Báo Cáo" parent="menu_intern_work_root" sequence="10"/>
    <menuitem id="menu_daily_report" name="Báo Cáo Ngày" parent="menu_intern_reports" action="action_daily_report" sequence="10"/>
    <menuitem id="menu_weekly_report" name="Báo Cáo Tuần" parent="menu_intern_reports" action="action_weekly_report" sequence="20"/>

    <menuitem id="menu_intern_reviews" name="Thuyết Trình" parent="menu_intern_work_root" sequence="20"/>
    <menuitem id="menu_task_presentation" name="Lịch Thuyết Trình" parent="menu_intern_reviews" action="action_task_presentation" sequence="10"/>

    <!-- Bảng Đánh Giá -->
    <menuitem id="menu_intern_assessment_main" name="Đánh Giá Năng Lực" parent="menu_intern_work_root" sequence="20"/>
    <menuitem id="menu_intern_assessment_campaign" name="Chiến dịch Đánh giá" parent="menu_intern_assessment_main" action="action_intern_assessment_campaign" sequence="1"/>
    <menuitem id="menu_intern_assessment_dashboard" name="Dashboard Tổng Hợp" parent="menu_intern_assessment_main" action="action_intern_assessment_dashboard" sequence="2"/>
    <menuitem id="menu_evaluation_rubric" name="Bảng Tiêu Chí" parent="menu_intern_assessment_main" action="action_evaluation_rubric" sequence="3"/>
</odoo>
""")