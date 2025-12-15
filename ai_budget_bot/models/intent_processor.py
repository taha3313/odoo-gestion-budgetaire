from odoo import models
import requests
import json
import re

class IntentProcessor(models.AbstractModel):
    _name = "ai.intent.processor"
    _description = "Gemini Intent Processor"

    def _get_gemini_api_key(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'ai.gemini.api_key'
        )

    def interpret(self, question):
        api_key = self._get_gemini_api_key()
        if not api_key:
            raise ValueError("Gemini API key not configured")

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-2.5-flash:generateContent"
            f"?key={api_key}"
        )

        prompt = f"""
You are a budget assistant.
Convert the question into STRICT JSON only.

Question: "{question}"

JSON schema:
{{
  "action": "sum | list | compare | top",
  "type": "fonctionnement | investissement | dette | revenue | any",
  "year": number | null,
  "year_compare": number | null,
  "limit": number | null
}}
"""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=15
        )

        if response.status_code != 200:
            raise ValueError(f"Gemini error: {response.text}")

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        match = re.search(r"\{[\s\S]*\}", raw_text)
        if not match:
            raise ValueError("Gemini did not return valid JSON")

        return json.loads(match.group())