from odoo import models, fields, api
from datetime import date

class ReportAutonomieWizard(models.TransientModel):
    _name = "report.autonomie.wizard"
    _description = "Assistant Rapport Autonomie"



    def _get_year_selection(self):
        current_year = date.today().year
        return [(str(y), str(y)) for y in range(current_year - 20, current_year + 1)]

    year_n = fields.Selection(
        string="Année N",
        selection=_get_year_selection,
        required=True,
        default=lambda self: str(date.today().year)
    )

    mode = fields.Selection([
        ('exclude_categ', "Exclure une ou plusieurs catégories"),
        ('exclude_positions', "Positions spécifiques"),
    ], string="Mode de génération", required=True, default="exclude_categ")

    categorie_ids = fields.Many2many(
        'position.budgetaire.categorie',
        string="Catégories à exclure"
    )

    position_ids = fields.Many2many(
        'account.budget.post',
        string="Positions à traiter"
    )

    select_all = fields.Boolean(
        string="Sélectionner tout",
        help="Cocher pour inclure toutes les positions budgétaires"
    )


    @api.onchange('select_all', 'mode')
    def _onchange_select_all(self):
        if self.mode == 'exclude_positions' and self.select_all:
            self.position_ids = self.env['account.budget.post'].search([])
        else:
            self.position_ids = [(5, 0, 0)]
        if self.mode == 'exclude_categ' and self.select_all:
            self.categorie_ids = self.env['position.budgetaire.categorie'].search([])
        else:
            self.categorie_ids = [(5, 0, 0)]

    def action_generate(self):
        """Générer le rapport et rediriger vers la vue pivot/tree"""
        self.ensure_one()
        Report = self.env['report.autonomie']
        Report.with_context(year_n=self.year_n).generate_summary(
            year_n=self.year_n,
            categories=self.categorie_ids.ids if self.categorie_ids else None,
            selected_positions=self.position_ids.ids if self.position_ids else None,
            mode=self.mode,
        )
        return {
            'name': "Rapport Autonomie",
            'type': 'ir.actions.act_window',
            'res_model': 'report.autonomie',
            'view_mode': 'pivot,tree',
            'target': 'current',
            'domain': [('user_id', '=', self.env.uid)],
            'context': {'year_n': int(self.year_n)},
        }