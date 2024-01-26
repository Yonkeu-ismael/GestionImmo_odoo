# By IsmaDev
# Create from 25/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from odoo import fields, models

class Estate(models.Model):
    _name = "estate_property"
    _description = 'Propriété immobilière'

    name = fields.Char('Titre', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    postcode = fields.Char('Code postal', required=True, translate=True)
    #La date de disponibilité par défaut est  dans 3 mois
    #La date de disponibilité ne doit pas être copié lors de la duplication d'un enregistrement
    date_availability = fields.Date('Date de disponibilité', 
                                    default=lambda self: (datetime.today() + timedelta(days=90)).strftime('%Y-%m-%d'),copy=False)
    expected_price = fields.Float('Prix attendu',required=True)
    #Le prix de vente ne doit pas être copié lors de la duplication d'un enregistrement et est en lecture seul
    selling_price = fields.Float('Prix de vente',required=True,copy=False)
    bedrooms = fields.Integer('Chambres',default=2)
    living_area = fields.Integer('Salon')
    facades = fields.Integer('Façades')
    garage = fields.Boolean('Garage', default=False)
    garden = fields.Boolean('Jardin', default=False)
    garden_area = fields.Integer('Zone du jardin')
    garden_orientation = fields.Selection( 
        string='Orientation du jardin',
        selection=[('North', 'Nord'), ('South', 'Sud'), ('East', 'Est'), ('West', 'Ouest')])
    active = fields.Boolean('Actif', default=True)
    status = fields.Selection([
        ('new', 'Nouveau'),
        ('offer_received', 'Offre reçue'),
        ('offer_accepted', 'Offre acceptée'),
        ('sold', 'Vendue'),
        ('cancelled', 'Annulée'),
    ], string='Statut', default='new', required=True , copy=False)
    property_type_id = fields.Many2one("estate_property_type", string="Type propriété")
    salesman = fields.Many2one('res.users', string='Vendeur', index=True, default=lambda self: self.env.user.id)
    buyer = fields.Many2one('res.partner', string='Achéteur', index=True, default=lambda self: self.env.company.partner_id.id)
    tag_ids = fields.Many2many("estate_property_tag" , string="Etiquette" )
    offer_ids = fields.One2many("estate_property_offer" , "property_id", string="Offre")
    