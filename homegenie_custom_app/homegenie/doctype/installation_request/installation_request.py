# Copyright (c) 2024, Homegenie and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class InstallationRequest(Document):
	pass

@frappe.whitelist()
def get_child_item_value(name):
	try:
		if name:
			frappe.log_error('child_table',type(name))
			data = json.loads(name)
			# frappe.log_error('data',data)
			new_quo = frappe.new_doc('Quotation')
			child_item = data['installation_item_table']
			# frappe.log_error('child_iten',child_item)
			
			new_quo.party = "Customer"
			new_quo.party_name = data['customer']
			new_quo.customer_address = data['customer_address']
			new_quo.custom_installation_request = data['name']
			new_quo.contact_person = data['contact_person']
			new_quo.order_type = "Installation"

			if 'company' in data:
				if data["company"] == "Homegenie Building Products Private Limited":
					new_quo.naming_series = 'RT-QN-.###'
					new_quo.company = "Homegenie Building Products Private Limited"
				elif data["company"] == "Bioman Sewage Solutions Private Limited":
					new_quo.naming_series = 'BIO-QN-.###'
					new_quo.company = "Bioman Sewage Solutions Private Limited"
				elif data["company"] == "Doortisan Creations Private Limited":
					new_quo.naming_series = 'DD-QN-.###'
					new_quo.company = "Doortisan Creations Private Limited"
				elif data["company"] == "Timbe Windows Private Limited":
					new_quo.naming_series = 'TIMB-QN-.###'
					new_quo.company = "Timbe Windows Private Limited"
				else:
					new_quo.naming_series = ""

			for row in child_item:
				set_child = new_quo.append('items',{})
				set_child.item_code = row['item_code']
				set_child.uom = row['uom']
				set_child.description = row['description']
				set_child.qty = row['quantity']
			new_quo.insert(ignore_mandatory=True)
			return {'function':'Success','doctype':'Quotation','value':new_quo.name}
	except :
		frappe.msgprint('Error',frappe.get_traceback())
		return {'function':'failed'}
	
@frappe.whitelist()
def get_contact(contact):
	from frappe.contacts.doctype.contact.contact import get_contact_details
	try:
		contact_display = ""
		result = {}
		if contact:
			contact_address = get_contact_details(contact)
			mobile_no = frappe.db.get_value('Contact Phone',{"parent":contact},['phone'])
			contact_display = contact_address
			# frappe.log_error('Address',contact_display)
			result["function"] = "Success"
			result["value"] = contact_display
			result['mobile'] = mobile_no
			return result
	except:
		frappe.log_error('no error',frappe.get_traceback())

@frappe.whitelist()
def get_customer_contact_details(party):
	from frappe.contacts.doctype.contact.contact import get_contact_details
	if party:
		party = get_contact_details(contact=party)
		return party

@frappe.whitelist()
def fetch_party_details(party):
	from erpnext.accounts.party import get_party_details
	if party:
		party = get_party_details(party=party)
		# frappe.log_error("Party Details", party)
		return party

@frappe.whitelist()
def get_address(customer_name):
	from frappe.contacts.doctype.address.address import get_address_display
	
	try:
		# frappe.log_error("CD",customer_name)
		address = get_address_display(address_dict=customer_name)
		# frappe.log_error('test',customer_name)
		
		address_display = address
		result = {}
		result["function"] = "Success"
		result["value"] = address_display
		return result
	except:
		frappe.log_error('no error',frappe.get_traceback())

@frappe.whitelist()
def get_installation_note_child_table(name):
	try:
		if name:
			data = json.loads(name)
			new_installation_note = frappe.new_doc('Installation Note')
			child_item = data['installation_item_table'] if 'installation_item_table' in data else None
			new_installation_note.customer = data['customer'] if 'customer' in data else None
			new_installation_note.customer_address = data['customer_address'] if 'customer_address' in data else None
			new_installation_note.custom_installation_request_id = data['name'] if 'name' in data else None
			new_installation_note.contact_person = data['contact_person'] if 'contact_person' in data else None
			new_installation_note.inst_date = data['installation_date'] if 'installation_date' in data else None
			new_installation_note.territory = "India"
			new_installation_note.custom_brand = data['brand'] if 'brand' in data else None
			new_installation_note.company = data['company'] if 'company' in data else None
			new_installation_note.custom_sales_person = data['sales_person'] if 'sales_person' in data else None
			if 'company' in data:
				if data["company"] == "Homegenie Building Products Private Limited":
					new_installation_note.naming_series = 'RT-IN-.###'
				elif data["company"] == "Bioman Sewage Solutions Private Limited":
					new_installation_note.naming_series = 'BIO-IN-.###'
				elif data["company"] == "Doortisan Creations Private Limited":
					new_installation_note.naming_series = 'DD-IN-.###'
				elif data["company"] == "Timbe Windows Private Limited":
					new_installation_note.naming_series = 'TIMB-IN-.###'
				else:
					new_installation_note.naming_series = ""
			# new_installation_note.naming_series = data['naming_series'] if 'naming_series' in data else None

			for row in child_item:
				set_child = new_installation_note.append('items',{})
				set_child.item_code = row['item_code']
				set_child.custom_uom = row['uom']
				set_child.description = row['description']
				set_child.qty = row['quantity']
			new_installation_note.insert(ignore_mandatory=True)
			return {'function':'Success','doctype':'Installation Note','value':new_installation_note.name}
	except :
		frappe.msgprint('Error',frappe.get_traceback())
		return {'function':'failed'}

@frappe.whitelist()
def get_connection_of_quo_to_ir(doc,method=None):
	if doc and doc.custom_installation_request:
		installation_request_id = frappe.get_doc("Installation Request",doc.custom_installation_request)
		installation_request_id.quotation_id=doc.name
		installation_request_id.save()		
	