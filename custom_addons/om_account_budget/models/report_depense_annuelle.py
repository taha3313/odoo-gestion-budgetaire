from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class ReportDepenseAnnuelleWizard(models.TransientModel):
    _name = 'report.depense.annuelle'
    _description = 'Dépenses Annuelles Wizard'

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

        # Clear previous user data
        self.env['report.depense.annuelle.result'].search([('user_id', '=', self.env.uid)]).unlink()

        BudgetLine = self.env['crossovered.budget.lines']
        years = range(int(self.start_year), int(self.end_year) + 1)
        types_depense = ['fonctionnement', 'investissement', 'dette']

        for year in years:
            date_from = f'{year}-01-01'
            date_to = f'{year}-12-31'
            for dep_type in types_depense:
                domain = [
                    ('date_from', '<=', date_to),
                    ('date_to', '>=', date_from),
                    ('crossovered_budget_id.type_budget', '=', dep_type),
                ]
                lines = BudgetLine.search(domain)
                total_real = sum(line.montant_realise or 0.0 for line in lines)
                total_prev = sum(line.montant_prev or 0.0 for line in lines)

                self.env['report.depense.annuelle.result'].create({
                    'annee': str(year),
                    'type_depense': dep_type,
                    'montant_real': total_real,
                    'montant_prev': total_prev,
                    'user_id': self.env.uid,
                })

        return {
            'name': 'Rapport Dépenses Annuelles',
            'view_mode': 'pivot,tree',
            'res_model': 'report.depense.annuelle.result',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('user_id', '=', self.env.uid)],
            'context': {'group_by': 'annee'},
        }
