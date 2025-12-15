from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class ReportPositionBudgetaireWizard(models.TransientModel):
    _name = 'report.position.budgetaire'
    _description = 'Position Budgetaire Wizard'

    def _get_year_selection(self):
        current_year = date.today().year
        return [(str(y), str(y)) for y in range(current_year - 20, current_year + 1)]

    start_year = fields.Selection(
        selection=_get_year_selection,
        string='Année début',
        required=True,
        default=lambda self: str(date.today().year - 3)
    )

    end_year = fields.Selection(
        selection=_get_year_selection,
        string='Année fin',
        required=True,
        default=lambda self: str(date.today().year)
    )

    select_all = fields.Boolean(
        string="Sélectionner tout",
        help="Cocher pour inclure toutes les positions budgétaires"
    )

    positions_budgetaires_ids = fields.Many2many(
        'account.budget.post',
        string="Positions Budgétaires"
    )

    @api.onchange('select_all')
    def _onchange_select_all(self):
        """Select or unselect all positions when 'Select All' checkbox is toggled."""
        if self.select_all:
            self.positions_budgetaires_ids = self.env['account.budget.post'].search([])
        else:
            self.positions_budgetaires_ids = [(5, 0, 0)]

    def generate_report(self):
        if int(self.start_year) > int(self.end_year):
            raise ValidationError("L'année de début doit être inférieure ou égale à l'année de fin.")

        # Clear previous results
        self.env['report.position.budgetaire.result'].search([('user_id', '=', self.env.uid)]).unlink()

        BudgetLine = self.env['crossovered.budget.lines']
        years = range(int(self.start_year), int(self.end_year) + 1)

        # If "select all" or no manual selection, include all
        if self.select_all or not self.positions_budgetaires_ids:
            position_ids = self.env['account.budget.post'].search([]).ids
        else:
            position_ids = self.positions_budgetaires_ids.ids

        for year in years:
            date_from = f'{year}-01-01'
            date_to = f'{year}-12-31'
            for position_id in position_ids:
                domain = [
                    ('date_from', '<=', date_to),
                    ('date_to', '>=', date_from),
                    ('general_budget_id', '=', position_id),
                    ('crossovered_budget_id.state', '=', 'done'),
                ]
                lines = BudgetLine.search(domain)

                total_real = sum(line.montant_realise or 0.0 for line in lines)
                total_prev = sum(line.montant_prev or 0.0 for line in lines)

                if abs(total_prev) > 0:
                    pourcentage_realisation = (total_real / total_prev) * 100
                    self.env['report.position.budgetaire.result'].create({
                        'annee': str(year),
                        'position_budgetaire': position_id,
                        'montant_real': total_real,
                        'montant_prev': total_prev,
                        'pourcentage_realisation': pourcentage_realisation,
                        'user_id': self.env.uid,
                    })
                else:
                    self.env['report.position.budgetaire.result'].create({
                        'annee': str(year),
                        'position_budgetaire': position_id,
                        'montant_real': total_real,
                        'montant_prev': total_prev,
                        'user_id': self.env.uid,
                    })
  

        return {
            'name': 'Rapport Position Budgetaire',
            'view_mode': 'pivot,tree',
            'res_model': 'report.position.budgetaire.result',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('user_id', '=', self.env.uid)],
            'context': {'group_by': 'annee'},
        }
