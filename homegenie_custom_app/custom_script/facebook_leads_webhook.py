import frappe

@frappe.whitelist(allow_guest = True)
def handleFaceBookWebhook():
	if frappe.request.method == "POST":
		data = frappe.request.data
		frappe.log_error("From Webhook for HomeGenie",data)
		createLead(data)
		return "OK", 200
	
	elif frappe.request.method == "GET":

		from werkzeug.wrappers import Response
		response = Response()
		# frappe.response.display_content_as = 'inline'
		
		hub_mode = frappe.request.args.get("hub.mode")
		hub_challenge = frappe.request.args.get("hub.challenge")
		hub_verify_token = frappe.request.args.get("hub.verify_token")

		your_verify_token = "#$LeadsWebhookToken$#"

		if hub_mode == "subscribe" and hub_verify_token == your_verify_token:
			response.mimetype = "text/plain"
			response.data = hub_challenge
			return response
			# frappe.response.type = 'txt'
			# frappe.response = hub_challenge
		else:
			frappe.response.status_code = 403
			return "Verification failed"
	else:
		return "Invalid request", 400

	
def createLead(data):
	leadgen_id = data["entry"][0]["changes"][0]["value"]["leadgen_id"]
	page_id = data["entry"][0]["changes"][0]["value"]["page_id"]
	form_id = data["entry"][0]["changes"][0]["value"]["form_id"]
	frappe.log_error("Parsed Data from Webhook",[leadgen_id,page_id,form_id])

	


# @frappe.whitelist(allow_guest=True)
# def sampleFunction():
# 	frappe.log_error("from API","Yes, It is.")
# 	return "Yes Worked!"