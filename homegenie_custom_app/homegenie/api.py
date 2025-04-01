import frappe
from frappe.utils.password import get_decrypted_password
from frappe import _
from frappe.utils import get_link_to_form, getdate


# Delete Company Transaction
@frappe.whitelist()
def create_transaction_deletion_request(company):
    from homegenie_custom_app.homegenie.doctype.homegenie_transaction_deletion_record.homegenie_transaction_deletion_record import (
        is_deletion_doc_running,
    )

    is_deletion_doc_running(company)

    tdr = frappe.get_doc(
        {"doctype": "Homegenie Transaction Deletion Record", "company": company}
    )
    tdr.submit()
    tdr.start_deletion_tasks()

    frappe.msgprint(
        _("A Transaction Deletion Document: {0} is triggered for {0}").format(
            get_link_to_form("Homegenie Transaction Deletion Record", tdr.name)
        ),
        frappe.bold(company),
    )


@frappe.whitelist()
def update_event(event_id, distance, location, log_type, time, duration=0):
    try:
        event = frappe.get_doc("Event", event_id)
        event.custom_location = location
        time = frappe.utils.now()
        if log_type == "IN" and not event.custom_check_in:
            event.custom_check_in = time
            event.custom_distance = distance
        if log_type == "OUT" and not event.custom_check_out:
            event.custom_check_out = time
            event.custom_duration = duration
            event.status = "Completed"

        event.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.response.status = "Success"
        frappe.response.message = event
    except Exception:
        frappe.response.status = "Failed"
        frappe.log_error("homegenie.update_event", frappe.get_traceback())


@frappe.whitelist()
def validate_event_otp(event_id, otp):
    event = frappe.get_doc("Event", event_id)
    if int(event.custom_otp) == int(otp):
        event.custom_validate = otp
        event.status = "Completed"
        event.save(ignore_permissions=True)
        return {"status": "Success", "message": "OTP validated successfully."}
    else:
        event.custom_validate = otp
        event.save(ignore_permissions=True)
        return {"status": "Failed", "message": "Invalid OTP."}

@frappe.whitelist()
def get_employee_office_types(employee_id):
    office_types = frappe.db.get_all("Employee Office Type Mapping",filters={"parent":employee_id},fields=['office_type'])
    if not office_types:
        office_types = [{"office_type":"Head Office"}]
    return office_types


@frappe.whitelist()
def generate_event_otp(event_id):
    import random
    import math

    time = frappe.utils.now()
    random_number = math.floor(100000 + random.random() * 900000)
    otp_doc = frappe.new_doc("Number Log")
    otp_doc.otp = random_number
    otp_doc.event_name = event_id
    otp_doc.save(ignore_permissions=True)
    event = frappe.get_doc("Event", event_id)
    event.custom_otp = random_number
    # event.custom_check_out = time
    event.save(ignore_permissions=True)
    return {"status": "Success", "message": "OTP has been sent to customer."}


@frappe.whitelist()
def check_event(event_id):
    try:
        event_detail = {}
        event = frappe.get_doc("Event", event_id)
        event_detail.update({"event": event})
        distance = frappe.db.get_value(
            "Visit", {"event_id": event_id}, "custom_distance"
        )
        event_detail.update({"distance_travel": distance})
        value = {}
        if len(event.event_participants) > 0:
            for event_child in event.event_participants:
                doctype = event_child.reference_doctype
                docname = event_child.reference_docname
                value = frappe.get_doc(doctype, docname)

        frappe.response.status = "Success"
        # frappe.response.distance=distance
        frappe.response.message = [event_detail, value]
        # frappe.response.message = event
    except Exception:
        frappe.response.status = "Failed"
        frappe.log_error("homegenie.check_event", frappe.get_traceback())


