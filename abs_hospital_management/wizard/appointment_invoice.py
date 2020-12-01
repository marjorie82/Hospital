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

class AppointmentInvoice(models.TransientModel):
    _name = 'appointment.invoice'
    _description = "Appointment Invoice"

    patient_id = fields.Many2one('res.partner',string = "Patient's Name", required = True, readonly = True)
    doctor_id = fields.Many2one('hr.employee',string = 'Physician', readonly = True)
    appointment_date = fields.Date(string = 'Appointment Date', readonly = True)
    charges = fields.Integer(string = 'Charges')

    @api.model
    def default_get(self, fields):
        rec = super(AppointmentInvoice, self).default_get(fields)
        Move = self.env['patient.appointment']
        if self.env.context.get('active_id'):
            appointment_id = Move.browse(self.env.context['active_ids'])

            rec.update({ 'patient_id':  appointment_id.patient_id.id, 'doctor_id' : appointment_id.doctor_id.id, 'appointment_date' : appointment_id.appointment_date})

            return rec

    @api.onchange('doctor_id')
    def get_amount(self):
        for record in self:
            if record.doctor_id:
                self.charges = record.doctor_id.consultancy_charge

    def create_invoices(self):
        for record in self:
            Move = self.env['patient.appointment']
            if self.env.context.get('active_id'):
                appointment_id = Move.browse(self.env.context['active_ids'])
            if record.patient_id:
                ir_property_obj = self.env['ir.property']
                account_invoice_line_obj = self.env['account.move.line']
                product = self.env.ref('abs_hospital_management.product_appointment_id')
                invoice_date = date.today()
                account_id = False
                if product.id:
                    account_id = product.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                if not inc_acc:
                    raise ValidationError('You must have to add account!')

                account_invoice_obj = self.env['account.move']
                new_invoice_id = account_invoice_obj.create({'partner_id' : record.patient_id.id,
                                                             'invoice_date' :invoice_date,
                                                             'invoice_origin' :record.patient_id.patient_id,
                                                             'state' :'draft',
                                                             'type' : 'out_invoice',
                                                             'invoice_line_ids': [(0,0,{
                                                                                   'product_id': product.id,
                                                                                   'name'      : product.name,
                                                                                   'price_unit': self.charges,
                                                                                   'account_id': inc_acc.id,
                                                                                   })],
                                                           })
                appointment_id.write({ 'invoice_id' : new_invoice_id.id, 'invoice_exempt' : True, 'state' : 'invoiced', 'invoice_amount' : self.charges})
