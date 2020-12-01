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
{
    'name': "Hospital Management",
    'author': 'Ascetic Business Solution',
    'category': 'Human Resources',
    'summary': """Hospital Management""",
    'website': 'http://www.asceticbs.com',
    'license': 'OPL-1',
    'description': """ """,
    'version': '13.0.1.0',
    'depends': ['base','sale_management','account','hr'],
    'live_test_url' : "http://www.test.asceticbs.com/web/database/selector",
    'data': [
             'security/healthcare_management_security.xml',
             'security/ir.model.access.csv',
             'wizard/appointment_invoice_view.xml',
             'wizard/lab_test_invoice_view.xml',
             'views/patient_view.xml',
             'views/prescription_view.xml',
             'views/appointment_view.xml',
             'views/patient_hospitalization_view.xml',
             'views/physician_view.xml',
             'views/evaluation_view.xml',
             'views/diseases_view.xml',
             'views/physician_degree_view.xml',
             'views/health_center_view.xml',
             'views/symptoms_view.xml',
             'views/medicine_view.xml',
             'views/laboratory_view.xml',
             'views/lab_tests_view.xml',
             'views/patient_analysis_view.xml',
             'report/patient_admit_card_report_view.xml',
             'report/patient_admit_card_report_template.xml',
             'report/prescription_report_view.xml',
             'report/prescription_report_template.xml',
             'report/evaluation_report_view.xml',
             'report/evaluation_report_template.xml',
             'report/lab_test_report_view.xml',
             'report/lab_test_report_template.xml',
             'data/demo_product_view.xml',
             'data/laboratory_mail_template_data.xml'
            ],
    'price': 99.00, 
    'currency': "EUR",
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