@frappe.whitelist()
def get_event_list(
    user_id, view_type, date=None, page_no=1, page_length=20, search_txt=None
):
    try:
        page_start = (int(page_no) - 1) * int(page_length)
        condition = ""
        if view_type == "history":
            condition += " AND E.status = 'Completed'"
        elif view_type == "event":
            condition += " AND E.status not in ('Completed')"
            condition += " AND E.status = 'Open' "

        else:
            frappe.response.status = "Failed"
            frappe.response.message = (
                "Parameter view_type should be either 'history' or 'event'"
            )
        event_dict = frappe.db.get_all(
            "ToDo",
            {
                "allocated_to": user_id,
                "reference_type": "Event",
                "status": ("!=", "Cancelled"),
            },
            ["reference_name"],
        )
        # frappe.log_error("event dict",event_dict)
        event_list = ""
        if search_txt:
            condition += f" {condition} AND E.subject LIKE '%{search_txt}%'"
        for event in event_dict:
            event_list += "'" + event.reference_name + "'" + ","
        # frappe.log_error("Event List", event_list)

        event_list = "(" + event_list[:-1] + ")"
        # frappe.log_error("Event List Modified", event_list)

        if event_list != "()" and view_type == "event":
            if date:
                condition += f" AND DATE(E.starts_on) = '{date}' "
            response = frappe.db.sql(
                f"""
				SELECT E.name, E.starts_on,E.custom_product_enquired, E.status, E.subject, E.event_type, E.custom_distance FROM `tabEvent` E LEFT JOIN `tabEvent Participants` EP ON E.name = EP.parent WHERE E.name in {event_list} {condition} ORDER BY E.starts_on DESC LIMIT {page_start},{page_length} 
				""",
                as_dict=1,
            )
            frappe.response.status = "Success"
            frappe.response.message = response
        if event_list != "()" and view_type == "history":
            if date:
                condition += f" AND DATE(E.starts_on) = '{date}' "
            v_query = f"""
				SELECT E.name, E.starts_on, E.status, E.subject, E.custom_product_enquired , E.event_type, E.custom_check_in, E.custom_check_out, E.custom_duration, E.custom_distance FROM `tabEvent` E LEFT JOIN `tabEvent Participants` EP ON E.name = EP.parent WHERE E.name in {event_list} {condition} ORDER BY E.custom_check_in DESC LIMIT {page_start},{page_length} 
				"""
            response = frappe.db.sql(v_query, as_dict=1)
            frappe.log_error("response history", v_query)
            date_list = []
            date_data = {}
            date_sorted_response = []
            for row in response:
                row.starts_on = row.starts_on.strftime("%Y-%m-%d")
                # frappe.log_error(row.starts_on)
                if row.starts_on not in date_list:
                    # frappe.log_error("check_data_list",date_list)
                    # frappe.log_error("check_date_data",date)
                    date_list.append(row.starts_on)
                    if date_data:
                        date_sorted_response.append(date_data)
                    date_data = {"date": row.starts_on, "data": [row]}
                else:
                    date_data["data"].append(row)
            if date_data and not date_sorted_response:
                date_sorted_response.append(date_data)

            # frappe.log_error("date_list", date_list)
            # frappe.log_error("date_data", date_data)
            # frappe.log_error("date_sorted_response", date_sorted_response)

            frappe.response.status = "Success"
            frappe.response.message = date_sorted_response
        if event_list == "()":
            frappe.response.status = "Success"
            frappe.response.message = []
    except Exception:
        frappe.response.status = "Failed"
        frappe.log_error("homegenie.get_event_list", frappe.get_traceback())


@frappe.whitelist()
def get_upcoming_events(event_id):
    try:
        party_name = frappe.db.sql(
            f"SELECT EP.reference_docname from `tabEvent` E INNER JOIN `tabEvent Participants` EP ON E.name = EP.parent where E.name = '{event_id}'",
            as_dict=1,
        )[0]
        if party_name:
            event_data = frappe.db.sql(
                f"SELECT E.name, E.starts_on, E.status, E.subject, E.event_type, E.custom_check_in, E.custom_check_out, E.custom_duration FROM `tabEvent` E INNER JOIN `tabEvent Participants` EP ON E.name = EP.parent WHERE EP.reference_docname = '{party_name.reference_docname}' ORDER BY E.starts_on asc",
                as_dict=1,
            )
            if event_data:
                frappe.response.status = "Success"
                frappe.response.message = event_data
            else:
                frappe.response.status = "Success"
                frappe.response.message = []
        else:
            frappe.response.status = "Success"
            frappe.response.message = []
    except Exception:
        frappe.response.status = "Failed"
        frappe.log_error("homegenie.get_upcoming_events", frappe.get_traceback())


@frappe.whitelist(allow_guest=True)
def get_auth_token(user):
    api_key = frappe.db.get_value("User", user, "api_key")
    if api_key:
        api_secret = frappe.utils.password.get_decrypted_password(
            "User", user, fieldname="api_secret"
        )
        return {"api_secret": api_secret, "api_key": api_key}


@frappe.whitelist()
def generate_token(user):
    user_details = frappe.get_doc("User", user)
    api_key = user_details.api_key
    changes = 0
    if not user_details.api_secret:
        api_secret = frappe.generate_hash(length=15)
        user_details.api_secret = api_secret
        changes = 1
    else:
        api_secret = get_decrypted_password("User", user, "api_secret")
    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
        changes = 1
    if changes:
        user_details.save(ignore_permissions=True)
    return {"api_key": api_key, "api_secret": api_secret}


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        frappe.local.login_manager.authenticate(usr, pwd)
        frappe.local.login_manager.post_login()
        login_response = {}
        token = get_auth_token(usr)
        if token:
            login_response["api_key"] = token["api_key"]
            login_response["api_secret"] = token["api_secret"]
        else:
            token = generate_token(user=usr)
            login_response["api_key"] = token["api_key"]
            login_response["api_secret"] = token["api_secret"]
        # login_response['status'] = "Success"
        # frappe.log_error("api_key",token['api_key'])
        users = frappe.db.get_all(
            "User", fields=["name", "full_name"], filters={"api_key": token["api_key"]}
        )

        if users and users[0].name:
            roles = frappe.db.get_all(
                "Has Role", fields=["role"], filters={"parent": users[0].name}
            )
            # frappe.log_error(title="role",message=roles)
            employee = frappe.db.get_all(
                "Employee",
                fields=["name"],
                filters={"user_id": users[0].name, "status": "Active"},
            )
            # frappe.log_error(title="employee",message=employee)
            login_response["roles"] = roles
            if employee and employee[0]:
                login_response["message"] = frappe.local.response["message"]
                login_response["status"] = "Success"
                login_response["employee_id"] = employee[0].name
                login_response["user_id"] = users[0].name
                login_response["full_name"] = users[0].full_name
                return login_response
            if not employee:
                employee_reponse = {}
                employee_reponse["message"] = "User Has No  Employee Role"
                employee_reponse["status"] = "Employee Not Found"
                return employee_reponse
    except Exception:
        frappe.log_error(message=frappe.get_traceback(), title="login")
        # frappe.local.response["message"] = "Login Failed"
        # frappe.local.response["status"] = "Failed"

        return {"message": "login Failed", "status": "Failed"}


