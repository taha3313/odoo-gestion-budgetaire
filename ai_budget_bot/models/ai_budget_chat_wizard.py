from odoo import models, fields

class AIBudgetChatWizard(models.TransientModel):
    _name = "ai.budget.chat.wizard"

    question = fields.Text(required=True)
    answer = fields.Text(readonly=True)

    def action_ask(self):
        self.answer = self.env['ai.chat.service'].ask(self.question)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
