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

class Appointment(models.Model):
    _name = 'patient.appointment'
    _description = "Patient Appointment"

    name = fields.Char(string = 'Appointment Number', copy=False, readonly=True, index=True, default='New')
    patient_id = fields.Many2one('res.partner',string = "Patient", required = True)
    doctor_id = fields.Many2one('hr.employee',string = 'Doctor')
    appointment_date = fields.Date(string = 'Appointment Date')
    patient_status = fields.Char(string = 'Patient status')
    health_centers = fields.Many2one('health.center',string = 'Health Center')
    urgency_level = fields.Char(string = 'Urgency level')
    invoice_exempt = fields.Boolean(string = 'Invoice exempt')
    invoice_id = fields.Many2one('account.move',string = 'Invoice',readonly = True)
    description = fields.Text(string = 'Comment')
    gender = fields.Selection([('male','Male'),('female','Female')],string = "Gender")
    dob = fields.Date(string = 'Date of Birth',required = True)
    marital_status = fields.Selection([('single','Single'),('married','Married')],string = "Marital Status")
    mobile = fields.Char(string = 'Mobile')

    state = fields.Selection([('draft','Draft'),('invoiced','Invoiced')],string = "State", readonly=True, default='draft')
    invoice_amount = fields.Float(string = 'Invoice Amount')

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            res_partner_obj = self.env['res.partner'].search([('id','=',self.patient_id.id)])
            if res_partner_obj:
                self.gender = res_partner_obj.gender
                self.dob = res_partner_obj.dob
                self.marital_status = res_partner_obj.marital_status
                self.mobile = res_partner_obj.mobile

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            ir_sequence_obj = self.env['ir.sequence']
            code = (_('APNMT/'))

            ir_sequence_id = self.env['ir.sequence'].search([('name','=','Appointment'),('implementation','=','no_gap'),('prefix','=',code),('code','=','patient.appointment')])

            if not ir_sequence_id:
                new_ir_sequence_id = ir_sequence_obj.create({
                                                             'name' : 'Appointment',
                                                             'implementation' : 'no_gap',
                                                             'prefix' : code,
                                                             'code' : 'patient.appointment',
                                                             'padding' : 4
                                                           })

            vals['name'] = self.env['ir.sequence'].next_by_code('patient.appointment') or '/'
            res_partner_obj = self.env['res.partner'].search([('id','=',vals['patient_id'])])
            if res_partner_obj:
                res_partner_obj.write({ 'is_patient' : True, 'gender' : vals['gender'], 'dob' : vals['dob'], 'marital_status' : vals['marital_status'], 'mobile' : vals['mobile'] })
        return super(Appointment, self).create(vals)