@frappe.whitelist(allow_guest=True)
def insert_doc(data=None, search_text=None, page_no=1, page_length=20):
    try:
        # data = json.loads(data)
        if data.get("name"):
            # new_doc = json.loads(data)
            insert_doc = frappe.get_doc(data.get("doctype"), data.get("name"))
            insert_doc.update(data)
            value = insert_doc.save(ignore_permissions=True)
            frappe.db.commit()
            return {
                "data": value,
                "status": "Success",
                "message": "Update Successfully",
            }
        elif data:
            # new_doc = json.loads(data)
            insert_doc = frappe.get_doc({"doctype": data.get("doctype")})
            insert_doc.update(data)
            value = insert_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return {
                "data": value,
                "status": "Success",
                "message": "Update Successfully",
            }
            frappe.response["status"] = "success"
    except Exception:
        frappe.response["status"] = "failed"
        frappe.response["message"] = "insert doc details failed"
        frappe.log_error("seapi.api.insert_doc", frappe.get_traceback())


@frappe.whitelist()
def insert_check_in(data):
    try:
        # if date:
        data["time"] = frappe.utils.now()
        dt = getdate(data.get("time"))
        lg_type = data.get("log_type")
        emp = data.get("employee")
        check_already = frappe.db.sql(
            f""" 
							SELECT name FROM `tabEmployee Checkin` 
							WHERE employee='{emp}' AND
							DATE(time)='{dt}' AND
							log_type = '{lg_type}'
						""",
            as_dict=1,
        )
        if check_already:
            return {
                "status": "Failed",
                "message": "You have already Checked " + data.get("log_type"),
            }
        if data.get("custom_office_type") == "HO":
            check_distance = validate_ho_distance(
                data.get("log_type"), data.get("device_id"), data.get("custom_ho")
            )
            if check_distance.get("status") == "Failed":
                return check_distance
        date = data.get("time")
        user_id = frappe.db.get_value("Employee", data.get("employee"), "user_id")
        check_event_visit_query = f"""SELECT V.name FROM 
									`tabVisit` V
									INNER JOIN `tabEvent` E ON V.event_id = E.name
									WHERE V.employee='{user_id}' AND
										V.date ='{getdate(date)}' AND 
										V.event_id<>'Employee Checked Out' AND
										V.event_id<>'Employee Checked In' AND 
										E.custom_check_out IS NULL
								"""
        # frappe.log_error("check_event_visit_query",check_event_visit_query)
        check_event_visit = frappe.db.sql(check_event_visit_query, as_dict=1)
        if check_event_visit:
            return {
                "status": "Failed",
                "message": "Please checkout for event which is already checked in.",
            }
        if data.get("employee") == "undefined":
            frappe.response["message"] = "User Has No  Employee Role"
            frappe.response["status"] = "Employee Not Found"
        else:
            if not data.get("custom_office_type"):
                data["custom_office_type"] = "Operations"
            data.update({"doctype": "Employee Checkin"})
            response = insert_doc(data)
            frappe.response["data"] = response
    except Exception:
        # updateaftersubmit_exception()
        frappe.log_error(message=frappe.get_traceback(), title="insert_check_in")
        frappe.response["status"] = "Failed"


@frappe.whitelist()
def get_head_office_list():
    return frappe.db.get_all("Homegenie Head Office", order_by="title")


def validate_ho_distance(log_type, from_location, custom_ho):
    import requests

    destinations = ""
    hos = frappe.db.get_all(
        "Homegenie Head Office",
        order_by="creation DESC",
        filters={"name": custom_ho},
        fields=["address", "latitude", "longitude", "allowd_distance_meters"],
        limit_page_length=100,
    )
    if hos:
        for h in hos:
            # destinations += h.latitude+","+h.longitude
            destinations = h.address
            maps = frappe.get_single("Google Settings")
            if maps.enable:
                GOOGLE_MAPS_API_URL = (
                    "https://maps.googleapis.com/maps/api/distancematrix/json"
                )
                params = {
                    "key": maps.api_key,
                    "origins": from_location,
                    "destinations": destinations,
                    "mode": "driving",
                }
                req = requests.get(GOOGLE_MAPS_API_URL, params=params)
                res = req.json()
                if res.get("rows"):
                    is_allowed = 0
                    for x in res.get("rows")[0].get("elements"):
                        if x.get("distance"):
                            if float(x.get("distance").get("value")) <= float(
                                h.allowd_distance_meters
                            ):
                                is_allowed = 1
                    if is_allowed == 1:
                        return {"status": "Success"}
                return {
                    "status": "Failed",
                    "message": "To check "
                    + log_type
                    + ", you must be within "
                    + "{:.2f}".format(float(h.allowd_distance_meters))
                    + " meters from the head office.",
                }
    return {"status": "Success"}


@frappe.whitelist()
def check_in_condition(data):
    try:
        # filters = {"employee": data.get("employee")}
        # frappe.log_error(title="employee",message=filters)
        if data.get("employee") == "undefined":
            frappe.response["message"] = "User Has No  Employee Role"
            frappe.response["status"] = "Employee Not Found"
        else:
            # today_checkin = frappe.db.get_all("Employee Checkin", filters=filters)
            today_checkin_query = f""" SELECT name as employee_checkin_id,employee,
										employee_name,
										log_type,`time`
									FROM `tabEmployee Checkin`
									WHERE employee='{data.get("employee")}' 
									AND DATE(time) = '{data.get("date")}'
								"""
            today_checkin = frappe.db.sql(today_checkin_query, as_dict=1)
            filtered_check_in = today_checkin if today_checkin else []
            frappe.response.message = filtered_check_in
            frappe.response.status = "success"

    except Exception:
        frappe.response.status = "Failed"
        frappe.log_error(message=frappe.get_traceback(), title="check_in_condition")


