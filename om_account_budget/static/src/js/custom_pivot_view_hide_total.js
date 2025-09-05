odoo.define("custom_pivot_hide_total.PivotViewHideTotal", function(require) {
    "use strict";

    console.log("Loading custom pivot view to hide total row");

    const PivotView = require("web.PivotView");
    const PivotModelHideTotal = require("custom_pivot_hide_total.PivotModelHideTotal");
    const viewRegistry = require("web.view_registry");

    const PivotViewHideTotal = PivotView.extend({
        config: _.extend({}, PivotView.prototype.config, {
            Model: PivotModelHideTotal,
        }),
    });

    viewRegistry.add("custom_pivot_hide_total", PivotViewHideTotal);
});
