from odoo import models, fields, api

class MatchRecommendationWizard(models.TransientModel):
    _name = 'match.recommendation.wizard'
    _description = 'Wizard Gợi Ý Doanh Nghiệp Phù Hợp'

    partner_id = fields.Many2one('res.partner', string='Doanh nghiệp gốc', required=True)
    line_ids = fields.One2many('match.recommendation.line', 'wizard_id', string='Danh sách đề xuất')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['partner_id'] = active_id
            lines = self._calculate_recommendations(active_id)
            res['line_ids'] = lines
        return res

    def _calculate_recommendations(self, source_id):
        source = self.env['res.partner'].browse(source_id)
        # Chỉ quét các partner hợp lệ, khác chính nó
        targets = self.env['res.partner'].search([
            ('id', '!=', source_id),
            ('name', '!=', False)
        ], limit=30)
        
        results = []
        for t in targets:
            score = 10
            reasons = ['Mạng lưới đối tác (+10)']
            
            # Khớp quốc gia
            if source.country_id and t.country_id and source.country_id == t.country_id:
                score += 30
                reasons.append(f'Cùng quốc gia: {source.country_id.name} (+30)')
                
            # Khớp ngành nghề
            if source.industry_id and t.industry_id and source.industry_id == t.industry_id:
                score += 40
                reasons.append('Cùng ngành nghề (+40)')

            results.append((0, 0, {
                'target_partner_id': t.id,
                'country_id': t.country_id.id,
                'score': score,
                'reason': ', '.join(reasons)
            }))
            
        # Sắp xếp theo điểm giảm dần và lấy Top 10
        results = sorted(results, key=lambda x: x[2]['score'], reverse=True)[:10]
        return results

class MatchRecommendationLine(models.TransientModel):
    _name = 'match.recommendation.line'
    _description = 'Chi tiết Đề xuất Đối tác'

    wizard_id = fields.Many2one('match.recommendation.wizard', ondelete='cascade')
    target_partner_id = fields.Many2one('res.partner', string='Đối tác đề xuất', readonly=True)
    country_id = fields.Many2one('res.country', string='Quốc gia', readonly=True)
    score = fields.Integer(string='Điểm phù hợp', readonly=True)
    reason = fields.Char(string='Tiêu chí khớp', readonly=True)

    def action_create_match(self):
        """Bấm nút tạo ngay bản ghi Match Making kết nối giữa 2 công ty"""
        self.ensure_one()
        match_lead = self.env['mm.lead'].create({
            'partner_id': self.wizard_id.partner_id.id,
            'partner_id_2': self.target_partner_id.id,
            'stage_id': 'new'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'B2B Match Lead',
            'res_model': 'mm.lead',
            'res_id': match_lead.id,
            'view_mode': 'form',
            'target': 'current',
        }
