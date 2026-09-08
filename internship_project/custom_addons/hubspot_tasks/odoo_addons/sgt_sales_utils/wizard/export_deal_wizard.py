from odoo import models, fields, api
import io
import base64
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

class ExportDealWizard(models.TransientModel):
    _name = 'export.deal.wizard'
    _description = 'Wizard Export Deal XLSX'

    file_data = fields.Binary('File Data', readonly=True)
    file_name = fields.Char('File Name', readonly=True)

    def action_export_xlsx(self):
        if not xlsxwriter:
            raise models.ValidationError("Thư viện xlsxwriter chưa được cài đặt.")
            
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Deals Pipeline')

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#D3D3D3', 'align': 'center', 'border': 1
        })
        currency_format = workbook.add_format({'num_format': '#,##0 "VND"', 'border': 1})
        default_format = workbook.add_format({'border': 1})

        headers = ['Deal ID', 'Tên Deal', 'Khách hàng', 'Doanh thu (VND)', 'Trạng thái']
        for col, head in enumerate(headers):
            sheet.write(0, col, head, header_format)
            sheet.set_column(col, col, 20)

        active_ids = self.env.context.get('active_ids', [])
        deals = self.env['crm.lead'].browse(active_ids) if active_ids else self.env['crm.lead'].search([])

        row = 1
        total_revenue = 0
        for deal in deals:
            sheet.write(row, 0, deal.id, default_format)
            sheet.write(row, 1, deal.name, default_format)
            sheet.write(row, 2, deal.partner_id.name or '', default_format)
            sheet.write(row, 3, deal.expected_revenue, currency_format)
            sheet.write(row, 4, deal.stage_id.name or 'New', default_format)
            total_revenue += deal.expected_revenue
            row += 1

        sheet.write(row, 2, 'Tổng cộng', header_format)
        sheet.write(row, 3, total_revenue, currency_format)

        workbook.close()
        output.seek(0)
        
        self.write({
            'file_data': base64.b64encode(output.read()),
            'file_name': 'Pipeline_Export.xlsx'
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'export.deal.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
