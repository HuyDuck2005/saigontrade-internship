import io

file_path = 'views/daily_report_views.xml'
with io.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<field name="completed_task_ids" widget="many2many_tags" readonly="state != \'draft\'" domain="[(\'user_ids\', \'in\', [uid])]"/>',
    '<field name="completed_task_ids" widget="many2many_tags" readonly="state != \'draft\'"/>'
)
content = content.replace(
    '<field name="in_progress_task_ids" widget="many2many_tags" readonly="state != \'draft\'" domain="[(\'user_ids\', \'in\', [uid])]"/>',
    '<field name="in_progress_task_ids" widget="many2many_tags" readonly="state != \'draft\'"/>'
)

with io.open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

file_path2 = 'views/menu_views.xml'
with io.open(file_path2, 'r', encoding='utf-8') as f:
    content2 = f.read()

content2 = content2.replace('parent="menu_intern_work_root"', 'parent="menu_intern_work_management_root"')

with io.open(file_path2, 'w', encoding='utf-8') as f:
    f.write(content2)