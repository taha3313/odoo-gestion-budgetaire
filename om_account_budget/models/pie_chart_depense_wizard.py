from odoo import models

class PieChartWizard(models.TransientModel):
    _name = 'pie.chart.depense.wizard'
    _description = 'Wizard to regenerate Pie Chart Data'

    def generate(self):
        self.env['pie.chart.depense.line'].generate_lines_for_year()
