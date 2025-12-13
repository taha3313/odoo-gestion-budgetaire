from odoo import models, fields, api
from datetime import date


class BarChartBudgetLine(models.Model):
    _name = 'bar.chart.budget.line'
    _description = 'Ligne pour graphique à barres du budget'

    annee = fields.Char(string='Année', required=True)
    type_depense = fields.Selection([
        ('dette', 'Dette'),
        ('fonctionnement', 'Fonctionnement'),
        ('investissement', 'Investissement'),
    ], string='Type de Dépense', required=True)
    montant = fields.Float(string='Montant')
    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        default=lambda self: self.env.uid,
        index=True
    )

    @api.model
    def generate_lines_for_year(self, year):
        # Delete old lines for this year & user
        self.search([
            ('annee', '=', year),
            ('user_id', '=', self.env.uid)
        ]).unlink()

        BudgetLine = self.env['crossovered.budget.lines']
        date_from = f'{year}-01-01'
        date_to = f'{year}-12-31'

        for type_dep in ['fonctionnement', 'investissement', 'dette']:
            domain = [
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
                ('crossovered_budget_id.type_budget', '=', type_dep),
                ('crossovered_budget_id.state', '=', 'done'),
            ]
            lines = BudgetLine.search(domain)
            total = sum(abs(line.montant_prev or 0.0) for line in lines)

            if total > 0:
                self.create({
                    'annee': year,
                    'type_depense': type_dep,
                    'montant': total,
                    'user_id': self.env.uid,
                })

    @api.model
    def generate_all_years_data(self, start=2020, end=None):
        end = end or date.today().year
        # Delete current user’s data
        self.search([('user_id', '=', self.env.uid)]).unlink()
        for year in range(int(start), int(end) + 1):
            self.generate_lines_for_year(str(year))


class BarChartBudgetLineWizard(models.TransientModel):  # wizard
    _name = 'bar.chart.budget.line.wizard'
    _description = 'Wizard pour générer les données du graphique du budget'
    
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
    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        default=lambda self: self.env.uid,
        index=True
    )

    def action_generate(self):
        """Called when user clicks 'Generate' in wizard"""
        start = int(self.start_year)
        end = int(self.end_year)

        if start > end:
            raise ValueError("L'année de début doit être inférieure ou égale à l'année de fin.")

        self.env['bar.chart.budget.line'].generate_all_years_data(start=start, end=end)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget Prévu',
            'res_model': 'bar.chart.budget.line',
            'view_mode': 'graph',
            'target': 'current',
            'domain': [('user_id', '=', self.env.uid)],
        }