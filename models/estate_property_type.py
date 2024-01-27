# By IsmaDev
# Create from 25/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class Type(models.Model):
    _name = "estate_property_type"
    _description = 'Type de Propriété '
    _order = "name"

    name = fields.Char('Titre', required=True, translate=True)
    sequence = fields.Integer('Séquence', default=1, help="Utiliser pour mettre en avant le type le plus utilisé")
    property_ids = fields.One2many("estate_property" , "property_type_id", string="Offre")
#Ajout des contraintes unique sur le champ name
    _sql_constraints = [
        ('check_name', 'UNIQUE(name)',
         'Le nom du type de propriété dois être unique!'),
        ]
