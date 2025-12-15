# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError

# ---------------------------------------------------------
# Budgets
# ---------------------------------------------------------
class AccountBudgetPost(models.Model):
    _name = "account.budget.post"
    _order = "name"
    _description = "Budgetary Position"

    name = fields.Char('Nom', required=True)
    account_ids = fields.Many2many('account.account', 'account_budget_rel', 'budget_id', 'account_id', 'Comptes',
        domain=[('deprecated', '=', False)])
    company_id = fields.Many2one('res.company', 'Société', required=True,
                                 default=lambda self: self.env.company)


    categorie_id = fields.Many2one(
        'position.budgetaire.categorie',
        string='Catégorie',
        required=True
    )

    def _check_account_ids(self, vals):
        # Raise an error to prevent the account.budget.post to have not specified account_ids.
        # This check is done on create because require=True doesn't work on Many2many fields.
        if 'account_ids' in vals:
            account_ids = self.resolve_2many_commands('account_ids', vals['account_ids'])
        else:
            account_ids = self.account_ids
        if not account_ids:
            raise ValidationError(_('Le budget doit avoir au moins un compte'))

    @api.model
    def create(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).create(vals)


    def write(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).write(vals)


class CrossoveredBudget(models.Model):
    _name = "crossovered.budget"
    _description = "Budget"
    _inherit = ['mail.thread']

    name = fields.Char('Nom du budget', required=True, states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)
    date_from = fields.Date('Date début', required=True, states={'done': [('readonly', True)]})
    date_to = fields.Date('Date fin', required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('to_daf','En attente de validation du DAF'),
        ('validate', 'Validé'),
        ('refuse_daf', 'Refuser'),
        ('to_pdg', 'En attente de validation du PDG'),
        ('refuse_pdg', 'Refusé'),
        ('cancel', 'Annulé'),
        ('done', 'Validé')
        ], 'Status', default='draft', index=True, readonly=True, copy=False, track_visibility='always')
    crossovered_budget_line = fields.One2many('crossovered.budget.lines', 'crossovered_budget_id', 'Lignes budgétaires',
        states={'done': [('readonly', True)]}, copy=True)
    company_id = fields.Many2one('res.company', 'Société', required=True,
                                 default=lambda self: self.env.company)
    type_budget= fields.Selection([
        ('fonctionnement', 'Fonctionnement'),
        ('investissement', 'Investissement'),
        ('dette','Dette'),
        ('revenue', 'Revenue'),
        ], 'Type de budget', index=True, required=True,  copy=False, track_visibility='always')
    commentaire_daf = fields.Text(string='Commentaire du DAF')
    commentaire_pdg = fields.Text(string='Commentaire du PDG')
    date_commission = fields.Date('Date de conseil')
    pv_comission = fields.Binary(string="PV de conseil", attachment=True)

    def action_budget_confirm(self):
        self.write({'state': 'confirm'})
    def action_soumettre_daf(self):
        self.write({'state': 'to_daf'})
        ###################################### odoo notif ###################################
        group_id = self.env.ref('ccit_groups_config.group_responsables')
        user_obj = self.env['res.users'].search([('groups_id', '=', group_id.id)])
        notification_ids = []
        for rec in user_obj:
            notification_ids.append((0, 0, {
                'res_partner_id': rec.partner_id.id,
                'notification_type': 'inbox'}))
        self.message_post(body="Vous avez un budget en attente de validation portant le nom de: " + self.name , message_type='notification',
                          subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)


    def action_budget_draft(self):
        self.write({'state': 'draft'})

    def action_budget_validate(self):
        self.write({'state': 'validate'})
        ###################################### odoo notif ###################################
        group_id = self.env.ref('ccit_groups_config.group_resp_controle_gestion')
        user_obj = self.env['res.users'].search([('groups_id', '=', group_id.id)])
        notification_ids = []
        for rec in user_obj:
            notification_ids.append((0, 0, {
                'res_partner_id': rec.partner_id.id,
                'notification_type': 'inbox'}))
        self.message_post(body="Le budget portant le nom de: " + self.name + "a été validé par le DAF",
                          message_type='notification',
                          subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)

    def action_budget_refuser_daf (self):
        self.write({'state': 'draft'})
        ###################################### odoo notif ###################################
        group_id = self.env.ref('ccit_groups_config.group_resp_controle_gestion')
        user_obj = self.env['res.users'].search([('groups_id', '=', group_id.id)])
        notification_ids = []
        for rec in user_obj:
            notification_ids.append((0, 0, {
                'res_partner_id': rec.partner_id.id,
                'notification_type': 'inbox'}))
        self.message_post(body="Le budget portant le nom de: " + self.name + "a été révisé par le DAF",
                          message_type='notification',
                          subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)


    def action_budget_refuser_pdg(self):
        self.write({'state': 'refuse_pdg'})
        ###################################### odoo notif ###################################
        group_id = self.env.ref('ccit_groups_config.group_resp_controle_gestion')
        user_obj = self.env['res.users'].search([('groups_id', '=', group_id.id)])
        notification_ids = []
        for rec in user_obj:
            notification_ids.append((0, 0, {
                'res_partner_id': rec.partner_id.id,
                'notification_type': 'inbox'}))
        self.message_post(body="Le budget portant le nom de: " + self.name +"a été refusé par le PDG",
                          message_type='notification',
                          subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_set_to_draft (self):
        self.write({'state': 'draft'})

    def action_soumettre_pdg (self):
        self.write({'state': 'to_pdg'})

        ###################################### odoo notif ###################################
        group_id = self.env.ref('ccit_groups_config.group_directeur_general')
        user_obj = self.env['res.users'].search([('groups_id', '=', group_id.id)])
        notification_ids = []
        for rec in user_obj:
            notification_ids.append((0, 0, {
                'res_partner_id': rec.partner_id.id,
                'notification_type': 'inbox'}))
        self.message_post(body="Vous avez un budget en attente de validation portant le nom de: " + self.name , message_type='notification',
                          subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)

    def action_budget_done(self):
        self.write({'state': 'done'})
        ###################################### odoo notif ###################################
        group_id = self.env.ref('ccit_groups_config.group_resp_controle_gestion')
        user_obj = self.env['res.users'].search([('groups_id', '=', group_id.id)])
        notification_ids = []
        for rec in user_obj:
            notification_ids.append((0, 0, {
                'res_partner_id': rec.partner_id.id,
                'notification_type': 'inbox'}))
        self.message_post(body="Le budget portant le nom de: " + self.name + "a été validé par le PDG",
                          message_type='notification',
                          subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)


    def unlink (self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Vous ne pouvez pas supprimer un budget qui n'est pas en état de brouillon."))
        return super(CrossoveredBudget, self).unlink()


class CrossoveredBudgetLines(models.Model):
    _name = "crossovered.budget.lines"
    _description = "Budget Line"
    _rec_name = 'general_budget_id'


    name = fields.Char(compute='_compute_line_name')
    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget', ondelete='cascade', index=True, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Compte analytique')
    analytic_group_id = fields.Many2one('account.analytic.group', 'Groupe analytique', related='analytic_account_id.group_id', readonly=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Situation budgétaire')
    date_from = fields.Date('Date début', required=True)
    date_to = fields.Date('Date fin', required=True)
    paid_date = fields.Date('Date de paiement')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    planned_amount = fields.Monetary('Montant prévu', required=True,
        help="Montant que vous envisagez de gagner/dépenser. Enregistrez un montant positif s’il s’agit d’un revenu et un montant négatif s’il s’agit d’un coût.",)
    montant_prev = fields.Monetary( string='Montant prévue', related='planned_amount',store=True)
    montant_engaged = fields.Monetary(compute='_compute_engaged_amount',string='Montant engagé')
    montant_engag = fields.Monetary(compute='_compute_engaged_amount',string='Montant engagé',store=True)
    practical_amount = fields.Monetary( compute='_compute_practical_amount', string='Montant Réalisé', help="Montant réellement gagné/dépensé.",)
    montant_pratique = fields.Monetary(compute='_compute_montant_pratique',string='Montant Réalisé', store=True) #related='practical_amount',
    montant_pratique_paiement = fields.Monetary(compute='_compute_total_payments',string='Montant pratique',)
    paiement = fields.Monetary(compute='_compute_total_payments',string='Montant pratique',store=True)
    theoritical_amount = fields.Monetary(compute='_compute_theoritical_amount', string='Montant théorique', help="Montant que vous êtes censé avoir gagné/dépensé à cette date.",)
    montant_theorique = fields.Monetary(compute='_compute_montant_theorique', string='Montant theorique',store=True) #, related='theoritical_amount'
    montant_realise= fields.Monetary(compute='_compute_montant_realise', string='Montant réalisé')
    montant_rea= fields.Monetary(compute='_compute_montant_realise', string='Montant réalisé',store=True)
    percentage = fields.Float(compute='_compute_percentage', string='Réalisation',
        help="Comparaison entre montant pratique et théorique. Cette mesure vous indique si votre budget est inférieur ou supérieur à celui-ci.",)
    realisation = fields.Float (compute='_compute_realisation',string='Réalisation',store=True)
    pourcentage_engagement = fields.Float (compute='_compute_pourcentage_engagement',string="Engagement",)#related='percentage'
    engagement = fields.Float (compute='_compute_pourcentage_engagement',string="Engagement",store=True)

    company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company',
        string='Société', store=True, readonly=True)
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    crossovered_budget_state = fields.Selection(related='crossovered_budget_id.state', string='État budgétaire', store=True, readonly=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # overrides the default read_group in order to compute the computed fields manually for the group

        result = super(CrossoveredBudgetLines, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                                orderby=orderby, lazy=lazy)
        fields_list = ['practical_amount', 'theoritical_amount', 'percentage']
        if any(x in fields for x in fields_list):
            for group_line in result:

                # initialise fields to compute to 0 if they are requested
                if 'practical_amount' in fields:
                    group_line['practical_amount'] = 0
                if 'theoritical_amount' in fields:
                    group_line['theoritical_amount'] = 0
                if 'percentage' in fields:
                    group_line['percentage'] = 0
                    group_line['practical_amount'] = 0
                    group_line['theoritical_amount'] = 0

                if group_line.get('__domain'):
                    all_budget_lines_that_compose_group = self.search(group_line['__domain'])
                else:
                    all_budget_lines_that_compose_group = self.search([])
                for budget_line_of_group in all_budget_lines_that_compose_group:
                    if 'practical_amount' in fields or 'percentage' in fields:
                        group_line['practical_amount'] += budget_line_of_group.practical_amount

                    if 'theoritical_amount' in fields or 'percentage' in fields:
                        group_line['theoritical_amount'] += budget_line_of_group.theoritical_amount

                    if 'percentage' in fields:
                        if group_line['theoritical_amount']:
                            # use a weighted average
                            group_line['percentage'] = float(
                                (group_line['practical_amount'] or 0.0) / group_line['theoritical_amount']) * 100

        return result

    def _is_above_budget(self):
        for line in self:
            if line.theoritical_amount >= 0:
                line.is_above_budget = line.practical_amount > line.theoritical_amount
            else:
                line.is_above_budget = line.practical_amount < line.theoritical_amount

    def _compute_montant_pratique (self):
        for rec in self:
            rec.montant_pratique = rec.practical_amount


    def _compute_montant_theorique (self):

        for rec in self:
            rec.montant_theorique = rec.theoritical_amount


    # @api.depends('analytic_account_id', 'date_from', 'date_to')
    def _compute_engaged_amount(self):
        for rec in self:
            if not rec.analytic_account_id or not rec.date_from or not rec.date_to:
                rec.montant_engaged = 0.0
                rec.montant_engag = 0.0
                continue

            # 1. Récupérer le compte analytique
            analytic_account_id = rec.analytic_account_id.id

            # 2. Chercher les bons de commande d'ACHAT
            purchase_orders = self.env['purchase.order'].search([
                ('state', '=', 'purchase'),
                ('date_order', '>=', rec.date_from),
                ('date_order', '<=', rec.date_to),
            ])

            # 3. Chercher les bons de commande de VENTE
            sale_orders = self.env['sale.order'].search([
                ('state', '=', 'sale'),
                ('date_order', '>=', rec.date_from),
                ('date_order', '<=', rec.date_to),
            ])

            total_committed = 0.0

            # 4. Calcul pour les commandes d'achat
            for order in purchase_orders:
                for line in order.order_line:
                    if line.account_analytic_id.id == analytic_account_id:
                        total_committed += -line.price_total

            # # 5. Calcul pour les commandes de vente
            # for order in sale_orders:
            #     for line in order.order_line:
            #         if line.analytic_account_id.id == analytic_account_id:
            #             total_committed += line.price_subtotal

            # 6. Mise à jour du montant
            rec.montant_engaged = total_committed
            rec.montant_engag  = total_committed


    def _compute_montant_engag(self):
        for rec in self:
            rec.montant_engag = rec.montant_engaged

    def _compute_montant_realise(self):
        for line in self:
            line.practical_amount = 0.0
            line.montant_realise = 0.0
            line.montant_rea = 0.0

            if not line.analytic_account_id or not line.date_from or not line.date_to:
                continue

            # Récupérer toutes les lignes analytiques dans la période
            domain = [
                ('analytic_account_id', '=', line.analytic_account_id.id),
                ('date', '>=', line.date_from),
                ('date', '<=', line.date_to),
                ('parent_state', '=', 'posted')
            ]
            analytic_lines = self.env['account.move.line'].search(domain)

            # Grouper les lignes par facture (move)
            moves = analytic_lines.mapped('move_id')
            total = 0.0

            for move in moves:
                # Lignes avec analytique (et non lignes de taxes)
                product_lines = move.line_ids.filtered(lambda l: l.analytic_account_id and not l.tax_line_id)

                # Somme des prix TTC
                ttc = sum(l.price_total for l in product_lines)

                # Appliquer le bon signe
                sign = 1.0
                if move.type in ['out_invoice', 'in_refund']:
                    sign = 1.0
                elif move.type in ['out_refund', 'in_invoice']:
                    sign = -1.0

                total += sign * ttc

            # Affectation du montant calculé
            line.practical_amount = total
            line.montant_realise = total
            line.montant_rea = total

    def _compute_total_payments(self):
        for line in self:
            # Réinitialisation
            line.montant_pratique_paiement = 0.0
            line.paiement = 0.0

            if not line.analytic_account_id or not line.date_from or not line.date_to:
                continue

            # Domaine : écritures avec analytique, période, facture payée
            domain = [
                ('analytic_account_id', '=', line.analytic_account_id.id),
                ('date', '>=', line.date_from),
                ('date', '<=', line.date_to),
                ('parent_state', '=', 'posted'),
                ('move_id.invoice_payment_state', '=', 'paid'),
                ('move_id.type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']),
                ('tax_line_id', '=', False),  # Exclure les lignes de taxes
            ]

            move_lines = self.env['account.move.line'].search(domain)

            # Grouper par move
            moves = move_lines.mapped('move_id')
            total = 0.0

            for move in moves:
                product_lines = move.line_ids.filtered(lambda l: l.analytic_account_id and not l.tax_line_id)

                # Somme des prix TTC
                ttc = sum(l.price_total for l in product_lines)

                # Déterminer le signe selon type de facture
                sign = 1.0
                if move.type in ['out_invoice', 'in_refund']:
                    sign = 1.0
                elif move.type in ['out_refund', 'in_invoice']:
                    sign = -1.0

                total += sign * ttc

            # Affectation
            line.montant_pratique_paiement = total
            line.paiement = total

    def _compute_realisation(self):
        for rec in self:
            rec.realisation = rec.percentage

    def _compute_line_name(self):
        for rec in self:
            #just in case someone opens the budget line in form view
            computed_name = rec.crossovered_budget_id.name
            if rec.general_budget_id:
                computed_name += ' - ' + rec.general_budget_id.name
            if rec.analytic_account_id:
                computed_name += ' - ' + rec.analytic_account_id.name
            rec.name = computed_name
    def _compute_practical_amount(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]


                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to)
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount = self.env.cr.fetchone()[0] or 0.0
            line.montant_pratique = line.practical_amount

    def _compute_theoritical_amount(self):
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for line in self:
            if line.paid_date:
                if today <= line.paid_date:
                    theo_amt = 0.00
                else:
                    theo_amt = line.planned_amount
            else:
                line_timedelta = line.date_to - line.date_from
                elapsed_timedelta = today - line.date_from

                if elapsed_timedelta.days < 0:
                    # If the budget line has not started yet, theoretical amount should be zero
                    theo_amt = 0.00
                elif line_timedelta.days > 0 and today < line.date_to:
                    # If today is between the budget line date_from and date_to
                    theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                else:
                    theo_amt = line.planned_amount
            line.theoritical_amount = theo_amt
            line.montant_theorique =  line.theoritical_amount

