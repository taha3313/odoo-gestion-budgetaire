from odoo import models, api

class BudgetChatbot(models.AbstractModel):
    _name = "ai.budget.chatbot"
    _description = "Budget Assistant Chatbot"

    @api.model
    def chat(self, question):
        """
        Main entry point for developers.
        Returns:
        {
            "instruction": {...},  # Gemini parsed JSON
            "data": {...},         # Executor result (sum/list/compare/top)
            "response": "..."      # Human-readable text
        }
        """
        # 1. Get structured intent from Gemini
        intent_processor = self.env["ai.intent.processor"]
        instruction = intent_processor.interpret(question)

        # 2. Execute the intent against the database
        executor = self.env["ai.budget.executor"]
        data = executor.execute(instruction)

        # 3. Generate a readable response
        response_generator = self.env["ai.budget.response"]
        readable_response = response_generator.generate_response(instruction, data)

        return {
            "instruction": instruction,
            "data": data,
            "response": readable_response,
        }
