from odoo import models, fields, api

class MatchRecommendationWizard(models.TransientModel):
    _name = "match.recommendation.wizard"
    _description = "Wizard Gợi Ý Doanh Nghiệp Phù Hợp"

    partner_id = fields.Many2one("res.partner", string="Doanh nghiệp gốc", required=True)
    line_ids = fields.One2many("match.recommendation.line", "wizard_id", string="Danh sách đề xuất")

    @api.model
    def default_get(self, fields_list):
        res = super(MatchRecommendationWizard, self).default_get(fields_list)
        active_id = self.env.context.get("active_id")
        if active_id:
            res["partner_id"] = active_id
            lines = self._calculate_recommendations(active_id)
            res["line_ids"] = lines
        return res

    def _calculate_recommendations(self, source_id):
        source = self.env["res.partner"].browse(source_id)
        targets = self.env["res.partner"].search([
            ("id", "!=", source_id),
            ("name", "!=", False)
        ], limit=30)
        
        results = []
        for t in targets:
            score = 10
            reasons = ["Mạng lưới đối tác (+10)"]
            if source.country_id and t.country_id and source.country_id == t.country_id:
                score += 30
                reasons.append(f"Cùng quốc gia: {source.country_id.name} (+30)")
            if hasattr(source, "industry_id") and hasattr(t, "industry_id") and source.industry_id and source.industry_id == t.industry_id:
                score += 40
                reasons.append("Cùng ngành nghề (+40)")

            results.append((0, 0, {
                "target_partner_id": t.id,
                "country_id": t.country_id.id if t.country_id else False,
                "score": score,
                "reason": ", ".join(reasons)
            }))
        return sorted(results, key=lambda x: x[2]["score"], reverse=True)[:10]

class MatchRecommendationLine(models.TransientModel):
    _name = "match.recommendation.line"
    _description = "Chi tiết Đề xuất Đối tác"

    wizard_id = fields.Many2one("match.recommendation.wizard", ondelete="cascade")
    target_partner_id = fields.Many2one("res.partner", string="Đối tác đề xuất", readonly=True)
    country_id = fields.Many2one("res.country", string="Quốc gia", readonly=True)
    score = fields.Integer(string="Điểm phù hợp", readonly=True)
    reason = fields.Char(string="Tiêu chí khớp", readonly=True)

    def action_create_match(self):
        # Tránh kiểm tra dirty-state của form cha
        p1 = self.wizard_id.partner_id.id or self.env.context.get("active_id")
        p2 = self.target_partner_id.id
        
        match_lead = self.env["mm.lead"].sudo().create({
            "partner_id": p1,
            "partner_id_2": p2,
            "stage_id": "new"
        })
        
        return {
            "type": "ir.actions.act_window",
            "name": "B2B Match Lead",
            "res_model": "mm.lead",
            "res_id": match_lead.id,
            "view_mode": "form",
            "target": "current",
        }
