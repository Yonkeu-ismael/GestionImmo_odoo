# By IsmaDev
# Create from 25/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class Type(models.Model):
    _name = "estate_property_type"
    _description = 'Type de Propriété '

    name = fields.Char('Titre', required=True, translate=True)
