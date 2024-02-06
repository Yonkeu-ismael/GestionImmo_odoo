# By IsmaDev
# Create from 26/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,exceptions,tools
from datetime import timedelta

class Offer(models.Model):
    _name = "estate_property_offer"
    _description = 'Offre'
    _order = "price desc"

    price = fields.Float('Prix', required=True)
    validity = fields.Integer('Validité(jour)', default="7")
    date_deadline = fields.Date('Date échéance', compute='_compute_date_deadline', inverse='_inverse_date_deadline', readonly=False,store=True)
    create_date = fields.Date('Date de création', default=fields.Date.today())    
    status = fields.Selection([
        ('accepted', 'Accepté'),
        ('refused', 'Refusé'),
    ], string='Statut', copy=False)
    property_id = fields.Many2one('estate_property', string='Propriété' ,required=True, index=True,ondelete="cascade")
    partner_id = fields.Many2one('res.partner', string='Achéteur' ,required=True, index=True)
    # partner_id = fields.Many2one('res.partner', string='Achéteur' ,required=True, index=True, default=lambda self: self.env.company.partner_id.id)
    property_type_id = fields.Many2one('estate_property_type', string='Type Propriété', related='property_id.property_type_id', store=True)
   
    @api.model
    def default_get(self, fields):
        defaults = super(Offer, self).default_get(fields)
        defaults['property_id'] = self.env['estate_property'].search([], limit=1).id
        defaults['partner_id'] = self.env.company.partner_id.id
        return defaults
    # ici nous utilisons le décorateur @api.depends pour définir la méthode _compute_date_deadline() qui calcule la date d'échéance en ajoutant la validité (en jours) à la date de création. Si la date de création n'est pas définie, nous définissons date_deadline sur False.

    #Le décorateur @api.onchange est utilisé pour définir la méthode _inverse_date_deadline() qui est déclenchée lorsque la valeur de date_deadline change. Elle met à jour la date de création en fonction de la date d'échéance et de la validité.

    #Cela permet à l'utilisateur de définir soit la date de création, soit la validité, et d'avoir automatiquement la date d'échéance mise à jour en conséquence.
    
    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = False
    
    @api.onchange('date_deadline')
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.create_date = record.date_deadline - timedelta(days=record.validity)
            else:
                record.create_date = False

    #Lorsque la méthode accept_offer() est appelée et que l'offre est acceptée, nous mettons à jour le champ state pour le passer à 'accepted'. 
    #Ensuite, nous affectons la valeur de buyer et sale_price du modèle estate.property.offer aux champs correspondants buyer et sale_price 
    #du modèle estate.property. property_id est un champ relationnel entre estate.property.offer et estate.property qui relie l'offre à la propriété correspondante.    
    def accept_offer(self):
        self.status = 'accepted'
        self.property_id.write({
                    'buyer': self.partner_id.id,
                    'selling_price': self.price, 
                    'state': 'offer_accepted'               
                })
    def reject_offer(self):
        self.status = 'refused'
    #Ajout des contraintes sur les champs, les montant doivent être positif
    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)',
         "Le prix de l'offre doivent être strictement positifs!"),
        ]
    #Lors de la création d'une offre, la méthode create() est appelée. Elle récupère l'ID de la propriété et le montant de l'offre à partir des valeurs (vals) passées en paramètre.
    # la méthode vérifie si une propriété et un montant sont présents. Si oui, elle utilise self.env['estate_property'].browse(property_id) pour obtenir l'objet estate_property correspondant à l'ID de la propriété. Ensuite, elle recherche les offres existantes pour cette propriété avec self.search([('property_id', '=', property_id)]).
    #Si des offres existent et que le montant de l'offre nouvellement créée est inférieur au montant de l'offre existante le plus élevé, une exception ValidationError est levée pour indiquer que le montant de l'offre doit être supérieur ou égal à l'offre existante la plus élevée.
    #la méthode write() est utilisée pour définir l'état de la propriété sur "Offre reçue" en utilisant property.write({'state': 'offer_received'}).
    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        price = vals.get('price')
        
        if property_id and price:
            property = self.env['estate_property'].browse(property_id)
            existing_offers = self.search([('property_id', '=', property_id)])
            
            if existing_offers and price < max(existing_offers.mapped('price')):
                raise exceptions.ValidationError("Le montant de l'offre doit être supérieur ou égal à l'offre existante la plus élevée.")
            
            property.write({'state': 'offer_received'})
        
        return super(Offer, self).create(vals)
    
    @api.model
    def _cron_cancel_expired_offers(self):
        expired_offers = self.search([('date_deadline', '<=', fields.Date.today()), ('status', '!=', 'accepted')])
        expired_offers.reject_offer()

    # @api.constrains('price')
    # def _check_price(self):
    #     for offer in self:
    #         property = offer.property_id
    #         best_offer = self.search([('property_id', '=', property.id), ('state', '=', 'accepted')], order='price desc', limit=1)
    #         if best_offer and offer.price <= best_offer.price:
    #             raise exceptions.UserError("Vous ne pouvez pas valider une offre inférieure à la meilleure offre existante.")