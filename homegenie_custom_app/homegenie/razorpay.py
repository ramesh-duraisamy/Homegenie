import frappe
import razorpay


@frappe.whitelist(allow_guest=True)
def create_payment_link(dt, docname):
    try:
        gateway_settings = frappe.get_single("Razorpay Settings")
        if gateway_settings.api_key and gateway_settings.api_secret:
            doc = frappe.get_doc(dt, docname)
            api_key = gateway_settings.api_key
            api_secret = gateway_settings.get_password("api_secret")
            check_company_keys = frappe.db.get_all(
                "Company Razorpay Configuration",
                filters={"r_company": doc.company},
                fields=["api_key", "api_secret"],
            )
            frappe.log_error(title="check_company_keys", message=check_company_keys)
            if check_company_keys:
                api_key = check_company_keys[0].api_key
                api_secret = check_company_keys[0].api_secret
            client = razorpay.Client(auth=(api_key, api_secret))
            customer_name = ""
            customer_phone = ""
            customer = ""
            amount = doc.outstanding_amount
            amount_paid = doc.outstanding_amount
            customer_name = doc.customer
            customer_phone = ""
            if doc.custom_whatsapp_no:
                customer_phone = doc.custom_whatsapp_no
            customer = doc.customer
            amount = int(amount * 100)
            if frappe.db.get_value("Sales Invoice", docname, "status") == "Paid":
                return {
                    "status": "Failed",
                    "message": "Already payment is done for this invoice.",
                }
            response = client.payment_link.create(
                {
                    "amount": amount,
                    "currency": "INR",
                    "accept_partial": False,
                    "description": "Payment Against " + dt + " ( " + docname + " )",
                    "customer": {"name": customer_name, "contact": customer_phone},
                    "notify": {"sms": True, "email": True},
                    "reminder_enable": True,
                    "callback_url": frappe.utils.get_url()
                    + "/api/method/homegenie_custom_app.homegenie.razorpay.complete_payment_link",
                    "callback_method": "get",
                }
            )
            if not response.get("error"):
                if customer:
                    p_link = frappe.new_doc("Payment Link")
                    p_link.reference_document = dt
                    p_link.reference_name = docname
                    p_link.payment_link = response.get("short_url")
                    p_link.customer = customer
                    p_link.payment_link_id = response.get("id")
                    p_link.amount = amount_paid
                    p_link.save(ignore_permissions=True)
                    return {
                        "status": "Success",
                        "message": "Payment link has been sent to customer.",
                        "url": response.get("short_url"),
                    }
            else:
                frappe.log_error(title="payment_link", message=response)
                return {
                    "status": "Failed",
                    "message": response.get("error").get("description"),
                }
    except Exception:
        frappe.log_error(
            message=frappe.get_traceback(), title="create_payment_link-Razorpay"
        )
        return {"status": "Failed"}


@frappe.whitelist(allow_guest=True)
def complete_payment_link(**kwargs):
    response = kwargs
    if response.get("razorpay_payment_link_status") == "paid":
        payment_link = frappe.db.get_all(
            "Payment Link",
            filters={"payment_link_id": response.get("razorpay_payment_link_id")},
        )
        if payment_link:
            p_doc = frappe.get_doc("Payment Link", payment_link[0].name)
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = p_doc.payment_link


