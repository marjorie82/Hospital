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
from datetime import date

class Prescription(models.Model):
    _name = 'patient.prescription'
    _description = "Patient Prescription"

    name = fields.Char(string = 'Prescription Number', copy=False, readonly=True, index=True, default='New')
    patient_id = fields.Many2one('res.partner',string = 'Patient',required = True)
    date = fields.Date(string = 'Prescription Date')
    doctor_id = fields.Many2one('hr.employee',string = 'Prescribing Doctor')
    description = fields.Text(string = 'Notes')
    medicine_ids = fields.One2many('patient.prescription.line','prescription_id',string = 'prescription Detail')
    invoice_id = fields.Many2one('account.move',string = 'Invoice', readonly = True)
    state = fields.Selection([('draft','Draft'),('invoiced','Invoiced')],string = "State", readonly=True, default='draft')

    def create_invoices(self):
        for record in self:
            if record.patient_id:
                invoice_line_list = []
                ir_property_obj = self.env['ir.property']
                invoice_date = date.today()
                product = self.env.ref('abs_hospital_management.product_prescription_id')
                account_id = False
                if product.id:
                    account_id = product.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                if not inc_acc:
                    raise ValidationError('You must have to add account!')

                if record.medicine_ids:
                    for medicine in record.medicine_ids:
                        if medicine:
                            invoice_line_dict = {'product_id' : medicine.medicicament_id.id,
                                                 'name' : medicine.medicicament_id.name,
                                                 'price_unit' : medicine.medicicament_id.list_price,
                                                 'account_id' : inc_acc.id,
                                                 'quantity' : medicine.quantity}
                            invoice_line_list.append((0,0, invoice_line_dict))
                account_invoice_obj = self.env['account.move']
                new_invoice_id = account_invoice_obj.create({
                                                             'partner_id': self.patient_id.id,
                                                             'invoice_origin'    : record.patient_id.patient_id,
                                                             'invoice_date' : invoice_date,
                                                             'state' :'draft',
                                                             'type' : 'out_invoice',
                                                             'invoice_line_ids': invoice_line_list,
                                                            })
                record.write({ 'invoice_id' : new_invoice_id.id, 'state' : 'invoiced'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            ir_sequence_obj = self.env['ir.sequence']
            code = (_('PRES/'))

            ir_sequence_id = self.env['ir.sequence'].search([('name','=','Patient Prescription'),('implementation','=','no_gap'),('prefix','=',code),('code','=','patient.prescription')])

            if not ir_sequence_id:
                new_ir_sequence_id = ir_sequence_obj.create({
                                                             'name' : 'Patient Prescription',
                                                             'implementation' : 'no_gap',
                                                             'prefix' : code,
                                                             'code' : 'patient.prescription',
                                                             'padding' : 4
                                                           })

            vals['name'] = self.env['ir.sequence'].next_by_code('patient.prescription') or '/'
        return super(Prescription, self).create(vals)

class PrescriptionLine(models.Model):
    _name = 'patient.prescription.line'
    _description = "Patient Prescription Line"

    prescription_id = fields.Many2one('patient.prescription',string = 'Reference ID')
    medicicament_id = fields.Many2one('product.product',string = 'Medicament')
    indication = fields.Char(string = 'Indication')
    dose = fields.Char(string = 'Dose')
    dose_unit = fields.Many2one('uom.uom',string = 'Dose Unit')
    form = fields.Char(string = 'Form')
    frequency = fields.Float(string = 'Frequency')
    quantity = fields.Float(string = 'Quantity',default = 1.0)
    treatment_duration = fields.Float(string = 'Treatment Duration')
    treatment_period = fields.Char(string = 'Treatment Period')
    allow_substitution = fields.Selection([('allow','Allow'),('not allow','Not Allow')],string = "Substitution")
    comment = fields.Char(string = 'Comment')

    @api.onchange('medicicament_id')
    def onchange_medicicament_id(self):
        if not self.prescription_id:
            return
        part = self.prescription_id.patient_id
        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a patient!'),
                }
            return {'warning': warning}
        if self.medicicament_id:
            self.dose_unit = self.medicicament_id.uom_id
