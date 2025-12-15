from odoo import models, fields, api
from datetime import date


class PieChartDepenseLine(models.Model):
    _name = 'pie.chart.depense.line'
    _description = 'Ligne pour graphique en camembert des dépenses'

    annee = fields.Char(string='Année', default=lambda self: str(date.today().year))
    type_depense = fields.Selection([
        ('dette', 'Dette'),
        ('fonctionnement', 'Fonctionnement'),
        ('investissement', 'Investissement'),
    ], string='Type de Dépense', required=True)
    montant = fields.Float(string='Montant')
    percentage = fields.Float(
        string='Pourcentage (%)',
        compute='_compute_percentage',
        store=True,
        digits=(5, 2)
    )
    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        default=lambda self: self.env.uid,
        index=True
    )

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
                ('crossovered_budget_id.state', '=', 'done'),

            ]
            lines = BudgetLine.search(domain)
            total = sum(abs(line.montant_realise or 0.0) for line in lines)

            if total > 0:
                self.create({
                    'annee': year,
                    'type_depense': type_dep,
                    'montant': total,
                    'user_id': self.env.uid,
                })


class PieChartDepenseLineWizard(models.TransientModel):
    _name = 'pie.chart.depense.line.wizard'
    _description = 'Wizard pour générer les données du camembert des dépenses'

    def _get_year_selection(self):
        current_year = date.today().year
        return [(str(y), str(y)) for y in range(current_year - 20, current_year + 1)]

    year = fields.Selection(
        selection=_get_year_selection,
        string="Année",
        required=True,
        default=lambda self: str(date.today().year)
    )

    def action_generate(self):
        """Generate pie chart lines for selected year"""
        self.env['pie.chart.depense.line'].generate_lines_for_year(year=self.year)

        return {
            'type': 'ir.actions.act_window',
            'name': f"Camembert Dépenses {self.year}",
            'res_model': 'pie.chart.depense.line',
            'view_mode': 'graph,tree',
            'target': 'current',
            'domain': [('user_id', '=', self.env.uid), ('annee', '=', self.year)],
        }