@frappe.whitelist(allow_guest=True)
def payment_link_paid(**kwargs):
    try:
        response = kwargs.get("payload")
        frappe.log_error(title="payment_link_paid", message=response)
        allow = False
        payment_link_id = None
        payment_transaction_id = None
        customer_phone = None
        commission_amount = 0
        if response and response.get("order").get("entity"):
            if response.get("order").get("entity").get("status") == "paid":
                if response.get("payment_link").get("entity"):
                    allow = True
                    payment_link_id = (
                        response.get("payment_link").get("entity").get("id")
                    )
                    payment_transaction_id = (
                        response.get("payment").get("entity").get("id")
                    )
                    # frappe.log_error(title="payment_entity",message=response.get("payment").get("entity"))
                    # frappe.log_error(title="payment_entity_customer",message=response.get("payment_link").get("entity").get("customer"))
                    commission_amount = response.get("payment").get("entity").get("fee")
                    if response.get("payment_link").get("entity").get("customer"):
                        if response.get("payment_link").get("entity").get("customer").get("contact"):
                            customer_phone = response.get("payment_link").get("entity").get("customer").get("contact")
        if allow and payment_link_id:
            payment_link = frappe.db.get_all(
                "Payment Link", filters={"payment_link_id": payment_link_id}
            )
            if payment_link:
                p_doc = frappe.get_doc("Payment Link", payment_link[0].name)
                p_doc.payment_status = "Paid"
                p_doc.transaction_id = payment_transaction_id
                p_doc.save(ignore_permissions=True)
                frappe.db.commit()
                # frappe.log_error(title="payment link",message=p_doc.as_dict())
                if not frappe.db.exists("Mode of Payment", "RazorPay"):
                    p_mode = frappe.new_doc("Mode of Payment")
                    p_mode.mode_of_payment = "Razorpay"
                    p_mode.save(ignore_permissions=True)
                # if p_doc.reference_document == "Sales Invoice":
                frappe.local.login_manager.user = "Administrator"
                frappe.local.login_manager.post_login()
                from erpnext.accounts.doctype.payment_entry.payment_entry import (
                    get_payment_entry,
                )

                pe = get_payment_entry(dt="Sales Invoice", dn=p_doc.reference_name)
                pe.reference_no = payment_transaction_id
                si_doc = frappe.get_doc("Sales Invoice",p_doc.reference_name)
                if si_doc.sales_team:
                    pe.custom_sales_person = si_doc.sales_team[0].sales_person
                from erpnext.accounts.doctype.payment_entry.payment_entry import get_party_details
                party_detail = get_party_details(company=si_doc.company,party_type="Customer",party=si_doc.customer,date=frappe.utils.getdate(),cost_center=si_doc.cost_center)
                pe.bank_account = ""           
                if party_detail:
                    if party_detail.get("bank_account"):
                        pe.bank_account = party_detail.get("bank_account")
                pe.naming_series = get_company_naming_series(si_doc.company)
                company_brand = frappe.db.get_all("Company Razorpay Configuration",filters={"r_company":si_doc.company},fields=['*'])
                if company_brand:
                    if company_brand[0].brand:
                        pe.custom_brand = company_brand[0].brand
                    if commission_amount>0:
                        if company_brand[0].commission_account_head and  company_brand[0].cost_center:
                            pe.append("deductions",{
                                                    'account':company_brand[0].commission_account_head,
                                                    'cost_center':company_brand[0].cost_center,
                                                    'amount':commission_amount/100
                                                    })
                pe.mode_of_payment = "Razorpay"
                pe.flags.ignore_permissions = True
                

                pe.save(ignore_permissions=True)
                frappe.local.login_manager.user = "Guest"
                frappe.local.login_manager.post_login()
            else:
                # frappe.log_error(title="customer_phone",message=customer_phone)
                if customer_phone:
                    customer_doc = frappe.db.get_all("Customer",filters={"custom_contact_number":customer_phone})
                    # frappe.log_error(title="customer_phone",message=customer_phone)
                    if customer_doc:
                        merchant_id = response.get("order").get("entity").get("merchant_id") 
                        if merchant_id:
                            frappe.local.login_manager.user = "Administrator"
                            frappe.local.login_manager.post_login()
                            from erpnext.accounts.doctype.payment_entry.payment_entry import get_party_details
                            company_brand = frappe.db.get_all("Company Razorpay Configuration",filters={"merchant_id":merchant_id},fields=['*'])
                            customer_id = customer_doc[0].name
                            party_detail = get_party_details(company=company_brand[0].r_company,party_type="Customer",party=customer_id,date=frappe.utils.getdate())
                            frappe.local.login_manager.user = "Administrator"
                            frappe.local.login_manager.post_login()
                            amount = float(float(response.get("payment_link").get("entity").get("amount_paid"))/100)
                            pe_doc = frappe.new_doc("Payment Entry")
                            pe_doc.party_type='Customer'
                            pe_doc.company=company_brand[0].r_company
                            pe_doc.party=customer_id
                            pe_doc.received_amount=amount
                            pe_doc.reference_no = payment_transaction_id
                            pe_doc.reference_date = frappe.utils.getdate()
                            pe_doc.mode_of_payment = "Razorpay"
                            pe_doc.payment_type = "Receive"
                            pe_doc.target_exchange_rate = 1
                            pe_doc.paid_to = company_brand[0].paid_to_account
                            pe_doc.paid_to_account_currency = "INR"
                            pe_doc.paid_amount = amount
                            pe_doc.bank_account = ""
                            pe_doc.naming_series = get_company_naming_series(company_brand[0].r_company)
                            if party_detail:
                                if party_detail.get("bank_account"):
                                    pe_doc.bank_account = party_detail.get("bank_account")
                                if party_detail.get("party_account"):
                                    pe_doc.paid_from = party_detail.get("party_account")
                            pe_doc.flags.ignore_permissions = True
                            frappe.log_error(title="pe_doc",message=pe_doc.as_dict())
                            pe_doc.save(ignore_permissions=True)
                            if company_brand[0].brand:
                                pe_doc.custom_brand = company_brand[0].brand
                            if commission_amount>0:
                                if company_brand[0].commission_account_head and  company_brand[0].cost_center:
                                    pe_doc.append("deductions",{
                                                            'account':company_brand[0].commission_account_head,
                                                            'cost_center':company_brand[0].cost_center,
                                                            'amount':float(float(commission_amount)/100)
                                                            })
                            pe_doc.save(ignore_permissions=True)
                            frappe.db.set_value("Payment Entry",pe_doc.name,"company",company_brand[0].r_company)
                            frappe.db.commit()
                            frappe.local.login_manager.user = "Guest"
                            frappe.local.login_manager.post_login()
                        else:
                            frappe.local.login_manager.user = "Administrator"
                            frappe.local.login_manager.post_login()
                            from erpnext import get_default_company
                            frappe.log_error(title="get_default_company()",message=get_default_company())
                            company_brand = frappe.db.get_all("Company Razorpay Configuration",filters={"r_company":get_default_company()},fields=['*'])
                            if company_brand:
                                customer_id = customer_doc[0].name
                                amount = float(float(response.get("payment_link").get("entity").get("amount_paid"))/100)
                                pe_doc = frappe.new_doc("Payment Entry")
                                pe_doc.party_type='Customer'
                                pe_doc.party=customer_id
                                pe_doc.compnay=company_brand[0].r_company
                                pe_doc.received_amount=amount
                                pe_doc.reference_no = payment_transaction_id
                                pe_doc.reference_date = frappe.utils.getdate()
                                pe_doc.mode_of_payment = "Razorpay"
                                pe_doc.payment_type = "Receive"
                                pe_doc.target_exchange_rate = 1
                                pe_doc.paid_to_account_currency = "INR"
                                pe_doc.paid_to = company_brand[0].paid_to_account
                                pe_doc.paid_amount = amount
                                pe_doc.flags.ignore_permissions = True
                                pe_doc.save(ignore_permissions=True)
                                pe_doc.naming_series = get_company_naming_series(company_brand[0].r_company)
                                if company_brand[0].brand:
                                    pe_doc.custom_brand = company_brand[0].brand
                                if commission_amount>0:
                                    if company_brand[0].commission_account_head and  company_brand[0].cost_center:
                                        pe_doc.append("deductions",{
                                                                'account':company_brand[0].commission_account_head,
                                                                'cost_center':company_brand[0].cost_center,
                                                                'amount':float(float(commission_amount)/100)
                                                                })
                                pe_doc.save(ignore_permissions=True)
                            frappe.local.login_manager.user = "Guest"
                            frappe.local.login_manager.post_login()

    except Exception:
        frappe.log_error(message=frappe.get_traceback(), title="complete_payment_link")

def get_company_naming_series(company):
    if company=='Homegenie Building Products Private Limited':
        return "RT-PE-.###"
    elif company=="Bioman Sewage Solutions Private Limited":
        return "BIO-PE-.###"
    elif company=="Doortisan Creations Private Limited":
        return "DD-PE-.###"
    elif company=="Timbe Windows Private Limited":
        return "TIMB-PE-.###"
    elif company == 'Colorhomes Developers Private Limited':
        return "CH-ACC-PAY-.###"
    else:
        return ""