###################### by Dhouha Mahdi nouvelle version avec formule réalisation = (montant pratique/ montant prévu)*100 ###################
    def _compute_percentage(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.percentage = float((line.montant_realise or 0.0) / line.planned_amount)
                line.realisation = line.percentage
            else:
                line.percentage = 0.00
                line.realisation = line.percentage

########################################################################################################################
    def _compute_pourcentage_engagement(self):
        for rec in self:
            if rec.theoritical_amount != 0.00:
                rec.pourcentage_engagement = float((rec.montant_engaged or 0.0) / rec.planned_amount)
                rec.engagement = rec.pourcentage_engagement
            else:
                rec.pourcentage_engagement = 0.0
                rec.engagement = rec.pourcentage_engagement


    @api.constrains('general_budget_id', 'analytic_account_id')
    def _must_have_analytical_or_budgetary_or_both(self):
        if not self.analytic_account_id and not self.general_budget_id:
            raise ValidationError(
                _("Vous devez saisir au minimum une position budgétaire ou un compte analytique sur une ligne budgétaire."))

    # def action_open_budget_entries(self):
    #     if self.analytic_account_id:
    #         # if there is an analytic account, then the analytic items are loaded
    #         action = self.env['ir.actions.act_window'].for_xml_id('analytic', 'account_analytic_line_action_entries')
    #         action['domain'] = [('account_id', '=', self.analytic_account_id.id),
    #                             ('date', '>=', self.date_from),
    #                             ('date', '<=', self.date_to)
    #                             ]
    #         if self.general_budget_id:
    #             action['domain'] += [('general_account_id', 'in', self.general_budget_id.account_ids.ids)]
    #     else:
    #         # otherwise the journal entries booked on the accounts of the budgetary postition are opened
    #         action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
    #         action['domain'] = [('account_id', 'in',
    #                              self.general_budget_id.account_ids.ids),
    #                             ('date', '>=', self.date_from),
    #                             ('date', '<=', self.date_to)
    #                             ]
    #     return action

    def action_open_budget_entries(self):

        # otherwise the journal entries booked on the accounts of the budgetary postition are opened
        action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
        action['domain'] = [('account_id', 'in',
                             self.general_budget_id.account_ids.ids),
                            ('date', '>=', self.date_from),
                            ('date', '<=', self.date_to)
                            ]
        return action


    @api.constrains('date_from', 'date_to')
    def _line_dates_between_budget_dates(self):
        for rec in self:
            budget_date_from = rec.crossovered_budget_id.date_from
            budget_date_to = rec.crossovered_budget_id.date_to
            if rec.date_from:
                date_from = rec.date_from
                if date_from < budget_date_from or date_from > budget_date_to:
                    raise ValidationError(_('"La date de début" de la ligne budgétaire doit être incluse dans la période du budget.'))
            if rec.date_to:
                date_to = rec.date_to
                if date_to < budget_date_from or date_to > budget_date_to:
                    raise ValidationError(_('"La date de fin" de la ligne budgétaire doit être incluse dans la période du budget.'))