from odoo import models

class AIUIRouter(models.AbstractModel):
    _name = 'ai.ui.router'
    _description = 'Decides UI behavior from intent'

    def route(self, intent):
        """
        Decide how the UI should react.
        """
        action = intent.get("action")

        # Later: charts, dashboards, reports
        if action in ("compare",):
            return "text"

        if action in ("sum", "list", "top"):
            return "text"

        return "text"
