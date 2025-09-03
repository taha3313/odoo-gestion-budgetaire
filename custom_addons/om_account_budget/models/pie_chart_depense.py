from odoo import models, fields, api
from datetime import date

class PieChartDepense(models.Model):
    _name = 'pie.chart.depense'
    _description = 'Répartition des dépenses par type de budget (camembert)'

    annee = fields.Char(
        string='Année',
        index=True,
        default=lambda self: str(date.today().year)
    )

    budget_total = fields.Float(string='Budget Total', compute='_compute_totaux', store=True)
    montant_dette = fields.Float(string='Montant Dette', compute='_compute_totaux', store=True)
    montant_fonctionnement = fields.Float(string='Montant Fonctionnement', compute='_compute_totaux', store=True)
    montant_investissement = fields.Float(string='Montant Investissement', compute='_compute_totaux', store=True)

    @api.depends('annee')
    def _compute_totaux(self):
        BudgetLine = self.env['crossovered.budget.lines']
        for record in self:
            date_from = f'{record.annee}-01-01'
            date_to = f'{record.annee}-12-31'

            # Domaine commun
            base_domain = [
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
            ]

            # Dette
            lines_dette = BudgetLine.search(base_domain + [('crossovered_budget_id.type_budget', '=', 'dette')])
            montant_dette = sum(line.montant_realise or 0.0 for line in lines_dette)

            # Fonctionnement
            lines_fct = BudgetLine.search(base_domain + [('crossovered_budget_id.type_budget', '=', 'fonctionnement')])
            montant_fonctionnement = sum(line.montant_realise or 0.0 for line in lines_fct)

            # Investissement
            lines_inv = BudgetLine.search(base_domain + [('crossovered_budget_id.type_budget', '=', 'investissement')])
            montant_investissement = sum(line.montant_realise or 0.0 for line in lines_inv)

            # Affectation des valeurs
            record.montant_dette = montant_dette
            record.montant_fonctionnement = montant_fonctionnement
            record.montant_investissement = montant_investissement
            record.budget_total = montant_dette + montant_fonctionnement + montant_investissement
