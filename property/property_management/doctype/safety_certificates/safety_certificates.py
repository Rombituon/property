# -*- coding: utf-8 -*-
# Copyright (c) 2020, BJJ and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class SafetyCertificates(Document):
	def autoname(self):
		prefix = ''
		if self.certificate_type == "Gas":
			prefix = 'GSC'
		if self.certificate_type == "Electric":
			prefix = 'ESC'
		if prefix == '':
			frappe.throw("Certificate Type Mandatory")
		self.name = make_autoname(prefix + ' .####')

