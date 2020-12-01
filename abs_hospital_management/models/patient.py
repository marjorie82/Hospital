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
from datetime import datetime
from datetime import date

class Patients(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string = 'Is Patient')
    patient_id = fields.Char(string = 'Patient ID', copy=False, readonly=True, index=True, default='New')
    gender = fields.Selection([('male','Male'),('female','Female')],string = "Gender")
    dob = fields.Date(string = 'Date of Birth')
    marital_status = fields.Selection([('single','Single'),('married','Married')],string = "Marital Status")
    age = fields.Integer(string = "Patient's Age",compute = 'onchange_patient_age')
    description = fields.Text(string = 'Description')

    ####### oe-button
    appointment_ids = fields.One2many('patient.appointment','patient_id', string='Patient Appointments')
    prescription_ids = fields.One2many('patient.prescription','patient_id', string='Patient Prescriptions')
    invoice_ids = fields.One2many('account.move','partner_id', string='Patient Invoices')
    laboratory_ids = fields.One2many('patient.laboratory','patient_id', string='Patient Laboratories')

    appointment_count = fields.Integer(string = 'Appointments', compute = 'count_appointment')
    prescription_count = fields.Integer(string = 'Prescriptions', compute = 'count_prescription')
    invoice_count = fields.Integer(string = 'Invoices', compute = 'count_invoice')
    tests_count = fields.Integer(string = 'Lab tests', compute = 'count_lab_tests')

    ####### General Information
    profession = fields.Char(string = 'Profession')
    is_deceased = fields.Boolean(string = 'Patient deceased')

    ####### Family
    member_ids = fields.One2many('patient.family','patient_patient_id',string = 'Members')

    ####### Lifestyle
    exercise = fields.Boolean(string = 'Exercise')
    sleeps_at_daytime = fields.Boolean(string = 'Sleeps at Daytime')
    minutes_per_day = fields.Char(string = 'Minutes/Day')
    hours_of_sleep = fields.Char(string = 'Hours of Sleep')
    meals_per_day = fields.Char(string = 'Meals/Day')
    eat_alone = fields.Boolean(string = 'Eats alone')
    coffee = fields.Boolean(string = 'Coffee')
    cups_per_day = fields.Char(string = 'Cups/Day')
    soft_drinks = fields.Boolean(string = 'Soft drinks(sugar)')
    salt = fields.Boolean(string = 'Salt')
    on_diet = fields.Boolean(string = 'On diet?')
    diet_info = fields.Char(string = 'Diet info')

    ####### Diseases
    diseases_ids = fields.One2many('patient.diseases','patient_diseases_id',string = 'Diseases')
    invoice_amount = fields.Monetary(string = 'Invoice Amount', currency_field='currency_id', compute = 'compute_invoice_amount', store = True)

    def onchange_patient_age(self):
        today_date = date.today()
        date1 = datetime.strptime(str(self.dob),'%Y-%m-%d').date()
        self.age = today_date.year - date1.year

    @api.depends('invoice_ids.amount_total')
    def compute_invoice_amount(self):
        for patient in self:
            total = 0
            if patient.invoice_ids:
                for invoice in patient.invoice_ids:
                    total += invoice.amount_total
            patient.invoice_amount = total

    @api.model
    def create(self,vals):
        if self.env.context.get('is_patient', False):
            vals['is_patient'] = True

        if vals.get('patient_id', 'New') == 'New':
            ir_sequence_obj = self.env['ir.sequence']
            code = (_('PAC/'))

            ir_sequence_id = self.env['ir.sequence'].search([('name','=','Patients'),('implementation','=','no_gap'),('prefix','=',code),('code','=','res.partner')])

            if not ir_sequence_id:
                new_ir_sequence_id = ir_sequence_obj.create({
                                                             'name' : 'Patients',
                                                             'implementation' : 'no_gap',
                                                             'prefix' : code,
                                                             'code' : 'res.partner',
                                                             'padding' : 4
                                                           })

            vals['patient_id'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'

        return super(Patients,self).create(vals)

    @api.depends('appointment_ids')
    def count_appointment(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids)

    @api.depends('prescription_ids')
    def count_prescription(self):
        for record in self:
            record.prescription_count = len(record.prescription_ids)

    @api.depends('invoice_ids')
    def count_invoice(self):
        for record in self:
            count = 0
            if record.invoice_ids:
                for invoice in record.invoice_ids:
                    if invoice.invoice_origin == record.patient_id:
                        count += 1
            record.invoice_count = count

    @api.depends('laboratory_ids')
    def count_lab_tests(self):
        for record in self:
            record.tests_count = len(record.laboratory_ids)

    def action_view_appointments(self):
        return {
                'name': _('Appointment'),
                'domain': [('patient_id','=',self.id)],
                'view_type': 'form',
                'view_mode': 'tree,form,calendar',
                'res_model': 'patient.appointment',
                'view_id': False,
                'views': [(self.env.ref('abs_hospital_management.view_appointment_menu_tree').id, 'tree'),
                          (self.env.ref('abs_hospital_management.view_appointment_menu_form').id, 'form'),
                          (self.env.ref('abs_hospital_management.view_appointment_menu_calendar').id, 'calendar')],
                'type': 'ir.actions.act_window'
               }

    def action_view_prescriptions(self):
        return {
                'name': _('Prescription'),
                'domain': [('patient_id','=',self.id)],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'patient.prescription',
                'view_id': False,
                'views': [(self.env.ref('abs_hospital_management.view_prescription_menu_tree').id, 'tree'),
                          (self.env.ref('abs_hospital_management.view_prescription_menu_form').id, 'form')],
                'type': 'ir.actions.act_window'
               }

    def action_view_invoices(self):
        return {
                'name': _('Invoice'),
                'domain': [('partner_id','=',self.id),('type','=','out_invoice')],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [(self.env.ref('account.view_invoice_tree').id, 'tree'),
                          (self.env.ref('account.view_move_form').id, 'form')],
                'type': 'ir.actions.act_window'
               }

    def action_view_lab_tests(self):
        return {
                'name': _('Lab Tests Result'),
                'domain': [('patient_id','=',self.id)],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'patient.laboratory',
                'view_id': False,
                'views': [(self.env.ref('abs_hospital_management.view_lab_tests_result_menu_tree').id, 'tree'),
                          (self.env.ref('abs_hospital_management.view_lab_tests_result_menu_form').id, 'form')],
                'type': 'ir.actions.act_window'
               }

class PatientFamily(models.Model):
    _name = 'patient.family'
    _description = "Patient Family"

    patient_patient_id = fields.Many2one('res.partner',string = 'Reference ID')
    name = fields.Char(string = 'Name')
    phone = fields.Char(string = 'Phone')
    email = fields.Char(string = 'Email')
    relation = fields.Char(string = 'Relation')

class PatientDiseases(models.Model):
    _name = 'patient.diseases'
    _description = "Patient Diseases"

    patient_diseases_id = fields.Many2one('res.partner')
    diseases = fields.Many2one('diseases.diseases',string = 'Diseases')
    severity = fields.Char(string = 'Severity')
    status = fields.Char(string = 'Status')
    active = fields.Boolean(string = 'Active')
    infectious = fields.Boolean(string = 'Infectious')
    diagnosed_date = fields.Date(string = 'Diagnosed Date')
    remarks = fields.Char(string = 'Remarks')
