from odoo import models, api
import requests
import json
import re

class IntentProcessor(models.AbstractModel):
    _name = "ai.intent.processor"
    _description = "Gemini Intent Processor with Budget Executor"

    def _get_gemini_api_key(self):
        return self.env['ir.config_parameter'].sudo().get_param('ai.gemini.api_key')

    def interpret(self, question):
        """
        1. Send question to Gemini
        2. Receive strict JSON response
        3. Return parsed JSON
        """
        api_key = self._get_gemini_api_key()
        if not api_key:
            raise ValueError("Gemini API key not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        prompt = f"""
You are a budget assistant. Convert the following question into STRICT JSON.
Only output JSON. Do NOT include explanations.

Question: "{question}"

JSON schema:
{{
  "action": "sum | list | compare | top",
  "type": "fonctionnement | investissement | dette | any",
  "year": number | null,
  "year_compare": number | null,
  "limit": number | null
}}
"""
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            raise ValueError(f"Gemini call failed: {response.text}")

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError(f"Gemini returned no JSON: {text}")

        return json.loads(match.group())

    @api.model
    def ask(self, question):
        """
        High-level entry point: interprets question and fetches data.
        """
        instruction = self.interpret(question)
        executor = self.env['ai.budget.executor']
        result = executor.execute(instruction)
        return result