@frappe.whitelist()
def get_location(
    user_id, event_id, employee_checkin_id, latitude, longitude, log_type="IN"
):
    try:
        import requests
        import json

        if event_id != "Employee Checked In":
            source = ""
            s_lat = ""
            s_lng = ""
            destinations = ""
            destination_date = ""
            dest_name = ""
            source_date = frappe.get_value(
                "Visit",
                {
                    "event_id": event_id,
                    "employee": user_id,
                    "custom_employee_checkin": employee_checkin_id,
                },
                ["date"],
            )
            visit_data = frappe.db.get_all(
                "Visit",
                filters={
                    "event_id": event_id,
                    "employee": user_id,
                    "custom_employee_checkin": employee_checkin_id,
                },
                fields=[
                    "longitude",
                    "destination",
                    "name",
                    "source",
                    "latitude",
                    "latitude",
                    "date",
                ],
            )
            if visit_data:
                dest_name = visit_data[0].name
                destinations = visit_data[0].destination
                destination_date = visit_data[0].date
                source = visit_data[0].source
                s_lat = visit_data[0].latitude
                s_lng = visit_data[0].longitude
                if event_id == "Employee Checked Out" and log_type == "OUT":
                    if not source:
                        source = frappe.get_value(
                            "Visit",
                            {
                                "event_id": "Employee Checked In",
                                "employee": user_id,
                                "date": source_date,
                            },
                            ["source"],
                        )
                        s_lat, s_lng = frappe.get_value(
                            "Visit",
                            {
                                "event_id": "Employee Checked In",
                                "employee": user_id,
                                "date": source_date,
                            },
                            ["latitude", "longitude"],
                        )
                        # source_date = ""
                        query = f""" 
									SELECT custom_latitude,custom_longitude,device_id FROM `tabEmployee Checkin` EC 
									INNER JOIN `tabEmployee` E ON E.name = EC.employee 
									WHERE E.user_id='{user_id}' AND DATE(time)='{source_date}' AND log_type='OUT'
								"""
                        destinations_data = frappe.db.sql(query, as_dict=1)
                        if destinations_data:
                            destinations = destinations_data[0].device_id
                            latitude = destinations_data[0].custom_latitude
                            longitude = destinations_data[0].custom_longitude
            # frappe.log_error("source",source)
            # frappe.log_error("destinations",destinations)
            # frappe.log_error("s_lng",s_lng)
            # frappe.log_error("s_lat",s_lat)
            # frappe.log_error("latitude",latitude)
            # frappe.log_error("longitude",longitude)
            if source_date == destination_date:
                maps = frappe.get_single("Google Settings")
                if maps.enable:
                    GOOGLE_MAPS_API_URL = (
                        "https://maps.googleapis.com/maps/api/distancematrix/json"
                    )
                    params = {
                        "key": maps.api_key,
                        "origins": source,
                        "destinations": destinations,
                        "mode": "driving",
                    }
                    if longitude and longitude and s_lat and s_lng:
                        params = {
                            "key": maps.api_key,
                            "origins": s_lat + "," + s_lng,
                            "destinations": str(latitude) + "," + str(longitude),
                            "mode": "driving",
                        }
                    req = requests.get(GOOGLE_MAPS_API_URL, params=params)
                    res = req.json()
                    frappe.log_error(title="response", message=res)
                    frappe.log_error(title=dest_name, message=destinations)
                    distance_value = 0
                    if res["rows"]:
                        if res["rows"][0]["elements"]:
                            if res["rows"][0]["elements"][0].get("distance"):
                                distance_value = res["rows"][0]["elements"][0][
                                    "distance"
                                ]["text"]
                        if res["destination_addresses"]:
                            if not destinations:
                                destinations = res["destination_addresses"][0]
                    is_allowed_dis = 1
                    if event_id == "Employee Checked Out" and log_type == "OUT":
                        check_length = frappe.db.get_all(
                            "Visit", {"employee": user_id, "date": source_date}
                        )
                        if len(check_length) == 2:
                            is_allowed_dis = 0
                    if is_allowed_dis:
                        frappe.db.set_value(
                            "Visit",
                            {
                                "event_id": event_id,
                                "custom_employee_checkin": employee_checkin_id,
                                "employee": user_id,
                            },
                            "custom_distance",
                            distance_value,
                        )
                        if (
                            event_id != "Employee Checked Out"
                            and event_id != "Employee Checked In"
                        ):
                            frappe.db.set_value(
                                "Event",
                                {"name": event_id},
                                "custom_distance",
                                distance_value,
                            )
                    if not frappe.db.get_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "destination",
                    ):
                        frappe.db.set_value(
                            "Visit",
                            {
                                "event_id": event_id,
                                "custom_employee_checkin": employee_checkin_id,
                                "employee": user_id,
                            },
                            "destination",
                            destinations,
                        )
                    if (
                        event_id != "Employee Checked Out"
                        and event_id != "Employee Checked In"
                    ):
                        frappe.db.set_value(
                            "Event",
                            {"name": event_id},
                            "custom_check_out_location",
                            destinations,
                        )
                    if not frappe.db.get_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "destination_lat",
                    ):
                        frappe.db.set_value(
                            "Visit",
                            {
                                "event_id": event_id,
                                "custom_employee_checkin": employee_checkin_id,
                                "employee": user_id,
                            },
                            "destination_lat",
                            latitude,
                        )
                    if not frappe.db.get_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "latitude",
                    ):
                        frappe.db.set_value(
                            "Visit",
                            {
                                "event_id": event_id,
                                "custom_employee_checkin": employee_checkin_id,
                                "employee": user_id,
                            },
                            "latitude",
                            s_lat,
                        )
                    if not frappe.db.get_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "longitude",
                    ):
                        frappe.db.set_value(
                            "Visit",
                            {
                                "event_id": event_id,
                                "custom_employee_checkin": employee_checkin_id,
                                "employee": user_id,
                            },
                            "longitude",
                            s_lng,
                        )
                    if not frappe.db.get_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "destination_lng",
                    ):
                        frappe.db.set_value(
                            "Visit",
                            {
                                "event_id": event_id,
                                "custom_employee_checkin": employee_checkin_id,
                                "employee": user_id,
                            },
                            "destination_lng",
                            longitude,
                        )
                    if not frappe.db.get_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "source",
                    ):
                        frappe.db.set_value(
                            "Visit",
                            {
                                "event_id": event_id,
                                "custom_employee_checkin": employee_checkin_id,
                                "employee": user_id,
                            },
                            "source",
                            source,
                        )
                    if (
                        event_id != "Employee Checked Out"
                        and event_id != "Employee Checked In"
                        and source
                    ):
                        frappe.db.set_value(
                            "Event", {"name": event_id}, "custom_location", source
                        )
                    frappe.db.commit()
                    if log_type == "OUT" and event_id != "Employee Checked Out":
                        log_doc = frappe.new_doc("Visit Log")
                        log_doc.user = user_id
                        log_doc.source_address = source
                        log_doc.event_id = event_id
                        log_doc.destination_address = destinations
                        log_doc.source_latitude = s_lat
                        log_doc.source_longitude = s_lng
                        log_doc.destination_latitude = latitude
                        log_doc.destination_longitude = longitude
                        log_doc.date = getdate()
                        log_doc.distance = distance_value
                        log_doc.distance_response = json.dumps(res)
                        log_doc.save(ignore_permissions=True)
            frappe.response.message = distance_value
            frappe.response.source = source
            frappe.response.destination = destinations
            frappe.response.status = "success"
    except Exception:
        frappe.log_error(message=frappe.get_traceback(), title="get_location")
        frappe.response["status"] = "Failed"


