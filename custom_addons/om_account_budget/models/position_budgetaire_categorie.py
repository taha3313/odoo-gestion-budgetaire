from odoo import models, fields

class PositionBudgetaireCategorie(models.Model):
    _name = 'position.budgetaire.categorie'
    _description = 'Catégorie de Position Budgétaire'

    name = fields.Char(string='Nom', required=True)
    user_id = fields.Many2one('res.users', string='Utilisateur', index=True)
    
    position_ids = fields.One2many(
        'account.budget.post',
        'categorie_id',
        string="Positions budgétaires"
    )