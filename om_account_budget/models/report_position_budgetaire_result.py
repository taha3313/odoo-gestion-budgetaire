from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ReportPositionBudgetaireResult(models.Model):
    _name = 'report.position.budgetaire.result'
    _description = 'Résultat Position Budgétaire'

    annee = fields.Char(string='Année', index=True)
    position_budgetaire = fields.Many2one('account.budget.post', string='Position Budgétaire', index=True)
    montant_real = fields.Float(string='Montant Réalisé',digits=dp.get_precision('Account'))
    montant_prev = fields.Float(string='Montant Prévisionnel',digits=dp.get_precision('Account'))
    user_id = fields.Many2one('res.users', string='Utilisateur', index=True)

    pourcentage_realisation = fields.Float(
        string='Réalisation (%)',
        group_operator="avg",
        store=True,
        readonly=True, digits=dp.get_precision('Account')
    )