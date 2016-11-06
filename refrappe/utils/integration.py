
import frappe
from frappe.utils import oauth



@frappe.whitelist(allow_guest=False)
def getIntegrationToken(provider):
	frappe.only_for("Administrator")
	state = {"site": frappe.utils.get_url(), "token": frappe.generate_hash()}
	frappe.cache().set_value("{0}:{1}".format(provider, state["token"]), True, expires_in_sec=120)

	return state

"""
#Not in use
@frappe.whitelist(allow_guest=True)
def login_oauth_user(data=None, provider=None, state=None, email_id=None, key=None, generate_login_token=False):
	from frappe.www.login import login_oauth_user as original_login_oauth_user

	print "login_oauth_user generate_login_token {}".format(generate_login_token)
	res = original_login_oauth_user(data, provider, state, email_id, key, generate_login_token)
	#frappe.local.response["type"] = ""

	return res


#Not in use
@frappe.whitelist(allow_guest=True)
def login_via_token(login_token):
	from frappe.www.login import login_via_token as original_login_token
	from frappe.auth import clear_cookies

	res = original_login_token(login_token)
	#frappe.local.response["type"] = ""
	#clear_cookies()

	return res

"""