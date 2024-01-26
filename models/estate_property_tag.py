# By IsmaDev
# Create from 26/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class Tag(models.Model):
    _name = "estate_property_tag"
    _description = 'étiquette de Propriété '

    name = fields.Char('Nom', required=True, translate=True)
