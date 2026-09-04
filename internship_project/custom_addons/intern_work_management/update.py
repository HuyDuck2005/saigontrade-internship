import io

file_path = 'views/daily_report_views.xml'
with io.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<field name="completed_task_ids" widget="many2many_tags" readonly="state != \'draft\'"/>',
    '<field name="completed_task_ids" widget="many2many_tags" readonly="state != \'draft\'" domain="[(\'user_ids\', \'in\', [uid])]"/>'
)
content = content.replace(
    '<field name="in_progress_task_ids" widget="many2many_tags" readonly="state != \'draft\'"/>',
    '<field name="in_progress_task_ids" widget="many2many_tags" readonly="state != \'draft\'" domain="[(\'user_ids\', \'in\', [uid])]"/>'
)

with io.open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)