odoo.define('om_account_budget.graph_export_pdf', function (require) {
    'use strict';

    const GraphRenderer = require('web.GraphRenderer');
    const ajax = require('web.ajax');

    console.log("graph_export_pdf.js loaded!");

    // 📦 Preload jsPDF only (html2canvas is no longer needed)
    const libsReady = ajax.loadJS('/om_account_budget/static/src/js/jspdf.umd.min.js')
        .then(() => console.log("✅ jsPDF preloaded!"));

    GraphRenderer.include({

        _render: function () {
            return this._super.apply(this, arguments).then(() => {
                console.log("Graph view rendered!");

                if (this._pdfButtonAdded) return;

                const observer = new MutationObserver((mutations, obs) => {
                    const $downloadContainer = $('.o_cp_buttons');
                    if ($downloadContainer.length) {
                        const $pdfButton = $('<button type="button" class="btn btn-secondary o_graph_button">')
                            .text("PDF")
                            .on('click', this._onDownloadGraphPDF.bind(this));

                        $downloadContainer.append($pdfButton);
                        this._pdfButtonAdded = true;
                        console.log("✅ PDF button added to graph!");

                        obs.disconnect();
                    }
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            });
        },

        _onDownloadGraphPDF: function () {
            const graphContainer = document.querySelector('.o_graph_canvas_container');

            if (!graphContainer) {
                alert("Graphique introuvable.");
                return;
            }

            // Show spinner
            const $spinner = $('<div class="o_pdf_spinner">Téléchargement PDF...</div>').css({
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                padding: '1rem 2rem',
                background: '#444',
                color: 'white',
                borderRadius: '8px',
                zIndex: 10000,
                fontSize: '16px',
            });
            $('body').append($spinner);

            libsReady.then(() => {
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF('landscape', 'pt', 'a4');

                const pageWidth = pdf.internal.pageSize.getWidth();
                const pageHeight = pdf.internal.pageSize.getHeight();

                const today = new Date();
                const formattedDate = today.toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                pdf.setFontSize(18);
                pdf.text("Graphique Budgétaire", pageWidth / 2, 30, { align: "center" });
                pdf.setFontSize(12);
                pdf.text(`Date : ${formattedDate}`, pageWidth / 2, 50, { align: "center" });

                // ✅ Direct Chart.js export
                if (this.chart && typeof this.chart.toBase64Image === 'function') {
                    console.log("📊 Using Chart.js direct export");
                    const imgData = this.chart.toBase64Image();
                    this._addImageToPDF(pdf, imgData, pageWidth, pageHeight);
                    $spinner.remove();
                } else {
                    console.error("❌ Chart.js instance not found. Export not possible.");
                    $spinner.remove();
                    alert("Export PDF impossible : graphique non-Chart.js.");
                }
            });
        },

        _addImageToPDF: function (pdf, imgData, pageWidth, pageHeight) {
            const imgProps = pdf.getImageProperties(imgData);
            const ratio = Math.min(pageWidth * 0.95 / imgProps.width, (pageHeight - 100) / imgProps.height);
            const imgWidth = imgProps.width * ratio;
            const imgHeight = imgProps.height * ratio;
            const x = (pageWidth - imgWidth) / 2;
            const y = 80;

            pdf.addImage(imgData, 'PNG', x, y, imgWidth, imgHeight);
            pdf.save('graphique_depenses.pdf');
        }

    });
});