@frappe.whitelist()
def get_location_old(
    user_id, event_id, employee_checkin_id, latitude, longitude, log_type="IN"
):
    try:
        import requests
        import json

        source = frappe.get_value(
            "Visit",
            {
                "event_id": event_id,
                "employee": user_id,
                "custom_employee_checkin": employee_checkin_id,
            },
            ["source"],
        )
        s_lat, s_lng = frappe.get_value(
            "Visit",
            {
                "event_id": event_id,
                "employee": user_id,
                "custom_employee_checkin": employee_checkin_id,
            },
            ["latitude", "longitude"],
        )
        if not source and event_id == "Employee Checked Out":
            source = frappe.get_value(
                "Employee",
                {
                    "event_id": "Employee Checked In",
                    "employee": user_id,
                    "date": getdate(),
                },
                ["source"],
            )
        if not s_lat and not s_lng and event_id == "Employee Checked Out":
            s_lat, s_lng = frappe.get_value(
                "Visit",
                {
                    "event_id": "Employee Checked In",
                    "employee": user_id,
                    "date": getdate(),
                },
                ["latitude", "longitude"],
            )
        source_date = frappe.get_value(
            "Visit",
            {
                "event_id": event_id,
                "employee": user_id,
                "custom_employee_checkin": employee_checkin_id,
            },
            ["date"],
        )
        if not source_date and event_id == "Employee Checked Out":
            source_date = frappe.get_value(
                "Visit",
                {
                    "event_id": "Employee Checked In",
                    "employee": user_id,
                    "date": getdate(),
                },
                ["date"],
            )
        dest_name = original_value(event_id, employee_checkin_id)
        if not frappe.db.exists("Visit", dest_name):
            dest_name = frappe.get_value(
                "Visit",
                {"event_id": event_id, "custom_employee_checkin": employee_checkin_id},
                "name",
            )
        destinations = frappe.get_value("Visit", dest_name, ["destination"])
        destination_date = frappe.get_value("Visit", dest_name, ["date"])
        # if user_id=="thirupal.operations@homegeniegroup.com":
        # 	frappe.log_error(title="source_date",message=source_date)
        # 	frappe.log_error(title="event_id",message=event_id)
        # 	frappe.log_error(title="employee_checkin_id",message=employee_checkin_id)
        # 	frappe.log_error(title="dest_name",message=dest_name)
        # 	frappe.log_error(title="destinations",message=destinations)
        # 	frappe.log_error(title="destination_date",message=destination_date)
        if event_id == "Employee Checked Out":
            destinations = frappe.db.get_value(
                "Employee Checkin", event_id, "device_id"
            )
        if source_date == destination_date:
            maps = frappe.get_single("Google Settings")
            if maps.enable:
                GOOGLE_MAPS_API_URL = (
                    "https://maps.googleapis.com/maps/api/distancematrix/json"
                )
                params = {
                    "key": maps.api_key,
                    "origins": source,
                    "destinations": destinations,
                    "mode": "driving",
                }
                if longitude and longitude and s_lat and s_lng:
                    params = {
                        "key": maps.api_key,
                        "origins": s_lat + "," + s_lng,
                        "destinations": str(latitude) + "," + str(longitude),
                        "mode": "driving",
                    }
                req = requests.get(GOOGLE_MAPS_API_URL, params=params)
                res = req.json()
                frappe.log_error(title="response", message=res)
                frappe.log_error(title=dest_name, message=destinations)
                distance_value = 0
                if res["rows"]:
                    if res["rows"][0]["elements"]:
                        if res["rows"][0]["elements"][0].get("distance"):
                            distance_value = res["rows"][0]["elements"][0]["distance"][
                                "text"
                            ]
                    if res["destination_addresses"]:
                        if not destinations:
                            destinations = res["destination_addresses"][0]
                frappe.db.set_value(
                    "Visit",
                    {
                        "event_id": event_id,
                        "custom_employee_checkin": employee_checkin_id,
                        "employee": user_id,
                    },
                    "custom_distance",
                    distance_value,
                )
                if destinations:
                    frappe.db.set_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "destination",
                        destinations,
                    )
                if latitude:
                    frappe.db.set_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "destination_lat",
                        latitude,
                    )
                if s_lat:
                    frappe.db.set_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "latitude",
                        s_lat,
                    )
                if s_lng:
                    frappe.db.set_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "longitude",
                        s_lng,
                    )
                if longitude:
                    frappe.db.set_value(
                        "Visit",
                        {
                            "event_id": event_id,
                            "custom_employee_checkin": employee_checkin_id,
                            "employee": user_id,
                        },
                        "destination_lng",
                        longitude,
                    )
                # if source:
                # 	frappe.db.set_value('Visit', {'event_id': event_id,"custom_employee_checkin":employee_checkin_id,"employee": user_id}, 'source', source)

                frappe.db.commit()
                if log_type == "OUT" and event_id != "Employee Checked Out":
                    log_doc = frappe.new_doc("Visit Log")
                    log_doc.user = user_id
                    log_doc.source_address = source
                    log_doc.event_id = event_id
                    log_doc.destination_address = destinations
                    log_doc.source_latitude = s_lat
                    log_doc.source_longitude = s_lng
                    log_doc.destination_latitude = latitude
                    log_doc.destination_longitude = longitude
                    log_doc.date = getdate()
                    log_doc.distance = distance_value
                    log_doc.distance_response = json.dumps(res)
                    log_doc.save(ignore_permissions=True)
            frappe.response.message = distance_value
            frappe.response.source = source
            frappe.response.destination = destinations
            frappe.response.status = "success"
    except Exception:
        frappe.log_error(message=frappe.get_traceback(), title="get_location")
        frappe.response["status"] = "Failed"


