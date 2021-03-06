import hashlib
import frappe
import bcrypt
import json
import os


ROUNDS = 10
REACTIONDB = "meteor"

bcrypt_prefix = None
reaction_web_client = None
BASE64_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"


def get_mongo_id(n=17):
	from random import choice

	id = []
	for i in range(n):
		id.append(choice(BASE64_CHARS))

	return "".join(id)


def get_reaction_bcrypt_prefix():
	global bcrypt_prefix

	if bcrypt_prefix:
		return bcrypt_prefix

	common_config = frappe.get_file_json("common_site_config.json")
	site_path = frappe.get_site_path()
	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	_bcrypt_prefix = site_config.get("BCRYPT_PREFIX") or common_config.get("BCRYPT_PREFIX") or '2a'

	bcrypt_prefix = bytes(_bcrypt_prefix)

	return bcrypt_prefix



def is_from_reaction(data=None):
	# Here we get from frappe first and if not present the from data (the default)
	# frappe parameter is in the case frappe use data. For instance in the case of create user API request.
	data = data or frappe.local.form_dict.frappe or frappe.local.form_dict.data
	if data:
		obj = json.loads(data)
		if isinstance(obj, dict):
			efrappe = obj.get("efrappe")
			if efrappe:
				origin = efrappe.get("origin")
				if origin == "efrappe":
					frappe.local.flags.is_from_efrappe = True
					return True
	frappe.local.flags.is_from_efrappe = False
	return False

def hashpw(pwd):
	m = hashlib.sha256()
	m.update(pwd)
	hexpass = m.hexdigest()

	return hexpass


def bcrypt_hashpw(pwd):
	hexpass = hashpw(pwd)
	bcrypt_prefix = get_reaction_bcrypt_prefix()
	return bcrypt.hashpw(hexpass, bcrypt.gensalt(rounds=ROUNDS, prefix=bcrypt_prefix))


def bcrypt_only(hexpass):
	bcrypt_prefix = get_reaction_bcrypt_prefix()
	return bcrypt.hashpw(hexpass, bcrypt.gensalt(rounds=ROUNDS, prefix=bcrypt_prefix))


def pwd_compare(pwd_sha256, bcrypt_hash):
	return bcrypt.hashpw(pwd_sha256, bcrypt_hash) == bcrypt_hash


def get_userId(email):
	client = get_mongo_client()
	db = client[REACTIONDB]
	users = db.users
	user = users.find_one({"emails.address": {"$in": [email]}})
	if user:
		return user._id
	return

def get_mongo_client():
	import refrappe as rc
	return rc.get_mongo_cli()


def get_mongo_db():
	client = get_mongo_client()
	return client[REACTIONDB]


def get_mongo_user_password(username):
	db = get_mongo_db()
	users = db.users
	user = users.find_one({"emails.address":{"$in": [username]}})
	if user:
		return user.get("services").get("password").get("bcrypt")

	return None


def validate(doc, method=None):
	"""
		Validate users inserts and updates. Hash + bcrypt password for compatibility with reaction ecommerce app.
		Call reaction to create user in mongodb.
	"""
	print "validate doc {} method {}".format(doc, method)
	if doc.get("__islocal"):#this is an insert
		return
	else:#this is an update. Check if password has changed
		from frappe.utils.password import check_password
		#userdoc = frappe.get_all("User", fields=["name", "password"], filters = {"name":doc.name})
		None
	return


def on_trash(doc, method=None):
	#remove from mongodb user.email.
	if is_from_reaction():
		return

	print "removed user {} method {}".format(doc.email, method)
	db = get_mongo_db()
	db.users.delete_one({"emails.address": {"$in": [doc.email]}})




@frappe.whitelist(allow_guest=True)
def update_password(new_password, key=None, old_password=None):
	from frappe.core.doctype.user.user import update_password as update_pwd, _get_user_for_update_password

	print "update password new {}".format(new_password)
	original_old_password = old_password

	if old_password and not is_from_reaction():
		old_password = hashpw(old_password)

	if not is_from_reaction():
		new_password = hashpw(new_password)
		res = _get_user_for_update_password(key, original_old_password)
		mongodb_update_password(res['user'], new_password)

	url = update_pwd(new_password, key, old_password)

	return url


@frappe.whitelist(allow_guest=False)
def reset_password(email, new_password):
	print "resetPassword email {} new_password {}".format(email, new_password)
	frappe.only_for("Administrator")
	if email:
		from frappe.utils.password import update_password
		#user = frappe.get_doc("User", email)
		update_password(email, new_password)

"""
@frappe.whitelist(allow_guest=True)
def update_password(new_password, key=None, old_password=None):
	from frappe.core.doctype.user.user import update_password as update_pwd

	print "in update_password form_dict: {}".format(frappe.local.form_dict)
	def user_callback(error, result):
		if error:
			print "error for creteFrappeUser {}".format(error)
		else:
			print "result for creteFrappeUser {}".format(result)

	orinal_new_pwd = new_password
	#orinal_old_pwd = old_password

	first_time = True

	if old_password:
		old_password = hashpw(old_password)
		first_time = False


	new_password = hashpw(new_password)

	url = update_pwd(new_password, key, old_password)

	if first_time and frappe.session.user != "Guest":
		#user has login
		#create user in reaction ecommerce
		import meteor_ddp as ddp
		user = get_user_for_update_password(key, old_password)
		if user:
			ddp.create_meteor_user(user.email, orinal_new_pwd, user.username, user_callback)
	elif frappe.session.user != "Guest":
		#change password
		import meteor_ddp as ddp

		user = get_user_for_update_password(key, old_password)
		if user:
			userId = get_userId(user.email)
			if userId:
				ddp.change_user_password(userId, orinal_new_pwd, user_callback)


	return url
"""

