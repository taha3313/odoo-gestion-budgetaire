from odoo import models, fields

class ReportCAAnneeResult(models.Model):
    _name = 'report.ca.annee.result'
    _description = 'Résultat Chiffre d’Affaires Annuel'

    annee = fields.Char(string='Année', index=True)
    montant_real = fields.Float(string='Montant Réalisé')
    montant_prev = fields.Float(string='Montant Prévisionnel')
    user_id = fields.Many2one('res.users', string='Utilisateur', index=True)
