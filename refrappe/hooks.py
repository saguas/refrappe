# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "refrappe"
app_title = "Reaction Ecommerce"
app_publisher = "Luis Fernandes"
app_description = "Reaction Ecommerce"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "luisfmfernandes@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/refrappe/css/refrappe.css"
# app_include_js = "/assets/refrappe/js/refrappe.js"

# include js, css files in header of web template
# web_include_css = "/assets/refrappe/css/refrappe.css"
# web_include_js = "/assets/refrappe/js/refrappe.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
#home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }


on_logout = "refrappe.utils.users.on_logout"


# Website user home page (by function)
get_website_user_home_page = "refrappe.utils.get_home_page"
#website_route_rules = [
#	{"from_route": "/cfs/<path:name>", "to_route": "http://localhost:3000/cfs/servertime"},
	#{"from_route": "/update-password", "to_route": "/index"}
#]
#/cfs/

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "refrappe.install.before_install"
after_install = "refrappe.utils.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "refrappe.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"User": {
#		"validate": "refrappe.utils.users.validate",
 		"on_trash":	"refrappe.utils.users.on_trash",
		"after_insert":	"refrappe.utils.users.mongodb_insert_user"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"refrappe.tasks.all"
# 	],
# 	"daily": [
# 		"refrappe.tasks.daily"
# 	],
# 	"hourly": [
# 		"refrappe.tasks.hourly"
# 	],
# 	"weekly": [
# 		"refrappe.tasks.weekly"
# 	]
# 	"monthly": [
# 		"refrappe.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "refrappe.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.core.doctype.user.user.update_password": "refrappe.utils.users.update_password",
	"frappe.core.doctype.user.user.verify_password": "refrappe.utils.users.verify_password",
	"frappe.core.doctype.user.user.test_password_strength": "refrappe.utils.users.test_password_strength"
}
