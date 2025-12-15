odoo.define('restore_pivot_buttons.PivotFix', function(require) {
    "use strict";

    var PivotController = require('web.PivotController');
    var PivotView = require('web.PivotView');

    // Restaurer le bouton Mesure dans la PivotView
    PivotView.include({
        render_buttons: function($node) {
            this._super($node);
            if (this.$buttons) {
                this.$buttons.find('.o_pivot_measure').show(); // Mesure
            }
        },
    });

    // Restaurer le bouton Export PDF dans la PivotController
    PivotController.include({
        renderButtons: function($node) {
            this._super($node);
            if (this.$buttons) {
                // Affiche tous les boutons export
                this.$buttons.find('.o_pivot_download').show();

                // Vérifie si un rapport PDF existe pour ce modèle
                var model = this.modelName;
                var self = this;
                this._rpc({
                    model: 'ir.actions.report',
                    method: 'search_count',
                    args: [[['model', '=', model]]],
                }).then(function(count){
                    if (count === 0) {
                        // Pas de rapport, cacher le bouton
                        self.$buttons.find('.o_pivot_download').hide();
                    }
                });
            }
        },
    });
});