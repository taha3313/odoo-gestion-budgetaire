from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import base64
import csv
from io import StringIO

class ReportDepenseAnnuelle(models.TransientModel):
    _name = 'report.depense.annuelle'
    _description = "Dépenses Annuelles"

    name = fields.Char(string="Nom", default="Tableau des Dépenses", readonly=True)

    start_year = fields.Date(
        string="Année de début",
        required=True,
        default=lambda self: date(datetime.today().year - 3, 1, 1)
    )
    end_year = fields.Date(
        string="Année de fin",
        required=True,
        default=lambda self: date(datetime.today().year, 1, 1)
    )

    table_html = fields.Html(string="Tableau", compute='_compute_table')

    def _get_budget_data_by_year_and_type(self, start_year, end_year):
        BudgetLine = self.env['crossovered.budget.lines']
        years = list(range(start_year, end_year + 1))
        result = {'fonctionnement': {}, 'investissement': {}, 'dette': {}}

        for depense_type in result:
            for year in years:
                date_from = f'{year}-01-01'
                date_to = f'{year}-12-31'

                domain = [
                    ('date_from', '<=', date_to),
                    ('date_to', '>=', date_from),
                    ('crossovered_budget_id.type_budget', '=', depense_type),
                    # ('crossovered_budget_id.state', '=', 'done'),
                ]

                budget_lines = BudgetLine.search(domain)

                total_real = sum(line.montant_realise or 0.0 for line in budget_lines)
                total_prev = sum(line.montant_prev or 0.0 for line in budget_lines)

                result[depense_type][year] = {
                    'real': total_real,
                    'prev': total_prev,
                }

        return result

    @api.onchange('start_year', 'end_year')
    def _onchange_years(self):
        if self.start_year and self.end_year:
            if self.start_year > self.end_year:
                raise ValidationError("L'année de début ne peut pas être supérieure à l'année de fin.")

    @api.depends('start_year', 'end_year')
    def _compute_table(self):
        for rec in self:
            if not rec.start_year or not rec.end_year:
                rec.table_html = ""
                continue

            start_year = rec.start_year.year
            end_year = rec.end_year.year

            if start_year > end_year:
                rec.table_html = "<p style='color:red;'>L'année de début doit être inférieure ou égale à l'année de fin.</p>"
                continue

            years = list(range(start_year, end_year + 1))
            data = rec._get_budget_data_by_year_and_type(start_year, end_year)

            def format_row(label, values_by_year):
                row_html = f"<tr><td><strong>{label}</strong></td>"
                for year in years:
                    year_data = values_by_year.get(year, {'real': 0.0, 'prev': 0.0})
                    real = year_data['real']
                    prev = year_data['prev']
                    pct = (real / prev * 100.0) if prev else 0.0
                    row_html += f"<td>{real:.2f}</td><td>{pct:.2f}%</td>"
                row_html += "</tr>"
                return row_html

            html = "<table class='table table-sm table-bordered'>"
            html += "<thead><tr><th>Dépenses</th>" + ''.join(
                [f"<th colspan='2'>{year}</th>" for year in years]) + "</tr>"
            html += "<tr><th></th>" + "<th>Montant</th><th>%</th>" * len(years) + "</tr></thead><tbody>"

            html += format_row("Fonctionnement", data["fonctionnement"])
            html += format_row("Investissement", data["investissement"])
            html += format_row("Dette", data["dette"])

            total_by_year = {
                year: {
                    'real': sum(data[depense].get(year, {}).get('real', 0.0) for depense in data),
                    'prev': sum(data[depense].get(year, {}).get('prev', 0.0) for depense in data)
                }
                for year in years
            }

            html += format_row("Total", total_by_year)
            html += "</tbody></table>"
            rec.table_html = html

    def print_pdf(self):
        return self.env.ref('om_account_budget.action_report_depense_annuelle_pdf').report_action(self)

    def export_csv(self):
        self.ensure_one()
        start_year = self.start_year.year
        end_year = self.end_year.year
        years = list(range(start_year, end_year + 1))
        data = self._get_budget_data_by_year_and_type(start_year, end_year)

        output = StringIO()
        writer = csv.writer(output)

        # CSV Header
        header = ['Dépenses']
        for year in years:
            header.extend([f"{year} - Réalisé", f"{year} - %"])
        writer.writerow(header)

        def write_row(label, values_by_year):
            row = [label]
            for year in years:
                val = values_by_year.get(year, {'real': 0.0, 'prev': 0.0})
                real = val['real']
                prev = val['prev']
                pct = (real / prev * 100.0) if prev else 0.0
                row.extend([f"{real:.2f}", f"{pct:.2f}%"])
            writer.writerow(row)

        write_row("Fonctionnement", data['fonctionnement'])
        write_row("Investissement", data['investissement'])
        write_row("Dette", data['dette'])

        total_by_year = {
            year: {
                'real': sum(data[dep].get(year, {}).get('real', 0.0) for dep in data),
                'prev': sum(data[dep].get(year, {}).get('prev', 0.0) for dep in data)
            }
            for year in years
        }

        write_row("Total", total_by_year)

        output.seek(0)
        file_content = output.getvalue().encode()
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'depenses_annuelles.csv',
            'type': 'binary',
            'datas': base64.b64encode(file_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/csv'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }


