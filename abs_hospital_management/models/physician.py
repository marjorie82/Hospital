# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api, fields, models, _

class Physician(models.Model):
    _inherit = 'hr.employee'

    is_physician = fields.Boolean(string = 'Is Doctor?')
    physician_id = fields.Char(string = 'Doctor ID')
    degree = fields.Many2many('physician.degree',string = 'Degree')
    graduation_institute = fields.Char(string = 'Graduation Institute')
    is_pharmacist = fields.Boolean(string = 'Pharmacist')
    consultancy_type = fields.Char(string = 'Consultancy Type')
    consultancy_charge = fields.Char(string = 'Consultancy Charge')
    description = fields.Text(string = 'Extra Information')

    @api.model
    def create(self,vals):
        res_user_obj = self.env['res.users']
        if vals.get('name'):
            physician_name = { 'name' : vals['name'], 'login' : vals['work_email'], 'email' :  vals['work_email'] }

            new_user_id = res_user_obj.sudo().create(physician_name)
            vals['user_id'] = new_user_id.id

        if self.env.context.get('is_physician', False):
            vals['is_physician'] = True

        return super(Physician,self).create(vals)
