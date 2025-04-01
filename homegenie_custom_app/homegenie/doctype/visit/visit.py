# Copyright (c) 2024, Homegenie and contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import getseries
from frappe.model.document import Document

class Visit(Document):
	def autoname(self):
		series = getseries(self.employee,4)
		self.name = f"{self.employee}-{series}"
