from odoo import models, fields, api

class ReportPositionBudgetaireResult(models.Model):
    _name = 'report.position.budgetaire.result'
    _description = 'Résultat Position Budgétaire'

    annee = fields.Char(string='Année', index=True)
    position_budgetaire = fields.Many2one('account.budget.post', string='Position Budgétaire', index=True)
    montant_real = fields.Float(string='Montant Réalisé')
    montant_prev = fields.Float(string='Montant Prévisionnel')
    user_id = fields.Many2one('res.users', string='Utilisateur', index=True)

    pourcentage_realisation = fields.Float(
        string='Réalisation (%)',
        compute='_compute_pourcentage_realisation',
        group_operator="avg",
        store=True,
        readonly=True
    )

    @api.depends('montant_real', 'montant_prev')
    def _compute_pourcentage_realisation(self):
        for record in self:
            if (record.montant_prev):
                record.pourcentage_realisation = (record.montant_real / record.montant_prev) * 100
            else:
                record.pourcentage_realisation = None