@frappe.whitelist()
def verify_password(password):
	from frappe.core.doctype.user.user import verify_password as verify_pwd

	password = hashpw(password)
	return verify_pwd(password)


@frappe.whitelist(allow_guest=True)
def test_password_strength(new_password, key=None, old_password=None):
	from frappe.core.doctype.user.user import test_password_strength as test_pwd_strength

	if old_password:
		old_password = hashpw(old_password)

	new_password = hashpw(new_password)

	return test_pwd_strength(new_password, key, old_password)


#on_logout {'items': u'["luisfernandes@eapelacao.pt"]', 'cmd': u'frappe.desk.reportview.delete_items', 'doctype': u'User'}
#on_logout {'cmd': u'logout', 'data': '{"efrappe":{"origin":"efrappe"}}'}
def on_logout():
	print "on_logout {}".format(frappe.local.form_dict)
	if frappe.session.user == "Guest":
		print "user Guest, do nothing!!"
		return
	"""
	data = frappe.local.form_dict.data
	if data:
		obj = json.loads(data)
		if isinstance(obj, dict):
			origin = obj.get("efrappe").get("origin")
			if origin == "efrappe":
				return
	"""
	if is_from_reaction():
		return
	#logout from frappe desk
	db = get_mongo_db()
	#if some user is remove, he is logged out by frappe and cmd is 'frappe.desk.reportview.delete_items' and doctype is 'User'
	#{'items': u'["someusername@domain.xxx"]', 'cmd': u'frappe.desk.reportview.delete_items', 'doctype': u'User'}
	if frappe.local.form_dict.cmd == 'frappe.desk.reportview.delete_items' and frappe.local.form_dict.doctype == 'User':
		items = frappe.local.form_dict.get("items")
		if isinstance(items, basestring):
			items = json.loads(items)
		for email in items:
			db.users.update_one({"emails.address": {"$in": [email]}}, {"$set": {"profile.frappe_login": False}})
		return

	email = frappe.session.user
	if email == "Administrator":
		user = frappe.get_doc("User", email)
		email = user.email

	db.users.update_one({"emails.address": {"$in": [email]}}, {"$set": {"profile.frappe_login": False}})
	"""
	from frappe.auth import CookieManager
	from werkzeug.wrappers import Response
	response = Response()
	cookie_manager = CookieManager()

	cookie_manager.delete_cookie(["full_name", "user_id", "sid", "user_image", "system_user"])
	cookie_manager.flush_cookies(response)

	cookies = []
	for h in response.headers:
		cookies.append(h[1]) if h[0].startswith("Set-Cookie") else None

	#print "response cookies {}".format(cookies)

	def user_callback(error, result):
		if error:
			print "error for logoutuser {}".format(error)
		else:
			print "result for logoutuser {}".format(result)
	"""
	#frappe Admin must have the same address of reaction admin
	#db.users.update_one({"emails.address": {"$in": [email]}}, {"$set":{"profile.cookies": cookies}})
	#import meteor_ddp as ddp
	#try:
	#	ddp.logoutuser(email, None)
	#except Exception as e:
	#	print "logout user {} error: {}".format(email, e)


# see frappe.client.insert
"""
frappe.client.insert

{"docstatus":0,"doctype":"User","name":"New User 1","__islocal":1,"__unsaved":1,"owner":"Administrator"
,"enabled":1,"send_welcome_email":0,"language":"pt","gender":"","thread_notify":1,"background_style"
:"Fill Screen","simultaneous_sessions":1,"user_type":"System User","__run_link_triggers":1,"email":"luisfmfernandes
@icloud.com","first_name":"Luis","last_name":"icloud"}

"""
"""
@frappe.whitelist()
def insert_user(doc):
	if isinstance(doc, basestring):
		doc = json.loads(doc)

	# this is necessary because we have a hook in User inserts. If is_from_efrappe=True don't insert user in mongodb in User insert hook.
	frappe.local.flags.is_from_efrappe = True

	doc = frappe.get_doc(doc).insert()

	frappe.local.flags.is_from_efrappe = False

	return doc.as_dict()
"""

#update mongodb password for user
def mongodb_update_password(user, hexpass):
	bcrypt_pwd = bcrypt_only(hexpass)
	db = get_mongo_db()
	db.users.update_one({"emails.address": {"$in": [user]}}, {"$set": {"services.password.bcrypt": bcrypt_pwd}})

#insert user on mongodb. We need update password yet.
def mongodb_insert_user(doc, method):
	#if flag is True user already inserted in mongodb.
	print "mongodb_insert_user form_dict {}".format(frappe.local.form_dict)
	if is_from_reaction():
		return

	import datetime

	#from bson.objectid import ObjectId


	user = frappe._dict({})

	#objid = ObjectId()
	#user._id = str(objid)
	user._id = get_mongo_id()
	user.emails = [
			{"address" : doc.email,
				"verified" : True,
				"provides" : "default"
			}
		]

	user.createdAt = datetime.datetime.utcnow()
	user.username = doc.username or doc.name
	user.services = {
		"password": {
			"bcrypt": ""
		},
		"resume": {
			"loginTokens": []
		}
	}

	user.profile = {
		"frappe_login": False
	}
	db = get_mongo_db()

	host = frappe.local.request.host.split(":")
	domain = host[0]
	if domain and domain.startswith('www.'):
		domain = domain[4:]

	shop = db.Shops.find_one({"domains": domain})
	shopid = shop.get("_id")
	user.roles = {}
	user.roles[shopid] = [
			"account/profile",
			"guest",
			"product",
			"tag",
			"index",
			"cart/checkout",
			"cart/completed"
		]

	db.users.insert_one(user)



@frappe.whitelist(allow_guest=True)
def get_logged_user():
	return frappe.session.user