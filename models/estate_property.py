# By IsmaDev
# Create from 25/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from odoo import api,fields, models,exceptions,tools
from odoo.exceptions import ValidationError
from lxml import etree

class Estate(models.Model):
    _name = "estate_property"
    _description = 'Propriété immobilière'
    _order = "id desc"

    name = fields.Char('Titre', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    postcode = fields.Char('Code postal', required=True, translate=True)
    #La date de disponibilité par défaut est  dans 3 mois
    #La date de disponibilité ne doit pas être copié lors de la duplication d'un enregistrement
    date_availability = fields.Date('Date de disponibilité', 
                                    default=lambda self: (datetime.today() + timedelta(days=90)).strftime('%Y-%m-%d'),copy=False)
    expected_price = fields.Float('Prix attendu',required=True)
    #Le prix de vente ne doit pas être copié lors de la duplication d'un enregistrement et est en lecture seul
    selling_price = fields.Float('Prix de vente',copy=False,readonly=True)
    bedrooms = fields.Integer('Chambres',default=2)
    living_area = fields.Integer('Surface habitable(m2)')
    facades = fields.Integer('Façades')
    garage = fields.Boolean('Garage', default=False)
    garden = fields.Boolean('Jardin', default=False)
    garden_area = fields.Integer('Surface du jardin(m2)')
    garden_orientation = fields.Selection( 
        string='Orientation du jardin',
        selection=[('North', 'Nord'), ('South', 'Sud'), ('East', 'Est'), ('West', 'Ouest')])
    active = fields.Boolean('Actif', default=True)
    state = fields.Selection([
        ('new', 'Nouveau'),
        ('offer_received', 'Offre reçue'),
        ('offer_accepted', 'Offre acceptée'),
        ('sold', 'Vendue'),
        ('cancelled', 'Annulée'),
    ], string='Etat', tracking=True, default='new',required=True, copy=False)
    property_type_id = fields.Many2one("estate_property_type", string="Type propriété")
    salesman_id = fields.Many2one('res.users', string='Vendeur', index=True, default=lambda self: self.env.user.id)
    buyer = fields.Many2one('res.partner', string='Achéteur', index=True, default=lambda self: self.env.company.partner_id.id)
    tag_ids = fields.Many2many("estate_property_tag" , string="Etiquette" )
    offer_ids = fields.One2many("estate_property_offer" , "property_id",ondelete="cascade", string="Offre")
    total_area = fields.Float('Superficie totale', compute='_compute_total_area', store=True, help="La superficie totale est la somme de la Surface du jardin(m2) et la Surface habitable(m2) ")
    best_price = fields.Float('Meilleur offre', compute='_compute_best_price',readonly=True, store=True)
    show_reset_to_draft_button = fields.Boolean(compute='_compute_show_reset_to_draft_button')

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    #Ici nous avons ajouté un décorateur @api.onchange pour les champs 'living_area', 'garden_area'.        
    #Lorsqu'on modifie la valeur de ces 2 champs, la methode _onchange_area est déclenchée pour calculer le total_area
    @api.onchange('living_area', 'garden_area')
    def _onchange_area(self):
        self.total_area = self.living_area + self.garden_area 
    #La méthode _compute_best_price retourne à chaque fois la meilleure offre et s'il n'y a pas d'offre il renvois 0
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for line in self:
                prices = line.offer_ids.mapped('price')
                if prices:
                    line.best_price = max(prices)
                else:
                    line.best_price = 0.0   
    #Cette méthode se déclanche à chaque fois que offer_ids change, il compare les prix et affecte le max à best_price                
    @api.onchange("offer_ids.price")
    def _onchange_area(self):
        for line in self:
                prices = line.offer_ids.mapped('price')
                if prices:
                    line.best_price = max(prices)
                else:
                    line.best_price = 0.0    
    #Ici nous avons ajouté un décorateur @api.onchange pour le champ garden. 
    #Lorsque la valeur du champ jardin change, la méthode _onchange_garden() est déclenchée.
    #Si garden est défini sur True, la méthode _onchange_garden() définit la garden_area sur 10 
    #et l'orientation sur "nord". Si garden est défini sur False, 
    #les champs garden_area et garden_orientation sont effacés en les définissant sur False.   
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'North'
        else:
            self.garden_area = False
            self.garden_orientation = False

    is_sold = fields.Boolean('Vendu', default=False)
    is_cancelled = fields.Boolean('Annulé', default=False)

    def action_cancel(self):
        if self.is_sold:
            raise exceptions.UserError("Une propriété vendue ne peut pas être annulée !!!")
        # self.is_cancelled = True
        self.state = 'cancelled'
    def action_sold(self):
        if self.is_cancelled:
            raise exceptions.UserError("Une propriété annulée ne peut pas être vendue !!!")
        # self.is_sold = True
        self.state = 'sold'
#Ajout des contraintes sur les champs, les montant doivent être positif
#ref https://www.postgresql.org/docs/12/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)',
         'Le prix de vente doit être strictement positif !'),
        ]

   #Ajout du contrainte python pour que le prix de vente ne puisse pas être inférieur à 90% du prix attendu.         
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if not tools.float_is_zero(record.selling_price, precision_digits=2) and \
                    tools.float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) == -1:
                raise exceptions.ValidationError("Le prix de vente ne peut pas être inférieur à 90% du prix attendu !!!")
    
    #Empêcher la suppression d'une propriété si son état n'est pas « new » ou « cancelled »        
    def _check_state_deletion(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise exceptions.UserError("Vous ne pouvez pas supprimer une propriété dont l'état n'est pas Nouveau ou Annulé.")
    
    def unlink(self):
        self._check_state_deletion()
        return super(Estate, self).unlink()
    
    # Règle de contrôle d'accès
    # def write(self, vals):
    #     if 'state' in vals and vals['state'] not in ('new','offer_received','offer_accepted') :
    #         raise exceptions.UserError("Vous ne pouvez pas modifier cette propriété")
    #     return super(Estate, self).write(vals)
    # @api.onchange('state')
    # def _onchange_state(self):
    #     if self.state != 'new':
    #         raise exceptions.UserError("Vous ne pouvez pas modifier une propriété si son état n'est pas 'Nouveau'.")
