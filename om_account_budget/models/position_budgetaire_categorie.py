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
    categorie_position_line = fields.One2many('categorie.position.lines', 'categorie_position_id', 'Lignes de catégorie')


class PositionBudgetaireCategorieline(models.Model):
    _name = 'categorie.position.lines'
    _description = 'Lignes de catégorie de Position Budgétaire'
    name = fields.Char(compute='_compute_line_name')
    categorie_position_id = fields.Many2one('position.budgetaire.categorie', 'Categorie', ondelete='cascade', index=True,
                                           required=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Situation budgétaire')


    def _compute_line_name(self):
        for rec in self:
            # just in case someone opens the budget line in form view
            computed_name = rec.crossovered_budget_id.name
            if rec.general_budget_id:
                computed_name += ' - ' + rec.general_budget_id.name

            rec.name = computed_name
