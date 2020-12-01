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

class Evaluation(models.Model):
    _name = 'patient.evaluation'
    _description = "Patient Evaluation"

    name = fields.Many2one('res.partner',string = 'Patient', required = True)
    doctor_id = fields.Many2one('hr.employee',string = 'Doctor')
    evaluation_start_date = fields.Date(string = 'Evaluation Start Date')
    evaluation_end_date = fields.Date(string = 'Evaluation End Date')
    complaint = fields.Char(string = 'Complaint')
    description = fields.Text(string = 'Evaluation Summary')

    ######## anthropometry
    weight = fields.Float(string = 'Weight(kg)')
    height = fields.Float(string = 'Height(cm)')
    body_mass_index = fields.Float(string = 'Body Mass Index(BMI)',compute = 'compute_bmi')

    ######## diagnosis
    information = fields.Text(string = 'Information on Diagnosis')
    treatment_plan = fields.Text(string = 'Treatment Plan')

    ######## symptoms
    symptoms_ids = fields.Many2many('patient.symptoms',string = 'Symptoms')

    prescription_count = fields.Integer(string = 'Prescriptions', compute = 'count_prescription')

    def compute_bmi(self):
        for evaluation in self:
            bmi = 0
            if evaluation.height:
                bmi = (evaluation.weight/((evaluation.height/100)*(evaluation.height/100)))
            evaluation.body_mass_index = bmi

    @api.onchange('name')
    def onchanhe_name(self):
        if self.name:
            self.action_view_prescriptions()
            self.count_prescription()
            self.evaluation_start_date = date.today()

    def count_prescription(self):
        prescription_obj = self.env['patient.prescription'].search([('patient_id','=',self.name.id)])
        if prescription_obj:
            count = 0
            for prescription in prescription_obj:
                if prescription:
                    count += 1
            self.prescription_count = count

    def action_view_prescriptions(self):
        return {
                'name': _('Prescription'),
                'domain': [('patient_id','=',self.name.id)],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'patient.prescription',
                'view_id': False,
                'views': [(self.env.ref('abs_hospital_management.view_prescription_menu_tree').id, 'tree'),
                          (self.env.ref('abs_hospital_management.view_prescription_menu_form').id, 'form')],
                'type': 'ir.actions.act_window'
               }
