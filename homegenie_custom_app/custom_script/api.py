import frappe

@frappe.whitelist()
def get_address(name):
    query = f""" SELECT A.name FROM `tabAddress` A 
                INNER JOIN `tabDynamic Link` DL ON DL.parent = A.name 
                WHERE DL.link_title = '{name}'"""
    result = frappe.db.sql(query,as_dict=1)
    return result