@frappe.whitelist()
def original_value(event_id, employee_checkin_id):
    import re

    source = frappe.get_value(
        "Visit",
        {"event_id": event_id, "custom_employee_checkin": employee_checkin_id},
        "name",
    )
    # frappe.log_error(source)
    match = re.search(r"(\d+)$", source)
    # frappe.log_error(match)
    if match:
        numeric_part = match.group(1)
        new_numeric_part = str(int(numeric_part) - 1).zfill(len(numeric_part))
        previous_value = re.sub(r"\d+$", new_numeric_part, source)
        # frappe.log_error(previous_value)
        return previous_value
    else:
        return []


@frappe.whitelist()
def create_visit(
    event_id,
    location,
    user_id,
    employee_check_in_id,
    reference_id=None,
    date=None,
    in_time=None,
    out_time=None,
    latitude=None,
    longitude=None,
):
    try:
        event_exists = frappe.db.exists(
            "Visit",
            {
                "event_id": event_id,
                "employee": user_id,
                "custom_employee_checkin": employee_check_in_id,
            },
        )
        # frappe.log_error('event_exists',[event_exists,event_id,employee_check_in_id])
        if not event_exists:
            if in_time:
                in_time = frappe.utils.now()
            if out_time:
                out_time = frappe.utils.now()
            if event_id != "Employee Checked In" and event_id != "Employee Checked Out":
                create_doc = frappe.new_doc("Visit")
                create_doc.employee = user_id
                create_doc.event_id = event_id
                source_location = ""
                source_lat = ""
                source_lng = ""
                visit_locations = frappe.db.get_all(
                    "Visit",
                    fields=[
                        "source",
                        "latitude",
                        "longitude",
                        "destination",
                        "destination_lat",
                        "destination_lng",
                        "event_id",
                    ],
                    filters={"employee": user_id, "date": date},
                    order_by="creation desc",
                )
                # frappe.log_error("visit_locations",visit_locations)
                if visit_locations:
                    if visit_locations[0].event_id == "Employee Checked In":
                        source_location = visit_locations[0].source
                        source_lat = visit_locations[0].latitude
                        source_lng = visit_locations[0].longitude
                    else:
                        source_location = visit_locations[0].destination
                        source_lat = visit_locations[0].destination_lat
                        source_lng = visit_locations[0].destination_lng
                create_doc.source = source_location
                create_doc.reference = reference_id
                create_doc.custom_employee_checkin = employee_check_in_id
                create_doc.custom_check_in_time = in_time
                create_doc.latitude = source_lat
                create_doc.longitude = source_lng
                create_doc.date = date
                create_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                frappe.response.message = create_doc
                frappe.response.status = "success"
            if event_id == "Employee Checked In":
                create_doc = frappe.new_doc("Visit")
                create_doc.employee = user_id
                create_doc.event_id = event_id
                create_doc.source = location
                create_doc.custom_employee_checkin = employee_check_in_id
                create_doc.reference = reference_id
                create_doc.custom_distance = "0"
                create_doc.custom_check_in_time = in_time
                create_doc.date = date
                create_doc.latitude = latitude
                create_doc.longitude = longitude
                create_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                frappe.response.message = create_doc
                frappe.response.status = "success"
            if event_id == "Employee Checked Out":
                create_doc = frappe.new_doc("Visit")
                create_doc.employee = user_id
                create_doc.event_id = event_id
                create_doc.custom_employee_checkin = employee_check_in_id
                create_doc.reference = reference_id
                create_doc.custom_check_in_time = in_time
                create_doc.date = date
                visit_locations = frappe.db.get_all(
                    "Visit",
                    fields=[
                        "source",
                        "latitude",
                        "longitude",
                        "destination",
                        "destination_lat",
                        "destination_lng",
                        "event_id",
                    ],
                    filters={"employee": user_id, "date": date},
                    order_by="creation desc",
                )
                if visit_locations:
                    create_doc.source = visit_locations[0].destination
                    create_doc.latitude = visit_locations[0].destination_lat
                    create_doc.longitude = visit_locations[0].destination_lng
                    if not visit_locations[0].destination:
                        create_doc.source = visit_locations[0].source
                        create_doc.latitude = visit_locations[0].latitude
                        create_doc.longitude = visit_locations[0].longitude
                create_doc.destination = location
                create_doc.destination_lat = latitude
                create_doc.destination_lng = longitude
                frappe.log_error("visit_locations", create_doc.as_dict())
                create_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                frappe.response.message = create_doc
                frappe.response.status = "success"
        if event_exists:
            get_visit_doc = frappe.get_doc(
                "Visit",
                {"event_id": event_id, "custom_employee_checkin": employee_check_in_id},
            )
            get_visit_doc.reference = reference_id
            get_visit_doc.custom_check_in_time = in_time
            get_visit_doc.custom_check_out_time = out_time
            get_visit_doc.destination = location
            get_visit_doc.destination_lat = latitude
            get_visit_doc.destination_lng = longitude
            get_visit_doc.date = date
            get_visit_doc.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.response.revisit = get_visit_doc
            frappe.response.message = get_visit_doc
            frappe.response.status = "success"
    except Exception:
        frappe.response.status = "Failed"
        frappe.log_error(message=frappe.get_traceback(), title="create_visit")


