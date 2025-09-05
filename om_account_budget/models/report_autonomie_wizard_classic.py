import base64
import csv
import io
from datetime import date

from odoo import api, fields, models
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm


class ReportAutonomieWizardClassic(models.TransientModel):
    _name = "report.autonomie.wizard.classic"
    _description = "Assistant Rapport Autonomie Classic"

    def _get_year_selection(self):
        current_year = date.today().year
        return [(str(y), str(y)) for y in range(current_year - 20, current_year + 1)]

    year_n = fields.Selection(
        string="Année N",
        selection=_get_year_selection,
        required=True,
        default=lambda self: str(date.today().year)
    )

    mode = fields.Selection([
        ('exclude_categ', "Exclure une ou plusieurs catégories"),
        ('exclude_positions', "Positions spécifiques"),
    ], string="Mode de génération", required=True, default="exclude_categ")

    categorie_ids = fields.Many2many(
        'position.budgetaire.categorie',
        'rel_autonomie_wizard2_categ',
        'wizard_id', 'categorie_id',
        string="Catégories à exclure"
    )

    position_ids = fields.Many2many(
        'account.budget.post',
        'rel_autonomie_wizard2_position',
        'wizard_id', 'position_id',
        string="Positions à traiter"
    )

    select_all = fields.Boolean(
        string="Sélectionner tout",
        help="Cocher pour inclure toutes les positions budgétaires"
    )

    file_data = fields.Binary("Fichier", readonly=True)
    file_name = fields.Char("Nom du fichier", readonly=True)

    @api.onchange('select_all', 'mode')
    def _onchange_select_all(self):
        if self.mode == 'exclude_positions' and self.select_all:
            self.position_ids = self.env['account.budget.post'].search([])
        else:
            self.position_ids = [(5, 0, 0)]
        if self.mode == 'exclude_categ' and self.select_all:
            self.categorie_ids = self.env['position.budgetaire.categorie'].search([])
        else:
            self.categorie_ids = [(5, 0, 0)]

    def _get_data(self):
        """Call generator and fetch lines"""
        Report = self.env['report.autonomie']
        Report.generate_summary(
            categories=self.categorie_ids.ids if self.categorie_ids else None,
            selected_positions=self.position_ids.ids if self.position_ids else None,
            mode=self.mode,
            year_n=int(self.year_n),
        )
        return self.env['report.autonomie'].search([('user_id', '=', self.env.uid)])

    def _format_float(self, value):
        """Helper to round floats to 2 decimals, keep 0.00 if None"""
        return round(value or 0.0, 2)

    def action_export_csv(self):
        records = self._get_data()
        output = io.StringIO(newline='')
        writer = csv.writer(output, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Header
        writer.writerow([
            "Ligne",
            f"Réalisation {int(self.year_n) - 2}",
            f"Réalisation {int(self.year_n) - 1}",
            f"Réalisation {self.year_n}",
            f"Prévision {int(self.year_n) + 1}"
        ])

        # Rows
        for rec in records:
            writer.writerow([
                rec.name,
                self._format_float(rec.realisation_n_2),
                self._format_float(rec.realisation_n_1),
                self._format_float(rec.realisation_n),
                self._format_float(rec.prevision_n_plus_1),
            ])

        # Encode CSV
        self.file_data = base64.b64encode(output.getvalue().encode('utf-8-sig'))
        file_name = f"rapport_autonomie_{self.year_n}.csv"

        # Direct download
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model={self._name}&id={self.id}&field=file_data&filename={file_name}&download=true",
            'target': 'self',
        }

    def action_export_pdf(self):
        records = self._get_data()
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm,
                                topMargin=20*mm, bottomMargin=20*mm)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph(f"Rapport Autonomie - Année {self.year_n}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Header style
        header_style = styles['Heading4']
        header_style.textColor = colors.white
        header_style.alignment = 1

        # Table header
        data = [[
            Paragraph("Ligne", header_style),
            Paragraph(f"Réalisation {int(self.year_n) - 2}", header_style),
            Paragraph(f"Réalisation {int(self.year_n) - 1}", header_style),
            Paragraph(f"Réalisation {self.year_n}", header_style),
            Paragraph(f"Prévision {int(self.year_n) + 1}", header_style)
        ]]

        normal_style = styles['Normal']
        for rec in records:
            data.append([
                Paragraph(rec.name or "", normal_style),
                Paragraph(str(self._format_float(rec.realisation_n_2)), normal_style),
                Paragraph(str(self._format_float(rec.realisation_n_1)), normal_style),
                Paragraph(str(self._format_float(rec.realisation_n)), normal_style),
                Paragraph(str(self._format_float(rec.prevision_n_plus_1)), normal_style),
            ])

        page_width = A4[0] - doc.leftMargin - doc.rightMargin
        col_widths = [
            page_width * 0.35,
            page_width * 0.1625,
            page_width * 0.1625,
            page_width * 0.1625,
            page_width * 0.1625
        ]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4a90e2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
        doc.build(elements)

        pdf_data = buffer.getvalue()
        buffer.close()

        self.file_data = base64.b64encode(pdf_data)
        file_name = f"rapport_autonomie_{self.year_n}.pdf"

        # Direct download
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model={self._name}&id={self.id}&field=file_data&filename={file_name}&download=true",
            'target': 'self',
        }