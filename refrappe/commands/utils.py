#!/usr/bin/python
# -*- coding: latin-1 -*-

from __future__ import unicode_literals, absolute_import
import click



@click.command('nginx')
def nginx():
	info = """
		Add the following at the top of nginx.conf file after upstream frappe-bench-frappe and upstream frappe-bench-socketio-server

		upstream meteor-reaction {
			server 127.0.0.1:3000 fail_timeout=0;
		}

		map $http_upgrade $connection_upgrade {
		  default upgrade;
		  ''      close;
		}

		proxy_buffers 4 256k;
		proxy_buffer_size 128k;
		proxy_busy_buffers_size 256k;

		Add the following to server module:

		location ~ /reaction|/cfs|/packages|/sockjs {
			try_files /assets/refrappe/eweb/public/$uri /assets/refrappe/eweb/$uri @reaction;
		}

		location =/reaction/desk {
			rewrite ^/reaction/desk$ /desk redirect;
		}

		location ~ /login {
			if ($request_method = POST){
			  error_page 418 = @webserver;
			  return 418;
			}

			try_files /assets/refrappe/eweb/public/$uri /assets/refrappe/eweb/$uri @reaction;
		}

		location @reaction {
			proxy_set_header X-Forwarded-For $remote_addr;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header Host $host;
			proxy_http_version 1.1;
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection $connection_upgrade;
			add_header Cache-Control no-cache;
			proxy_pass  http://meteor-reaction;
		}

		Add the following to location / before @webserver and after try_files /your site name/public/$uri:

		/assets/refrappe/websrc/$uri /assets/refrappe/eweb/public/$uri /assets/refrappe/eweb/$uri;

		Note: when you are done do not forget to restart nginx
	"""

	print info


@click.command('before_start')
def before_start():
	info = """
		first:
			You need to correlate your frappe admin password with reaction admin password. So
			please run:
				bench refrappe set-admin-password

		second:
			install reaction_cli command line app:

				npm install -g reaction-cli

		third:
			The following is necessary for reaction to make url properly
			export ROOT_URL="http://localhost" ; make it permanente (~/.bash_profile) for instance

			Then:

			run bench refrappe nginx to see how to config nginx for reaction ecommerce app

		fourth:
			Go to refrappe/www/webreaction/settings folder and fill in some fields of dev.settings.json file:
			This example is for gmail and localhost, some were update be first step.

			{
			  "FRAPPE_URL": "http://localhost",
			  "DDP_DEFAULT_CONNECTION_URL": "http://localhost:3000/",
			  "ROOT_URL": "",
			  "MONGO_URL": "",
			  "MAIL_URL": "smtp://admin email address here@gmail.com:your_password_here@smtp.gmail.com:465/",
			  "reaction": {
				"REACTION_USER": "admin",
				"REACTION_AUTH": "admin password here",
				"REACTION_EMAIL": "reaction admin email here, same as frappe admin email",
			  },
			  "frappe":{
				"FRAPPE_ADMIN_USERNAME": "Administrator",
				"FRAPPE_URL": "http://localhost"
			  },
			  "isDebug": "info",
			  "public": {}
			}


			Note 1: FRAPPE_URL is the url of nginx.
			Note 2: DDP_DEFAULT_CONNECTION_URL is the url where is reaction ecommerce listen.
			Note 3: The administrator must have the same email address as the administrator of reaction ecommerce app
					You can change the frappe administrator email in setup/user menu.

		Note:
			If you already started reaction ecommerce before to do this changes in settings you must stop it and run it again with the following command:
				reaction reset (note: answer no to the question to reinstall npm packages)

		fifth:
			 In sites/common_site_config.json check if every thing is correct and accordling your case:

			Some fields was setting after installing this aplication:

			 "reaction_server": "http://localhost:3000",
			 "reaction_webapp_path": "../apps/refrappe/refrappe/www/webreaction",
			 "ROOT_URL":"http://localhost:3000",
			 "ROOT_URL_PATH_PREFIX":"",
			 "DDP_DEFAULT_CONNECTION_URL":"http://localhost:3000/",
			 "MONGOWEB":{
			   "host": "localhost",
			   "port": "3001"
			 }

		sixth:
			In one terminal cd frappe_bench folder and do bench start
			In another terminal from frappe_bench folder do cd apps/refrappe/refrappe/www/webreaction and issue reaction
			In your browser go to http://localhost or the url where is your nginx listening.

	"""

	print info


@click.command('after_start')
def after_start():
	info = """

		Every time you need to change admin password you must run bench refrappe set-admin-password.


		The meteor reaction ecommerce must be updated by you every time you need with the command reaction pull.
		Your app must go to inside imports/plugins/custom folder like efrappe folder, and you should git init.
		To share your app you just need to provide your git url and the other part git clone your app.


		For reaction help/tutorial go to: https://docs.reactioncommerce.com for more info.

		For meteor help/tutorial go to: https://www.meteor.com for more info.

		Or to meteor api: http://docs.meteor.com/#/full/


		Enjoy.
		Lu�s Fernandes

	"""

	print info



commands = [
	nginx,
	before_start,
	after_start,
]
