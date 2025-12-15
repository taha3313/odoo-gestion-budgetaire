from odoo import models

class AIChatService(models.AbstractModel):
    _name = "ai.chat.service"
    _description = "Main Chatbot Service"

    def ask(self, question, chat_history=None):
        # chat_history can be used here to provide context to the AI model
        try:
            # 1. NLP → structured intent
            intent = self.env['ai.intent.processor'].interpret(question)

            # 2. Decide UI behavior
            route = self.env['ai.ui.router'].route(intent)

            # 3. Execute logic
            if route == "report":
                # Check if it's a pivot view report
                if intent and intent.get('action_type') == 'pivot_view':
                    # This is a placeholder for generating an actual pivot view action
                    # In a real scenario, intent would contain details like model, domain, group_by, etc.
                    pivot_action = {
                        'type': 'ir.actions.act_window',
                        'name': 'Budget Pivot Analysis',
                        'res_model': 'account.budget.post', # Example model, replace with actual
                        'view_mode': 'pivot',
                        'views': [[False, 'pivot']],
                        'target': 'current',
                        # Add domain, group_by, etc. based on intent
                        # 'domain': intent.get('domain', []),
                        # 'context': intent.get('context', {}),
                    }
                    return {
                        "type": "action",
                        "message": "📊 Affichage du tableau croisé dynamique.",
                        "action": pivot_action
                    }
                else:
                    action = self.env['ai.report.runner'].run(intent)
                    return {
                        "type": "action",
                        "message": "📊 Rapport généré avec succès.",
                        "action": action
                    }

            data = self.env['ai.budget.executor'].execute(intent)
            text = self.env['ai.budget.response'].generate_response(intent, data)

            return {
                "type": "text",
                "message": text
            }
        
    

        except Exception as e:
            return {
                "type": "text",
                "message": f"❌ Erreur: {str(e)}"
            }
    
