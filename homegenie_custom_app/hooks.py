from . import __version__ as app_version

app_name = "homegenie_custom_app"
app_title = "Homegenie"
app_publisher = "Homegenie"
app_description = "Custom Fields"
app_email = "test@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/homegenie_custom_app/css/homegenie_custom_app.css"
# app_include_js = "/assets/homegenie_custom_app/js/homegenie_custom_app.js"
# app_include_js = ["/assets/homegenie_custom_app/js/custom_script.js"]

# include js, css files in header of web template
# web_include_css = "/assets/homegenie_custom_app/css/homegenie_custom_app.css"
# web_include_js = "/assets/homegenie_custom_app/js/homegenie_custom_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "homegenie_custom_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Customer" : "public/customer/customer.js",
    "Maintenance Visit":"public/customer/customer.js",
    "Event":"public/event/event.js",
    "Issue":"public/customer/customer.js",
    "Company":"public/js/company.js",
    "Sales Invoice":"public/js/sales_invoice.js",
    "Installation Note":"public/js/installation_note.js",
    "Customer": "public/js/customer.js",
    "Job Applicant": "public/js/job_applicant.js",
    "Razorpay Settings": "public/js/razorpay_setting.js",
    }
   
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

fixtures=[
    # "Labour Attendance Tool","Order Confirmation Form","Order Form Item","ERF Item Table","Estimation Request Form","Labour Attendance","Labours",
    # {"doctype":"Custom DocPerm"},
    {"doctype":"Custom Field", "filters":{"module": ["in", ["Homegenie"]]}},
    {"doctype":"Property Setter", "filters":{"module": ["in", ["Homegenie"]]}},
    # {"doctype":"Client Script","filters":[["module", "=", "Homegenie"]]}
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "homegenie_custom_app.utils.jinja_methods",
#	"filters": "homegenie_custom_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "homegenie_custom_app.install.before_install"
# after_install = "homegenie_custom_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "homegenie_custom_app.uninstall.before_uninstall"
# after_uninstall = "homegenie_custom_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "homegenie_custom_app.utils.before_app_install"
# after_app_install = "homegenie_custom_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "homegenie_custom_app.utils.before_app_uninstall"
# after_app_uninstall = "homegenie_custom_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "homegenie_custom_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Quotation": {
        "on_submit":"homegenie_custom_app.homegenie.doctype.installation_request.installation_request.get_connection_of_quo_to_ir"
	},
    "Installation Note":{
        "on_submit":"homegenie_custom_app.homegenie.api.get_connection_of_si_to_ins",
        "on_change":"homegenie_custom_app.homegenie.api.technician_validation"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"cron": {
		"*/30 * * * *" : [
			"homegenie_custom_app.homegenie.api.shift_sync_checkin"
		]
    }
}
# scheduler_events = {
#	"all": [
#		"homegenie_custom_app.tasks.all"
#	],
#	"daily": [
#		"homegenie_custom_app.tasks.daily"
#	],
#	"hourly": [
#		"homegenie_custom_app.tasks.hourly"
#	],
#	"weekly": [
#		"homegenie_custom_app.tasks.weekly"
#	],
#	"monthly": [
#		"homegenie_custom_app.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "homegenie_custom_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "homegenie_custom_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "homegenie_custom_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

ignore_links_on_delete = ["Quotation","Installation Request"]
# ignore_links_on_cancel = ["Quotation","Installation Request"]

# Request Events
# ----------------
# before_request = ["homegenie_custom_app.utils.before_request"]
# after_request = ["homegenie_custom_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["homegenie_custom_app.utils.before_job"]
# after_job = ["homegenie_custom_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"homegenie_custom_app.auth.validate"
# ]
