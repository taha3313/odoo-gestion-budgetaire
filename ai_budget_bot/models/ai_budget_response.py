from odoo import models, api

class BudgetResponseGenerator(models.AbstractModel):
    _name = "ai.budget.response"
    _description = "Generate human-readable responses for budget queries"

    @api.model
    def generate_response(self, instruction, data):
        """
        instruction: dict returned from Gemini (action, type, year, etc.)
        data: dict or list returned from executor.execute
        """
        action = instruction.get("action")
        budget_type = instruction.get("type", "any")
        year = instruction.get("year")
        year_compare = instruction.get("year_compare")
        limit = instruction.get("limit")

        response_lines = []

        # SUM action
        if action == "sum":
            total_real = data.get("total_real")
            total_prev = data.get("total_prev")
            response_lines.append(
                f"Budget type '{budget_type}' for year {year}:\n"
                f" - Total Realized: {total_real}\n"
                f" - Total Planned: {total_prev}"
            )

        # LIST action
        elif action == "list":
            response_lines.append(f"Listing budget lines for type '{budget_type}' in year {year}:")
            for line in data:
                response_lines.append(f" - {line['name']}: Real={line['montant_real']}, Planned={line['montant_prev']}")

        # COMPARE action
        elif action == "compare":
            response_lines.append(
                f"Comparison for budget type '{budget_type}':\n"
                f"Year {year} vs Year {year_compare}"
            )
            for key, value in data.items():
                response_lines.append(f" - {key}: {value}")

        # TOP action
        elif action == "top":
            response_lines.append(f"Top {limit} budget lines for '{budget_type}' in year {year}:")
            for i, line in enumerate(data[:limit], 1):
                response_lines.append(f"{i}. {line['name']}: Real={line['montant_real']}, Planned={line['montant_prev']}")

        else:
            response_lines.append("No valid action returned from Gemini.")

        return "\n".join(response_lines)
