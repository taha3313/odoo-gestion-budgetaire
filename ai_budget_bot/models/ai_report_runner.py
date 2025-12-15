from odoo import models, api

class AIReportRunner(models.AbstractModel):
    _name = "ai.report.runner"
    _description = "Generate Odoo UI actions from AI intent"

    @api.model
    def _domain_for_year_and_type(self, year, dep_type):
        domain = [
            ('date_from', '<=', f'{year}-12-31'),
            ('date_to', '>=', f'{year}-01-01'),
        ]
        if dep_type and dep_type != 'any':
            domain.append(
                ('crossovered_budget_id.type_budget', '=', dep_type)
            )
        return domain

    @api.model
    def run(self, intent):
        """
        Returns an Odoo action dict.
        """
        action = intent.get("action")
        year = intent.get("year")
        dep_type = intent.get("type", "any")
        limit = intent.get("limit")

        if not year:
            raise ValueError("Year is required to open a report")

        domain = self._domain_for_year_and_type(year, dep_type)

        # --------------------------
        # LIST → tree/form view
        # --------------------------
        if action == "list":
            return {
                "type": "ir.actions.act_window",
                "name": f"Lignes budgétaires {dep_type} ({year})",
                "res_model": "crossovered.budget.lines",
                "view_mode": "tree,form",
                "domain": domain,
                "context": {
                    "search_default_groupby_budget": 1,
                }
            }

        # --------------------------
        # TOP → ordered tree view
        # --------------------------
        if action == "top":
            return {
                "type": "ir.actions.act_window",
                "name": f"Top postes budgétaires {dep_type} ({year})",
                "res_model": "crossovered.budget.lines",
                "view_mode": "tree,form",
                "domain": domain,
                "context": {
                    "search_default_order_montant_prev": 1,
                },
                "limit": limit or 10,
            }

        # --------------------------
        # SUM / COMPARE → no UI report
        # --------------------------
        raise ValueError(
            f"No report view defined for action '{action}'"
        )
