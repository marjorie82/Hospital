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

class PatientHospitalization(models.Model):
    _name = 'patient.hospitalization'
    _description = "Patient Hospitialization"

    name = fields.Char(string = 'Registartion Code', copy=False, readonly=True, index=True, default='New')
    patient_id = fields.Many2one('res.partner',string = 'Patient',required = True)
    hospital_bed = fields.Char(string = 'Hospital Bed')
    hospitalization_date = fields.Date(string = 'Hospitalization date')
    expected_discharge_date = fields.Date(string = 'Expected discharge date')
    attending_doctor_id = fields.Many2one('hr.employee',string = 'Attending Doctor')
    operating_doctor_id = fields.Many2one('hr.employee',string = 'Operating Doctor')
    admission_type = fields.Char(string = 'Admission Type')
    reason_for_admission = fields.Many2one('diseases.diseases',string = 'Reason for Admission')
    description = fields.Text(string = 'Extra info')

    state = fields.Selection([('free','Free'),('confirmed','Confirmed'),('hospitalized','Hospitalized'),('discharge','Discharged'),('cancel','Cancel')],string = "State", readonly=True, default='free')

    def action_confirm(self):
        return self.write({'state': 'confirmed'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_patient_admitted(self):
        return self.write({'state': 'hospitalized'})

    def action_discharge_patient(self):
        for record in self:
            if record.patient_id:
                patient_obj = self.env['res.partner'].search([('id','=',record.patient_id.id)])
                if patient_obj:
                    invoice_obj = self.env['account.move'].search([('partner_id','=',patient_obj.id)])
                    if invoice_obj:
                        for invoice in invoice_obj:
                            if invoice.amount_residual != 0:
                                raise ValidationError(_( "Payment remain!"))
        return self.write({'state': 'discharge'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            ir_sequence_obj = self.env['ir.sequence']
            code = (_('INPAC/'))

            ir_sequence_id = self.env['ir.sequence'].search([('name','=','Patient Hospitalization'),('implementation','=','no_gap'),('prefix','=',code),('code','=','patient.hospitalization')])

            if not ir_sequence_id:
                new_ir_sequence_id = ir_sequence_obj.create({
                                                             'name' : 'Patient Hospitalization',
                                                             'implementation' : 'no_gap',
                                                             'prefix' : code,
                                                             'code' : 'patient.hospitalization',
                                                             'padding' : 4
                                                           })

            vals['name'] = self.env['ir.sequence'].next_by_code('patient.hospitalization') or '/'
        return super(PatientHospitalization, self).create(vals)
