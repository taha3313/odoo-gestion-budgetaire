odoo.define('ai_budget_bot.ai_budget_chat_widget', function(require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session'); // Added for session.uid

    var AIChat = AbstractAction.extend({ // Renamed from AIChatWidget to AIChat for consistency with user's provided code
        // No QWeb needed, as HTML is generated directly
        template: false, // Explicitly set to false as per user's instruction

        // User's provided start function
        start: function() {
            var html = `
                <div class="o_ai_chat_widget" style="width:400px; border:1px solid #ccc; border-radius:10px; padding:10px; font-family:sans-serif;">
                    <h3 style="text-align:center; margin-bottom:10px;">💬 AI Budget Chatbot</h3>
                    <div id="chat_messages" style="height:350px; overflow-y:auto; padding:10px; background:#f9f9f9; border-radius:5px; margin-bottom:5px;"></div>
                    <div style="display:flex;">
                        <input type="text" id="chat_input" placeholder="Posez votre question..." style="flex:1; padding:5px; border-radius:5px; border:1px solid #ccc;" />
                        <button id="chat_send" style="margin-left:5px; padding:5px 10px; border-radius:5px; border:none; background:#007bff; color:white; cursor:pointer;">Envoyer</button>
                    </div>
                </div>
            `;
            this.$el.html(html);

            var self = this;

            // Send on button click
            this.$('#chat_send').on('click', function(){
                self.sendMessage();
            });

            // Send on Enter key
            this.$('#chat_input').on('keypress', function(e){
                if(e.which === 13) self.sendMessage();
            });

            // Initialize history array
            this.chatHistory = [];
        },

        // User's provided sendMessage function
        sendMessage: function(){
            var question = this.$('#chat_input').val().trim();
            if (!question) return;

            this.addMessage("Vous", question);
            this.chatHistory.push({sender:"Vous", message: question});
            this.$('#chat_input').val('');
            this.askController(question);
        },

        // User's provided addMessage function
        addMessage: function(sender, msg){
            var $messages = this.$('#chat_messages');
            var color = sender === "Bot" ? "#007bff" : "#333";
            var align = sender === "Bot" ? "left" : "right";

            $messages.append(`<div style="text-align:${align}; margin-bottom:5px;">
                <strong style="color:${color};">${sender}:</strong> ${msg}
            </div>`);

            $messages.scrollTop($messages[0].scrollHeight);
        },

        // User's provided askController function with loading indicator and history saving
        askController: function(question){
            var self = this;
            var $messages = this.$('#chat_messages');
            var loading = $('<div id="loading" style="color:gray;">Bot is typing...</div>');
            $messages.append(loading);
            $messages.scrollTop($messages[0].scrollHeight);

            this._rpc({
                route: '/ai_budget_bot/chat',
                params: {question: question, chat_history: this.chatHistory},
            }).then(function(result){
                $('#loading').remove();
                if (result.message) {
                    self.addMessage("Bot", result.message);
                    self.chatHistory.push({sender:"Bot", message: result.message});
                }
                if (result.action) {
                    self.do_action(result.action);
                }

                // Optional: save history (only save bot message if there was one)
                if (result.message) {
                    self._rpc({
                        model: 'ai.chat.history',
                        method: 'create',
                        args: [{
                            user_id: session.uid,
                            message: result.message,
                            sender: 'bot'
                        }]
                    });
                }
            }).catch(function(err){
                $('#loading').remove();
                self.addMessage("Bot", "Erreur: " + (err.data ? err.data.message : err.message));
            });
        }
    });

    core.action_registry.add('ai_budget_chat_widget', AIChat); // Ensure widget name matches
    return AIChat;
});