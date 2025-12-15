from odoo import models, api

class BudgetResponseGenerator(models.AbstractModel):
    _name = "ai.budget.response"
    _description = "Generate human-readable responses"

    @api.model
    def generate_response(self, instruction, data):
        action = instruction.get("action")
        budget_type = instruction.get("type", "any")
        year = instruction.get("year")
        year_compare = instruction.get("year_compare")
        limit = instruction.get("limit")

        r = []

        if action == "sum":
            r.append(f"📊 Dépenses '{budget_type}' pour {year} :")
            r.append(f"- Montant prévu : {data.get('montant_prev', 0):,.2f}")
            r.append(f"- Montant réalisé : {data.get('montant_real', 0):,.2f}")
            pct = data.get("pourcentage_realisation")
            if pct is not None:
                r.append(f"- Taux de réalisation : {pct:.2f} %")

        elif action == "list":
            r.append(f"📋 Lignes budgétaires '{budget_type}' pour {year} :")
            for l in data.get("lines", []):
                r.append(
                    f"- {l.get('position_budgetaire') or 'Non défini'} "
                    f"(Budget: {l.get('budget')}): "
                    f"Prévu={l.get('montant_prev', 0):,.2f}, "
                    f"Réalisé={l.get('montant_realise', 0):,.2f}"
                )

        elif action == "compare":
            r.append(
                f"📈 Comparaison '{budget_type}' {year} vs {year_compare}:"
            )
            r.append(
                f"- {year}: "
                f"Prévu={data.get('montant_prev_1', 0):,.2f}, "
                f"Réalisé={data.get('montant_real_1', 0):,.2f}"
            )
            r.append(
                f"- {year_compare}: "
                f"Prévu={data.get('montant_prev_2', 0):,.2f}, "
                f"Réalisé={data.get('montant_real_2', 0):,.2f}"
            )

        elif action == "top":
            r.append(
                f"🏆 Top {limit or len(data.get('top_lines', []))} "
                f"postes '{budget_type}' pour {year}:"
            )
            for i, l in enumerate(data.get("top_lines", []), 1):
                r.append(
                    f"{i}. {l.get('position_budgetaire') or 'Non défini'} "
                    f"(Budget: {l.get('budget')}): "
                    f"Prévu={l.get('montant_prev', 0):,.2f}, "
                    f"Réalisé={l.get('montant_realise', 0):,.2f}"
                )

        else:
            r.append("Action non supportée.")

        return "\n".join(r)
