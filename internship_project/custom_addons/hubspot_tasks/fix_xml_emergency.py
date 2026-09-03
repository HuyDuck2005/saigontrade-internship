import os

xml_content = """<?xml version="1.0"?>
<odoo>
    <record id="view_crm_lead_form_inherit_sync" model="ir.ui.view">
        <name>crm.lead.form.inherit.sync</name>
        <model>crm.lead</model>
        <inherit_id ref="crm.crm_lead_view_form"/>
        <arch type="xml">
            <xpath expr="//header" position="inside">
                <button name="action_create_contact_both" string="Tạo Contact Odoo1 &amp; Odoo2" type="object" class="oe_highlight btn-primary"/>
                <button name="action_retry_sync" string="Thử lại đồng bộ (Retry)" type="object" class="btn-secondary" invisible="sync_status != 'failed'"/>
            </xpath>
            <xpath expr="//notebook" position="inside">
                <page string="Trạng thái Sync Odoo 2" name="sync_odoo2_page">
                    <group>
                        <group string="Thông tin đồng bộ">
                            <field name="sync_status" widget="badge" decoration-success="sync_status == 'success'" decoration-danger="sync_status == 'failed'" decoration-muted="sync_status == 'draft'"/>
                            <field name="remote_partner_id" readonly="1"/>
                            <field name="remote_lead_id" readonly="1"/>
                            <field name="retry_count" readonly="1"/>
                        </group>
                        <group string="Chi tiết lỗi">
                            <field name="sync_error_msg" readonly="1"/>
                        </group>
                    </group>
                </page>
            </xpath>
        </arch>
    </record>
</odoo>
"""

# Xóa file cũ nếu có để tránh lỗi ghi đè
path = os.path.expanduser("~/projects/hubspot_tasks/odoo_addons/sgt_odoo_sync/views/crm_lead_views.xml")
if os.path.exists(path):
    os.remove(path)

# Ghi file mới chuẩn xác
with open(path, "w", encoding="utf-8") as f:
    f.write(xml_content.strip())
print("✅ Đã ghi đè file XML chuẩn Odoo 17!")
