# import frappe

# @frappe.whitelist()
# def create_visit(Date,source,event_id):
#     employee_name=frappe.db.get_value('ToDo', {'reference_name': event_id}, ['allocated_to'])
#     frappe.log_error(employee_name)
#     new_visit=frappe.new_doc("Visit")
#     new_visit.date=Date
#     new_visit.source=source
#     new_visit.employee=employee_name
#     new_visit.event_id=event_id
#     new_visit.insert()
#     frappe.log_error(new_visit)
#     return new_visit
    