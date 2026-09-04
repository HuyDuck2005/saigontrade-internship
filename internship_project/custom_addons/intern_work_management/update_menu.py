import io

file_path = 'views/menu_views.xml'
with io.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('parent="menu_intern_work_management_root"', 'parent="menu_intern_work_root"')

with io.open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)