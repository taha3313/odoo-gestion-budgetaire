from odoo import models, fields, api

class BudgetQueryEngine(models.AbstractModel):
    _name = "ai.budget.query.engine"
    _description = "Safe Budget Query Engine"

    def run(self, intent):
        Budget = self.env['crossovered.budget.lines']
        domain = []

        # Filter by type via the related budget post
        if intent.get('type') != 'any':
            domain.append(('general_budget_id.type', '=', intent['type']))

        # Filter by year
        if intent.get('year'):
            domain += [
                ('date_from', '>=', f"{intent['year']}-01-01"),
                ('date_to', '<=', f"{intent['year']}-12-31")
            ]

        records = Budget.search(domain)

        action = intent.get('action')
        if action == 'sum':
            return {
                'total': sum(r.planned_amount for r in records),
                'count': len(records)
            }

        elif action == 'top':
            sorted_records = sorted(records, key=lambda r: r.planned_amount, reverse=True)
            limit = intent.get('limit') or 5
            return [
                {'name': r.name, 'amount': r.planned_amount} 
                for r in sorted_records[:limit]
            ]

        elif action == 'compare':
            if not intent.get('year_compare'):
                raise ValueError("year_compare is required for compare action")
            return self._compare_years(intent)

        elif action == 'list':
            return [{'name': r.name, 'amount': r.planned_amount} for r in records]

        else:
            raise ValueError(f"Unknown action: {action}")

    def _compare_years(self, intent):
        Budget = self.env['crossovered.budget.lines']

        def total_for_year(year):
            recs = Budget.search([
                ('date_from', '>=', f"{year}-01-01"),
                ('date_to', '<=', f"{year}-12-31")
            ])
            return sum(r.planned_amount for r in recs)

        return {
            'year_1': intent['year'],
            'year_2': intent['year_compare'],
            'total_1': total_for_year(intent['year']),
            'total_2': total_for_year(intent['year_compare']),
        }
