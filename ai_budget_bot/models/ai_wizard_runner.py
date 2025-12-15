from odoo import models

class AIWizardRunner(models.AbstractModel):
    _name = "ai.wizard.runner"
    _description = "Executes report wizards for AI"

    def run_depense_annuelle(self, intent):
        """
        intent contains:
        - year
        - year_compare (optional)
        """

        # Determine years
        if intent.get("year_compare"):
            start_year = min(intent["year"], intent["year_compare"])
            end_year = max(intent["year"], intent["year_compare"])
        else:
            start_year = end_year = intent["year"]

        # Create wizard
        wizard = self.env['report.depense.annuelle'].create({
            'start_year': str(start_year),
            'end_year': str(end_year),
        })

        # Execute wizard → this POPULATES result table
        return wizard.generate_report()
