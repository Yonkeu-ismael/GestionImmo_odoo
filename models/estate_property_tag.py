# By IsmaDev
# Create from 26/01/2024
# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models
from random import randint

class Tag(models.Model):
    _name = "estate_property_tag"
    _description = 'étiquette de Propriété '
    _order = "name"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Nom', required=True, translate=True)
    color = fields.Integer('Couleur', default=_get_default_color)
#Ajout des contraintes unique sur le champ name
    _sql_constraints = [
        ('check_name', 'UNIQUE(name)',
         'Le nom du tag dois être unique!'),
        ]
