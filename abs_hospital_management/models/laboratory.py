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
from odoo.exceptions import ValidationError

class PatientLaboratory(models.Model):
    _name = 'patient.laboratory'
    _description = "Patient Laboratory"

    name = fields.Char(string = 'Lab ID', copy=False, readonly=True, index=True, default='New')
    patient_id = fields.Many2one('res.partner',string = "Patient", required = True)
    doctor_id = fields.Many2one('hr.employee',string = 'Doctor')
    date = fields.Date(string = 'Date of Analysis')
    test_type = fields.Char(string = 'Test Type',required = True)
    results = fields.Text(string = 'Results')
    diagnosis = fields.Text(string = 'Diagnosis')
    state = fields.Selection([('draft','Draft'),('inprogress','Test is Progress'),('complete','Completed'),('invoiced','Invoiced')],string = "State", readonly=True, default='draft')
    lab_test_ids = fields.One2many('patient.laboratory.line','lab_test_id',string = 'Lab Tests')

    def action_progress(self):
        return self.write({'state': 'inprogress'})

    def action_complete(self):
        return self.write({'state': 'complete'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            ir_sequence_obj = self.env['ir.sequence']
            code = (_('TEST/'))

            ir_sequence_id = self.env['ir.sequence'].search([('name','=','Lab Test'),('implementation','=','no_gap'),('prefix','=',code),('code','=','patient.laboratory')])

            if not ir_sequence_id:
                new_ir_sequence_id = ir_sequence_obj.create({
                                                             'name' : 'Lab Test',
                                                             'implementation' : 'no_gap',
                                                             'prefix' : code,
                                                             'code' : 'patient.laboratory',
                                                             'padding' : 4
                                                           })

            vals['name'] = self.env['ir.sequence'].next_by_code('patient.laboratory') or '/'
        return super(PatientLaboratory, self).create(vals)

    def action_lab_test_send(self):
        if len(self.patient_id) == 0:
            raise ValidationError('You must first select a patient!')
        else:
            template1 = self.env.ref('abs_hospital_management.email_template_patient_lab_test')
            for record in self:
                mail_create = self.env['mail.template'].browse(template1.id).send_mail(record.id)
                if mail_create:
                    mail = self.env['mail.mail'].browse(mail_create).send()

            template2 = self.env.ref('abs_hospital_management.email_template_doctor_lab_test')
            for record in self:
                mail_create = self.env['mail.template'].browse(template2.id).send_mail(record.id)
                if mail_create:
                    mail = self.env['mail.mail'].browse(mail_create).send()
            return True

class PatientLaboratoryLine(models.Model):
    _name = 'patient.laboratory.line'
    _description = "Patient Laboratory Line"

    lab_test_id = fields.Many2one('patient.laboratory',string = "Reference ID")
    test_id = fields.Many2one('lab.tests',string = 'Test Name',required = True)
    result_range = fields.Char(string = 'Result Range')
    normal_range = fields.Char(string = 'Normal Range')
