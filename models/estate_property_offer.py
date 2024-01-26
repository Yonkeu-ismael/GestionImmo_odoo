# By IsmaDev
# Create from 26/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class Offer(models.Model):
    _name = "estate_property_offer"
    _description = 'Offre'

    price = fields.Float('Prix', required=True)
    status = fields.Selection([
        ('accepted', 'Accepté'),
        ('refused', 'Refusé'),
    ], string='Statut', default='accepted', required=True , copy=False)
    property_id = fields.Many2one('estate_property', string='Propriété' ,required=True, index=True)
    # property_id = fields.Many2one('estate_property', string='Propriété' ,required=True, index=True, default=lambda self: self.env.estate_property.id)
    partner_id = fields.Many2one('res.partner', string='Achéteur' ,required=True, index=True)
    # partner_id = fields.Many2one('res.partner', string='Achéteur' ,required=True, index=True, default=lambda self: self.env.company.partner_id.id)

    @api.model
    def default_get(self, fields):
        defaults = super(Offer, self).default_get(fields)
        defaults['property_id'] = self.env['estate_property'].search([], limit=1).id
        defaults['partner_id'] = self.env.company.partner_id.id
        return defaults