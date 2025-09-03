odoo.define('om_account_budget.pivot_export_pdf', function (require) {
    'use strict';

    const PivotRenderer = require('web.PivotRenderer');
    const ajax = require('web.ajax');

    PivotRenderer.include({


            _renderTable: function () {
            const table = this._super.apply(this, arguments);

            // Find all elements responsible for the expand/collapse behavior
            // and remove their event listeners and visual indicators.
            table.find('th.o_pivot_header_cell').off('click');
            table.find('th.o_pivot_header_cell > .fa-caret-right, th.o_pivot_header_cell > .fa-caret-down').hide();
            return table;
        },

        _render: function () {
            return this._super.apply(this, arguments).then(() => {
                if (this._pdfButtonAdded) return;

                const observer = new MutationObserver((mutations, obs) => {
                    const $downloadContainer = $('.o_pivot_download');
                    if ($downloadContainer.length) {
                        const $pdfButton = $('<button type="button" class="btn btn-secondary ml-2">')
                            .text("PDF")
                            .on('click', this._onDownloadPDF.bind(this));
                        $downloadContainer.parent().append($pdfButton);
                        this._pdfButtonAdded = true;
                        obs.disconnect();
                    }
                });

                observer.observe(document.body, { childList: true, subtree: true });
            });
        },


        _onDownloadPDF: function () {
            ajax.loadJS('/om_account_budget/static/src/js/jspdf.umd.min.js').then(() => {
                return ajax.loadJS('/om_account_budget/static/src/js/jspdf.plugin.autotable.js');
            }).then(() => {
                const jsPDF = window.jspdf.jsPDF;
                const pdf = new jsPDF('landscape', 'pt', 'a4');

                const rowHeaderCount = this.$el.find('tbody tr:first th').length;

                // ---- BUILD HEADERS ----
                const head = [];
                const headerRows = this.$el.find('thead tr');
                headerRows.each(function () {
                    const row = [];

                    for (let i = 0; i < rowHeaderCount; i++) {
                        row.push('');
                    }

                    $(this).find('th').each(function (index) {
                        let text = $(this).text().trim() || '';
                        const colspan = parseInt($(this).attr('colspan')) || 1;

                        if (headerRows.index($(this).closest('tr')) === 0 && index === rowHeaderCount && text.toLowerCase() === 'total') {
                            text = '';
                        }

                        row.push(text);
                        for (let i = 1; i < colspan; i++) {
                            row.push('');
                        }
                    });

                    head.push(row);
                });

                // ---- BUILD BODY ----
                const body = [];
                this.$el.find('tbody tr').each(function () {
                    const row = [];

                    $(this).find('th').each(function () {
                        row.push({
                            content: $(this).text().trim() || '',
                            styles: { fontStyle: 'bold', fillColor: [240, 240, 240] }
                        });
                    });

                    $(this).find('td').each(function () {
                        row.push($(this).text().trim() || '');
                    });

                    body.push(row);
                });

                const colCount = body[0].length;
                head.forEach(row => {
                    while (row.length < colCount) {
                        row.push('');
                    }
                });

                // ---- Generate PDF ----
                pdf.autoTable({
                    head: head,
                    body: body,
                    startY: 50,
                    theme: 'grid',
                    margin: { left: 20, right: 20 },
                    styles: {
                        fontSize: 9,
                        cellPadding: 4,
                        valign: 'middle',
                        overflow: 'linebreak'
                    },
                    headStyles: {
                        fillColor: [41, 128, 185],
                        textColor: 255,
                        halign: 'center'
                    },
                    showHead: 'everyPage',
                    pageBreak: 'auto',
                    didParseCell: function (data) {
                        // Add subtle alternating background per group column
                        if (data.section === 'head') {
                            const colIndex = data.column.index;
                            if (colIndex >= rowHeaderCount) {
                                const groupIndex = Math.floor((colIndex - rowHeaderCount) / 2);
                                data.cell.styles.fillColor = (groupIndex % 2 === 0) ? [52, 152, 219] : [41, 128, 185];
                            }
                        }
                    }
                });

                pdf.save('pivot_report.pdf');
            }).catch(err => {
                console.error('Erreur lors du téléchargement du PDF', err);
                alert('Erreur: Vérifiez que jsPDF et AutoTable sont bien chargées.');
            });
        }

    });
});
