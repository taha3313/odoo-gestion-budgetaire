from odoo import models, fields, api
from datetime import date


class PieChartDepenseLine(models.Model):
    _name = 'pie.chart.depense.line'

    annee = fields.Char(string='Année', default=lambda self: str(date.today().year))
    type_depense = fields.Selection([
        ('dette', 'Dette'),
        ('fonctionnement', 'Fonctionnement'),
        ('investissement', 'Investissement'),
    ], string='Type de Dépense', required=True)
    montant = fields.Float(string='Montant')
    percentage = fields.Float(string='Pourcentage (%)', compute='_compute_percentage', store=True, digits=(5, 2))
    user_id = fields.Many2one('res.users', string='Utilisateur',
                              default=lambda self: self.env.uid,
                              index=True)

    @api.depends('montant', 'annee', 'user_id')
    def _compute_percentage(self):
        for record in self:
            total = sum(self.search([
                ('annee', '=', record.annee),
                ('user_id', '=', record.user_id.id)
            ]).mapped('montant'))
            record.percentage = (record.montant / total * 100) if total else 0.0

    @api.model
    def generate_lines_for_year(self, year=None):
        year = year or str(date.today().year)

        # Only unlink for current user + year
        self.search([
            ('annee', '=', year),
            ('user_id', '=', self.env.uid)
        ]).unlink()

        BudgetLine = self.env['crossovered.budget.lines']
        date_from = f'{year}-01-01'
        date_to = f'{year}-12-31'

        for type_dep in ['dette', 'fonctionnement', 'investissement']:
            domain = [
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
                ('crossovered_budget_id.type_budget', '=', type_dep),
            ]
            lines = BudgetLine.search(domain)
            total = sum(abs(line.montant_realise or 0.0) for line in lines)

            if total > 0:
                self.create({
                    'annee': year,
                    'type_depense': type_dep,
                    'montant': total,
                    'user_id': self.env.uid,  # link to current user
                })

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        year = str(date.today().year)
        self.generate_lines_for_year(year)
        return super(PieChartDepenseLine, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
