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

class LabTestInvoice(models.TransientModel):
    _name = 'lab.test.invoice'
    _description = "Lab Test Invoice"

    patient_id = fields.Many2one('res.partner',string = 'Patient',readonly = True)
    test_type = fields.Char(string = 'Test Type',readonly = True)
    charge = fields.Integer(string = 'Charge')

    @api.model
    def default_get(self, fields):
        rec = super(LabTestInvoice, self).default_get(fields)
        Move = self.env['patient.laboratory']
        if self.env.context.get('active_id'):
            lab_test_id = Move.browse(self.env.context['active_ids'])

            rec.update({ 'patient_id':  lab_test_id.patient_id.id, 'test_type' : lab_test_id.test_type})

            return rec

    def create_invoices(self):
        for record in self:
            Move = self.env['patient.laboratory']
            if self.env.context.get('active_id'):
                lab_test_id = Move.browse(self.env.context['active_ids'])
            if record.patient_id:
                ir_property_obj = self.env['ir.property']
                account_invoice_line_obj = self.env['account.move.line']
                product = self.env.ref('abs_hospital_management.product_lab_test_id')
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
                                                             'invoice_origin' : record.patient_id.patient_id,
                                                             'invoice_date' :invoice_date,
                                                             'state' :'draft',
                                                             'type' : 'out_invoice',
                                                             'invoice_line_ids': [(0,0,{
                                                                                   'product_id': product.id,
                                                                                   'name'      : self.test_type,
                                                                                   'price_unit': self.charge,
                                                                                   'account_id': inc_acc.id,
                                                                                   })],
                                                           })
                lab_test_id.write({ 'state' : 'invoiced'})
