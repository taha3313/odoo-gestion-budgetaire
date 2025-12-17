from odoo import models, fields, api
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class ReportChiffreAffaire(models.Model):
    _name = 'report.chiffre.affaire'
    _description = "Rapport Chiffre d'Affaire"

    position_budgetaire = fields.Many2one('account.budget.post', string='Position Budgétaire', index=True)
    type_depense = fields.Char(string="Type Dépense")
    montant_facture = fields.Float(string='Montant facturé')
    montant_prev = fields.Float(string='Montant Prévisionnel')
    montant_encaisse = fields.Float(string='Montant Encaissé')
    montant_realise_pred = fields.Float(string='Montant Réalisé (année précédente)')
    user_id = fields.Many2one('res.users', string='Utilisateur', index=True)

    # Pourcentages
    pourcentage_evolution = fields.Float(
        string='Évolution (%)',
        compute='_compute_pourcentages',
        group_operator="avg",
        store=True,
        readonly=True,
    )
    pourcentage_encaisse_prev = fields.Float(
        string='Encaissé / Prévisionnel (%)',
        compute='_compute_pourcentages',
        group_operator="avg",
        store=True,
        readonly=True,
    )
    pourcentage_encaisse_facture = fields.Float(
        string='Encaissé / Facturé (%)',
        compute='_compute_pourcentages',
        group_operator="avg",
        store=True,
        readonly=True,
    )

    @api.depends('montant_prev', 'montant_encaisse', 'montant_facture', 'montant_realise_pred')
    def _compute_pourcentages(self):
        for record in self:
            record.pourcentage_evolution = (
                (record.montant_realise_pred / record.montant_prev) * 100
                if (record.montant_prev and record.montant_realise_pred) else None
            )
            record.pourcentage_encaisse_prev = (
                (record.montant_encaisse / record.montant_prev) * 100
                if (record.montant_prev and record.montant_encaisse) else None
            )
            record.pourcentage_encaisse_facture = (
                (record.montant_encaisse / record.montant_facture) * 100
                if (record.montant_facture and record.montant_encaisse) else None
            )

    @api.model
    def generate_lines(self, year=None):
        """Génère les lignes pour une année donnée (ou l'année courante par défaut)."""
        year = str(year or date.today().year)
        year_pred = str(int(year) - 1)
        position_ids = self.env['account.budget.post'].search([]).ids

        # Supprimer les lignes de l'utilisateur courant
        self.search([('user_id', '=', self.env.uid)]).unlink()

        BudgetLine = self.env['crossovered.budget.lines']
        date_from = f'{year}-01-01'
        date_to = f'{year}-12-31'
        date_from_pred = f'{year_pred}-01-01'
        date_to_pred = f'{year_pred}-12-31'

        for position_id in position_ids:
            domain = [
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
                ('crossovered_budget_id.type_budget', '=', 'revenue'),
                # ('crossovered_budget_id.state', '=', 'done'),
                ('general_budget_id', '=', position_id),
            ]
            domain_pred = [
                ('date_from', '<=', date_to_pred),
                ('date_to', '>=', date_from_pred),
                ('crossovered_budget_id.type_budget', '=', 'revenue'),
                ('general_budget_id', '=', position_id),
            ]

            lines = BudgetLine.search(domain)
            total_realise = sum(abs(line.montant_realise or 0.0) for line in lines)
            total_prev = sum(abs(line.montant_prev or 0.0) for line in lines)
            total_encaisse = sum(abs(line.montant_pratique_paiement or 0.0) for line in lines)

            lines_pred = BudgetLine.search(domain_pred)
            total_realise_pred = sum(abs(line.montant_realise or 0.0) for line in lines_pred)

            self.create({
                'position_budgetaire': position_id,
                'type_depense': 'revenue',
                'montant_facture': total_realise,
                'montant_prev': total_prev,
                'montant_encaisse': total_encaisse,
                'montant_realise_pred': total_realise_pred,
                'user_id': self.env.uid,
            })

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Change dynamiquement les labels des champs en ajoutant l'année"""
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        current_year = date.today().year
        last_year = current_year - 1

        field_labels = {
            'montant_facture': f"Montant Facturé {current_year}",
            'montant_prev': f"Montant Prévisionnel {current_year}",
            'montant_encaisse': f"Montant Encaissé {current_year}",
            'montant_realise_pred': f"Montant Réalisé {last_year}",
        }

        for field, label in field_labels.items():
            if field in res['fields']:
                res['fields'][field]['string'] = label

        return res

class ReportChiffreAffaireWizard(models.TransientModel):
    _name = "report.chiffre.affaire.wizard"
    _description = "Wizard pour générer le rapport chiffre d'affaire"

    year = fields.Selection(
        selection=[(str(y), str(y)) for y in range(date.today().year - 20, date.today().year + 1)],
        string="Année",
        required=True,
        default=lambda self: str(date.today().year)
    )

    def action_generate(self):
        """Bouton de génération"""
        self.ensure_one()
        _logger.info(f"Génération du rapport chiffre d'affaire via wizard pour {self.year}")
        self.env["report.chiffre.affaire"].generate_lines(self.year)
        return {
            "type": "ir.actions.act_window",
            "name": "Rapport Chiffre d'Affaire",
            "res_model": "report.chiffre.affaire",
            "view_mode": "pivot,tree",
            "domain": [("user_id", "=", self.env.uid)],
            "target": "current",
        }
