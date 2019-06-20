# Ancile


Documentation for Ancile:


# Deployment Process
There are two ways Ancile can be deployed locally (for development) or on a
remote deployment for actual use.

### Pre-reqs
0. Tested on: Arch Linux, Ubuntu 18.04, OSX Mojave
1. Python 3.6+
    - python3 venv
    - python devtools
2. [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04).
   Ensure that the `docker run hello-world` command works properly before
   proceeding

### Remote Pre-reqs
1. Certbot
2. NGINX

### Intial installation
From the top directory run `bash scripts/full_setup.sh`, this will assemble
the virtual environment, docker containers, log folder, and configuration
file templates needed to run ancile. If there are any errors, the process
can be reversed by running `bash scripts/teardown.sh`. Please note that this
will delete the configuration files and database. If docker is running
slowly, the migrations can sometimes fail, if this occurs try running them
separately with `bash scripts/setup/run_migrations.sh`.


### Editing the secrets
In `config.yaml` change the values for:
- SECRET_KEY - generate a secure random string
- SECURITY_PASSWORD_SALT - generate a secure random string

Use your favorite locally sourced randomness and generate these strings before
proceeding.

We will come back to the configs shortly.

### Setup the roles and sample users (both)
Once you've setup the secret keys, run:
```
bash scripts/setup/role_setup.sh
```
This will configure the system roles and generate three sample users:
- username: admin, password: password, role: admin
- username: user, password: user_password, role: user
- username: app, password: app_password, role: app

### Edit the configs for local work
At this point the configs are properly configured for running ancile locally
without an email server. If you wish to use an email server, see the
instructions below. The `SERVER_NAME` config must be left blank for the local
instance to function.

### Edit the configs for remote work
If running the server on a remote machine meant to be accessed over the
internet, you will need to change the `SERVER_NAME` variable to the domain name
of your server, ex: "ancile.cs.vassar.edu".

### Configure Mail Server (remote) [recommended]
If available, running the ancile deployment with email validation is
recommended. The following config values will need to be adjusted with the
information of your mail server:
- MAIL_SERVER
- MAIL_PORT
- MAIL_USERNAME
- MAIL_PASSWORD

Next you'll need to adjust `SECURITY_EMAIL_SENDER` to match your deployment
information. Ex: "ancile@ancile.cs.vassar.edu".

### Configure Mail Server (locally)
No additional configuration needs to be done to run ancile with a local
email. You will however need to run a local email server by:
```
python3 -m venv .env
source .env/bin/activate
pip install aiosmtpd
aiosmtpd -n
```
This will capture any emails that Ancile sends, so that the links can be used
for local testing and verification. It will not, however, actually send any
email.

### Enable email (optional)
To enable the confirmation and email features of the server, change the
following configuration variables to true:
- SECURITY_CONFIRMABLE
- SECURITY_SEND_REGISTER_EMAIL
- SECURITY_SEND_PASSWORD_CHANGE_EMAIL
- SECURITY_SEND_PASSWORD_RESET_EMAIL
- SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL

This will require users to confirm their email before they can log in and will
configure the deployment to send email.

### Operational configuration
The info logs can be disabled by changing the `LOGGING` configuration value to
False. To disable access logs, run the server using
`bash scripts/start_server_no_logs.sh`. 

The redis cache can be enabled by changing the `CACHE` configuration value to
True.


### Setup SSL and Reverse Proxy (remote)
For remote setups, Ancile requires the use of a reverse proxy and SSL
certificates.

First install
[NGINX](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/)
on your system.
Then install
[certbot](https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx.html).

Once certbot is installed, run `sudo certbot --nginx` to get SSL certificates
for your domain. This will also add some configuration to NGINX automatically.

Then you need to configure NGINX to redirect traffic to the local server. 
First ensure that all traffic is redirected to 443 with a block like:
```
server {
	listen 80 default_server;
	listen [::]:80 default_server;
	
	server_name YOUR_DOMAIN_GOES_HERE_AND_REPLACES_THIS_TEXT;
	return 301 https://$server_name$request_uri;
}
```

Add the following to your 443 server block which certbot should have created:
```
location / {
		# First attempt to serve request as file, then
		# as directory, then fall back to displaying a 404.
                proxy_pass http://localhost:8000;
                proxy_redirect off;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
```

### (optional) Setup Supervisor [recommended for remote]
Setting up a supervisor process to run the server is recommended. First install
supervisor with `sudo apt-get install supervisor` (on debian based systems),
for other systems see their [site](http://supervisord.org/installing.html).

Create a new file in `/etc/supervisor/conf.d/` called `ancile`. Edit it such
that it contains the following:
```
[program:ancile]
command=bash scripts/start_server.sh
directory=PATH_TO_ANCILE/ancile
user=YOUR_USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

Ancile can now be run with `sudo supervisorctl start ancile` and should reboot
on system start.

### Running Ancile
Once everything is setup Ancile can be started in a local terminal by running:
```
bash scripts/start_server.sh
```
This will start the server locally on port 8000. If running locally you can now
access the deployment. If running on a remote machine, ensure that the NGINX
configurations upgrade connections to SSL and redirect requests to the gunicorn
server.


### Change admin user password
Once the server is running, the password to the admin user should be changed
from the web interface.


## Unit Tests:
To run the python unit tests:
```
ancile$  python -m unittest
```

## Development 

Let's just review each others code and verify that it works. 

Ideally, we will need to have better testing, but will see how it goes. 