@frappe.whitelist()
def create_installation_note(name):
    # import json
    try:
        if name:
            data = frappe.get_doc("Sales Invoice", name)
            # frappe.log_error('data',data)
            new_installation_note = frappe.new_doc("Installation Note")
            child_item = data.items

            new_installation_note.customer = data.customer
            new_installation_note.customer_address = data.customer_address
            new_installation_note.territory = data.territory
            new_installation_note.custom_project = data.project
            new_installation_note.contact_person = data.contact_person
            new_installation_note.custom_sales_invoice_id = data.name
            new_installation_note.inst_date = data.posting_date
            new_installation_note.company = data.company
            # sales person fetch from installation request added pandiaraj 19-12-2024
            # new_installation_note.custom_sales_person = data.sales_person

            if data.company == "Homegenie Building Products Private Limited":
                new_installation_note.custom_brand = "Rolays"
                new_installation_note.naming_series = "RT-IN-.###"
            if data.company == "Bioman Sewage Solutions Private Limited":
                new_installation_note.custom_brand = "Bioman"
                new_installation_note.naming_series = "BIO-IN-.###"
            if data.company == "Doortisan Creations Private Limited":
                new_installation_note.custom_brand = "D'Sign Doors"
                new_installation_note.naming_series = "DD-IN-.###"
            if data.company == "Timbe Windows Private Limited":
                new_installation_note.custom_brand = "Timbe"
                new_installation_note.naming_series = "TIMB-IN-.###"

            for row in child_item:
                set_child = new_installation_note.append("items", {})
                set_child.item_code = row.item_code
                set_child.custom_uom = row.uom
                set_child.description = row.description
                set_child.qty = row.qty
                set_child.serial_no = row.serial_no
            new_installation_note.insert(ignore_mandatory=True)

            return {
                "function": "Success",
                "doctype": "Installation Note",
                "value": new_installation_note.name,
            }
    except Exception:
        frappe.msgprint("Error", frappe.get_traceback())
        frappe.log_error("Error", frappe.get_traceback())
        return {"function": "failed"}


@frappe.whitelist()
def get_connection_of_si_to_ins(doc, method=None):
    if doc and doc.custom_sales_invoice_id:
        installation_note_id = frappe.get_doc(
            "Sales Invoice", doc.custom_sales_invoice_id
        )
        installation_note_id.custom_installation_note_id = doc.name
        installation_note_id.save(ignore_permissions=True)
    if doc and doc.custom_installation_request_id:
        # frappe.log_error("inside req")
        installation_request_doc = frappe.get_doc(
            "Installation Request", doc.custom_installation_request_id
        )
        # frappe.log_error("installation_request_doc",installation_request_doc)
        installation_request_doc.installation_note_id = doc.name
        installation_request_doc.save("Update")
        # frappe.log_error("installation_request_doc end",)
    frappe.db.commit()


def technician_validation(doc, method=None):
    if doc.custom_status in ["Initiated", "Work in Progress", "Completed"]:
        if not doc.custom_technician:
            frappe.throw("Technician is not set")


