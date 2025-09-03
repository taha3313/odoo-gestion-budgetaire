odoo.define("custom_pivot_hide_total.PivotModelHideTotal", function(require) {
    "use strict";

    const PivotModel = require("web.PivotModel");

    const PivotModelHideTotal = PivotModel.extend({
        /**
         * Override _getValues to remove total rows
         */
        _getValues: function() {
            const result = this._super.apply(this, arguments);

            if (result.rows && result.rows.length) {
                // Remove the last row if it is a total row
                const lastRow = result.rows[result.rows.length - 1];
                if (lastRow?.is_total) {
                    result.rows.pop();
                    console.log("Removed total row from pivot data");
                }
            }

            return result;
        },
    });

    return PivotModelHideTotal;
});
