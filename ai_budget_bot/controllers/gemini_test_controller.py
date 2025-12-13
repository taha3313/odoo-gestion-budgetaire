from odoo import http
from odoo.http import request
import requests
import json

class GeminiTestController(http.Controller):

    @http.route('/ai_budget_bot/gemini_test', type='json', auth='public')
    def gemini_test(self):
        api_key = request.env['ir.config_parameter'].sudo().get_param('ai.gemini.api_key')
        if not api_key:
            return {"error": "Gemini API key not configured"}

        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.5-flash:generateContent"
            "?key=" + api_key
        )

        payload = {
            "contents": [{
                "parts": [{
                    "text": "Reply exactly with: Gemini REST connection successful."
                }]
            }]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            return {
                "error": "Gemini API call failed",
                "status": response.status_code,
                "details": response.text
            }

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        return {"response": text}