@frappe.whitelist()
def shift_sync_checkin():
    try:
        shift_list = frappe.db.get_all(
            "Shift Type", filters={"enable_auto_attendance": 1}, pluck="name"
        )
        today_str = frappe.utils.today()
        today = frappe.utils.getdate()
        now = frappe.utils.get_datetime()
        for shift in shift_list:
            shift_doc = frappe.get_doc("Shift Type", shift)
            sync_check = frappe.utils.get_datetime(
                frappe.utils.add_to_date(
                    f"{today_str} {shift_doc.start_time}", hours=-1
                )
            )
            frappe.log_error(title="sync_check", message=sync_check)
            if now >= sync_check and sync_check > shift_doc.last_sync_of_checkin:
                frappe.log_error("last_sync", message="shift_doc.last_sync_of_checkin")
                if not shift_doc.process_attendance_after:
                    shift_doc.process_attendance_after = frappe.utils.getdate(
                        "0000-00-00"
                    )
                if today > shift_doc.process_attendance_after:
                    try:
                        shift_doc.last_sync_of_checkin = now
                        shift_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                    except Exception:
                        frappe.db.sql(
                            f"UPDATE `tabShift Type` SET last_sync_of_checkin = '{now}' WHERE name = '{shift}'"
                        )
                        frappe.log_error("error", frappe.get_traceback())
                    # if shift_doc.enable_auto_attendance:
                    # 	shift_doc.process_auto_attendance()
    except Exception:
        frappe.log_error("shift_sync_checkin", frappe.get_traceback())


@frappe.whitelist(allow_guest=True)
def indiamart_rocotile_sync():
    data = frappe.local.form_dict
    d = data["RESPONSE"]
    query_type = {
        "W": "Direct & ASTBUY Enquiries",
        "B": "Buy-Leads",
        "P": "PNS Calls",
        "V": "Catalog-view Leads",
        "BIZ": "Catalog-view Leads",
        "WA": "WhatsApp Enquiries",
    }
    code = d["SENDER_COUNTRY_ISO"]
    country = frappe.db.get_value("Country", {"code": code.lower()})
    frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": d.get("SENDER_NAME"),
            "source": "Indiamart",
            "custom_inquiry_type": query_type.get(d["QUERY_TYPE"])
            if d.get("QUERY_TYPE")
            else "",
            "custom_im_query_id": d.get("UNIQUE_QUERY_ID"),
            "email_id": d["SENDER_EMAIL"] if d.get("SENDER_EMAIL") else "",
            "lead_status": "Open",
            "custom_sender_company": d["SENDER_COMPANY"],
            "country": country if country else "",
            "city": d["SENDER_CITY"],
            "state": d["SENDER_STATE"],
            "custom_product_name": d["QUERY_PRODUCT_NAME"],
            "custom_subject": d["SUBJECT"],
            "custom_message": d["QUERY_MESSAGE"],
            "custom_address": d["SENDER_ADDRESS"],
            "custom_pincode": d["SENDER_PINCODE"] if d.get("SENDER_PINCODE") else "",
            "custom_product_enquired": "Rocotile",
            "custom_customer_category": "B2B",
            "custom_call_duration": d["CALL_DURATION"],
            "mobile_no": d["SENDER_MOBILE"],
            "whatsapp_no": d["SENDER_MOBILE"][4:]
            if (d.get("SENDER_MOBILE")[0:4] == "+91-")
            else d["SENDER_MOBILE"],
        }
    ).insert(ignore_permissions=True, ignore_mandatory=True)


@frappe.whitelist(allow_guest=True)
def indiamart_bioman_sync():
    data = frappe.local.form_dict
    d = data["RESPONSE"]
    query_type = {
        "W": "Direct & ASTBUY Enquiries",
        "B": "Buy-Leads",
        "P": "PNS Calls",
        "V": "Catalog-view Leads",
        "BIZ": "Catalog-view Leads",
        "WA": "WhatsApp Enquiries",
    }
    code = d["SENDER_COUNTRY_ISO"]
    country = frappe.db.get_value("Country", {"code": code.lower()})
    frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": d.get("SENDER_NAME"),
            "source": "Indiamart",
            "custom_inquiry_type": query_type.get(d["QUERY_TYPE"])
            if d.get("QUERY_TYPE")
            else "",
            "custom_im_query_id": d.get("UNIQUE_QUERY_ID"),
            "email_id": d["SENDER_EMAIL"] if d.get("SENDER_EMAIL") else "",
            "lead_status": "Open",
            "custom_sender_company": d["SENDER_COMPANY"],
            "country": country if country else "",
            "city": d["SENDER_CITY"],
            "state": d["SENDER_STATE"],
            "custom_product_name": d["QUERY_PRODUCT_NAME"],
            "custom_subject": d["SUBJECT"],
            "custom_message": d["QUERY_MESSAGE"],
            "custom_address": d["SENDER_ADDRESS"],
            "custom_pincode": d["SENDER_PINCODE"] if d.get("SENDER_PINCODE") else "",
            "custom_product_enquired": "Bioman",
            "custom_customer_category": "B2B",
            "custom_call_duration": d["CALL_DURATION"],
            "mobile_no": d["SENDER_MOBILE"],
            "whatsapp_no": d["SENDER_MOBILE"][4:]
            if (d.get("SENDER_MOBILE")[0:4] == "+91-")
            else d["SENDER_MOBILE"],
        }
    ).insert(ignore_permissions=True, ignore_mandatory=True)
