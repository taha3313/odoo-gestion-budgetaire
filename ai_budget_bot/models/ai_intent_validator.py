from odoo import models
from datetime import date

class IntentValidator(models.AbstractModel):
    _name = "ai.intent.validator"
    _description = "Validate and normalize AI intent"

    def validate(self, intent):
        current_year = date.today().year

        action = intent.get("action")
        if action not in ("sum", "list", "compare", "top"):
            raise ValueError("Unsupported action")

        intent.setdefault("type", "any")

        if intent.get("year") is None:
            intent["year"] = current_year

        if action == "compare":
            if not intent.get("year_compare"):
                raise ValueError("year_compare is required for comparison")

        if action == "top":
            intent["limit"] = min(int(intent.get("limit") or 5), 20)

        return intent
