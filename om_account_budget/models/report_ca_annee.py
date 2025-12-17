from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class ReportCAAnneeWizard(models.TransientModel):
    _name = 'report.ca.annee'
    _description = 'Chiffre d’Affaires Annuel Wizard'

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

    def generate_report(self):
        if int(self.start_year) > int(self.end_year):
            raise ValidationError("L'année de début doit être inférieure ou égale à l'année de fin.")

        self.env['report.ca.annee.result'].search([('user_id', '=', self.env.uid)]).unlink()

        BudgetLine = self.env['crossovered.budget.lines']
        years = range(int(self.start_year), int(self.end_year) + 1)

        for year in years:
            date_from = f'{year}-01-01'
            date_to = f'{year}-12-31'

            domain_ca = [
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
                ('crossovered_budget_id.type_budget', '=', 'revenue'),
                # ('crossovered_budget_id.state', '=', 'done'),
            ]
            lines_ca = BudgetLine.search(domain_ca)
            total_real_ca = sum(line.montant_realise or 0.0 for line in lines_ca)
            total_prev_ca = sum(line.montant_prev or 0.0 for line in lines_ca)

            self.env['report.ca.annee.result'].create({
                'annee': str(year),
                'montant_real': total_real_ca,
                'montant_prev': total_prev_ca,
                'user_id': self.env.uid,
            })

        return {
            'name': 'Chiffre d’Affaires Annuel',
            'view_mode': 'graph,tree',
            'res_model': 'report.ca.annee.result',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('user_id', '=', self.env.uid)],
            'context': {'group_by': 'annee'},
        }
