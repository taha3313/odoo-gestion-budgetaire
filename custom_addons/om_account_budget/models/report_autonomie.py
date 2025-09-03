# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class ReportAutonomie(models.Model):
    _name = 'report.autonomie'
    _description = 'Rapport Autonomie (N-2, N-1, N, N+1)'

    name = fields.Char(string="Ligne")
    realisation_n_2 = fields.Float()
    realisation_n_1 = fields.Float()
    realisation_n = fields.Float()
    prevision_n_plus_1 = fields.Float()
    user_id = fields.Many2one('res.users', string="Utilisateur", default=lambda self: self.env.uid)

    # Champs techniques
    categorie_id = fields.Many2one('position.budgetaire.categorie', string="Catégorie")
    position_id = fields.Many2one('account.budget.post', string="Position")

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Renommer dynamiquement les colonnes selon l'année choisie dans le wizard"""
        res = super().fields_get(allfields, attributes)
        context_year = self._context.get('year_n') or date.today().year
        if 'realisation_n_2' in res:
            res['realisation_n_2']['string'] = f"Réalisation {context_year - 2}"
        if 'realisation_n_1' in res:
            res['realisation_n_1']['string'] = f"Réalisation {context_year - 1}"
        if 'realisation_n' in res:
            res['realisation_n']['string'] = f"Réalisation {context_year}"
        if 'prevision_n_plus_1' in res:
            res['prevision_n_plus_1']['string'] = f"Prévision {context_year + 1}"
        return res

    @api.model
    def generate_summary(self, year_n=None, categories=None, selected_positions=None, mode='exclude_categ'):
        """Génération du rapport selon le wizard"""
        if not year_n:
            year_n = date.today().year
        year_n = int(year_n)

        _logger.info(f"Génération du rapport autonomie pour l'année N={year_n}")

        # Supprimer anciennes lignes de l'utilisateur
        self.search([('user_id', '=', self.env.uid)]).unlink()

        if mode == 'exclude_categ':
            categories = self.env['position.budgetaire.categorie'].browse(categories)
        if mode == 'exclude_positions':
            selected_positions = self.env['account.budget.post'].browse(selected_positions)

        BudgetLine = self.env['crossovered.budget.lines']

        def get_total(year, budget_type=None, position_domain=None, prev=False):
            domain = [
                ('date_from', '<=', f"{year}-12-31"),
                ('date_to', '>=', f"{year}-01-01"),
            ]
            if budget_type:
                domain.append(('crossovered_budget_id.type_budget', '=', budget_type))
            if position_domain:
                domain.append(position_domain)
            lines = BudgetLine.search(domain)
            return sum(abs(line.montant_prev if prev else line.montant_realise or 0.0) for line in lines)

        def safe_ratio(ca, frais):
            return (ca / frais * 100.0) if frais else None

        # Frais fonctionnement global
        frais_n_2 = get_total(year_n - 2, budget_type='fonctionnement')
        frais_n_1 = get_total(year_n - 1, budget_type='fonctionnement')
        frais_n = get_total(year_n, budget_type='fonctionnement')
        frais_n_plus_1 = get_total(year_n + 1, budget_type='fonctionnement', prev=True)

        # === Catégories ===
        if mode == 'exclude_categ' and categories:
            for cat in categories:
                cat_positions = self.env['account.budget.post'].search([('categorie_id', '=', cat.id)])
                pos_domain = ('general_budget_id', 'not in', cat_positions.ids)

                n_2 = get_total(year_n - 2, budget_type='revenue', position_domain=pos_domain)
                n_1 = get_total(year_n - 1, budget_type='revenue', position_domain=pos_domain)
                n = get_total(year_n, budget_type='revenue', position_domain=pos_domain)
                n_plus_1_prev = get_total(year_n + 1, budget_type='revenue', position_domain=pos_domain, prev=True)

                self.create({
                    'name': f"CA hors {cat.name}",
                    'realisation_n_2': n_2,
                    'realisation_n_1': n_1,
                    'realisation_n': n,
                    'prevision_n_plus_1': n_plus_1_prev,
                    'categorie_id': cat.id,
                })
                self.create({
                    'name': f"Ratio CA hors {cat.name}/frais fonctionnement",
                    'realisation_n_2': safe_ratio(n_2, frais_n_2),
                    'realisation_n_1': safe_ratio(n_1, frais_n_1),
                    'realisation_n': safe_ratio(n, frais_n),
                    'prevision_n_plus_1': safe_ratio(n_plus_1_prev, frais_n_plus_1),
                    'categorie_id': cat.id,
                })

        # === Positions sélectionnées ===
        if mode == 'exclude_positions' and selected_positions:
            for pos in selected_positions:
                pos_domain_excl = ('general_budget_id', '!=', pos.id)

                n_2_hors = get_total(year_n - 2, budget_type='revenue', position_domain=pos_domain_excl)
                n_1_hors = get_total(year_n - 1, budget_type='revenue', position_domain=pos_domain_excl)
                n_hors = get_total(year_n, budget_type='revenue', position_domain=pos_domain_excl)
                n_plus_1_hors = get_total(year_n + 1, budget_type='revenue', position_domain=pos_domain_excl, prev=True)

                self.create({
                    'name': f"CA hors {pos.name}",
                    'realisation_n_2': n_2_hors,
                    'realisation_n_1': n_1_hors,
                    'realisation_n': n_hors,
                    'prevision_n_plus_1': n_plus_1_hors,
                    'position_id': pos.id,
                })
                self.create({
                    'name': f"Ratio CA hors {pos.name}/frais fonctionnement",
                    'realisation_n_2': safe_ratio(n_2_hors, frais_n_2),
                    'realisation_n_1': safe_ratio(n_1_hors, frais_n_1),
                    'realisation_n': safe_ratio(n_hors, frais_n),
                    'prevision_n_plus_1': safe_ratio(n_plus_1_hors, frais_n_plus_1),
                    'position_id': pos.id,
                })


