# controllers/ai_chat_controller.py
from odoo import http
from odoo.http import request

class AIChatController(http.Controller):

    @http.route('/ai_budget_bot/chat', type='json', auth='user')
    def chat(self, question, chat_history=None):
        """
        Receives a question from the frontend and returns a response.
        """
        # Call your AI service/model logic
        try:
            res = request.env['ai.chat.service'].sudo().ask(question, chat_history)
            # res should be a dict like: {'type':'text','message':'...'}
            return res
        except Exception as e:
            return {'type': 'text', 'message': f"Erreur: {str(e)}"}
