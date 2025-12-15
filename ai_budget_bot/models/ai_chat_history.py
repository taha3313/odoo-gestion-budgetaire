# models/ai_chat_history.py
from odoo import models, fields

class AIChatHistory(models.Model):
    _name = 'ai.chat.history'
    _description = 'AI Chat History'

    user_id = fields.Many2one('res.users', string="User")
    message = fields.Text(string="Message")
    sender = fields.Selection([('user','User'),('bot','Bot')])
