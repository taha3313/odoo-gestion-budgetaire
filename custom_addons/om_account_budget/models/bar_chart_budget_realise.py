from odoo import models, fields, api
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class BarChartBudgetRealise(models.Model):
    _name = 'bar.chart.budget.realise'
    _description = 'Ligne pour graphique à barres des réalisations budgétaires'

    annee = fields.Char(string='Année', required=True)
    type_depense = fields.Selection([
        ('dette', 'Dette'),
        ('fonctionnement', 'Fonctionnement'),
        ('investissement', 'Investissement'),
    ], string='Type de Dépense', required=True)
    montant_realise = fields.Float(string='Montant Réalisé')
    user_id = fields.Many2one('res.users', string='Utilisateur',
                              default=lambda self: self.env.uid,
                              index=True)

    @api.model
    def generate_lines_for_year(self, year):
        _logger.info(f"[BarChartRealise] Regenerating lines for year: {year} (user {self.env.uid})")

        # Only unlink for current user + year
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
            ]
            lines = BudgetLine.search(domain)
            total_realise = sum(abs(line.montant_realise or 0.0) for line in lines)

            if total_realise > 0:
                self.create({
                    'annee': year,
                    'type_depense': type_dep,
                    'montant_realise': total_realise,
                    'user_id': self.env.uid,  # assign to current user
                })

    @api.model
    def generate_all_years_data(self, start=2020, end=None):
        end = end or date.today().year

        # Only delete current user's data
        self.search([('user_id', '=', self.env.uid)]).unlink()

        for year in range(start, end + 1):
            self.generate_lines_for_year(str(year))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        current_year = date.today().year
        self.generate_all_years_data(start=current_year - 4, end=current_year)
        return super(BarChartBudgetRealise, self).fields_view_get(view_id, view_type, toolbar, submenu)
