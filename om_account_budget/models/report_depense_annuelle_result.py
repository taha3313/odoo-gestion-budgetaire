from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ReportDepenseAnnuelleResult(models.Model):
    _name = 'report.depense.annuelle.result'
    _description = 'Résultat Dépenses Annuelles'

    annee = fields.Char(string='Année', index=True)
    type_depense = fields.Selection([
        ('fonctionnement', 'Fonctionnement'),
        ('investissement', 'Investissement'),
        ('dette', 'Dette'),
    ], string='Type Dépense', index=True)
    montant_real = fields.Float(string='Montant Réalisé', digits=dp.get_precision('Account'))
    montant_prev = fields.Float(string='Montant Prévisionnel', digits=dp.get_precision('Account'))
    user_id = fields.Many2one('res.users', string='Utilisateur', index=True)

    # stored percentage → usable in pivot
    pourcentage_realisation = fields.Float(
        string='Réalisation (%)',
        digits=dp.get_precision('Account'),
        readonly=True,
        store=True,
        group_operator="avg"
    )
