# Installation
There are two ways Ancile can be deployed locally (for development) or on a
remote deployment for actual use.

### Rolling pre-req list:
- libpq-dev

### Pre-reqs
0. Tested on: Arch Linux, Ubuntu 18.04, OSX Mojave
1. Python 3.7+
    - python3 venv
    - python devtools
2. [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04).
   Ensure that the `docker run hello-world` command works properly before
   proceeding

### Remote Pre-reqs
1. Certbot
2. NGINX

### Initial installation
From the top directory run `bash scripts/full_setup.sh`, this will assemble
the virtual environment, docker containers, log folder, and configuration
file templates needed to run ancile. If there are any errors, the process
can be reversed by running `bash scripts/teardown.sh`. Please note that this
will delete the configuration files and database. If docker is running
slowly, the migrations can sometimes fail, if this occurs try running them
separately with `bash scripts/setup/run_migrations.sh`.

Note: If python 3.7 is not the default python3 installation on the system, adjust the
`scripts/setup/setup_env.sh` to use `python3.7` instead of `python3` (or the appropriate
name on the system).

Note2: If you don't have Python3.7 on your machine, use 
[MiniConda](https://docs.conda.io/en/latest/miniconda.html) (that should give 
you `base` environment with Python3.7) and activate it `conda activate base`. 
Then rerun `bash scripts/full_setup.sh` (you might need to do `teardown.sh` 
first). This is the cheapest way to get dependencies installed and you don't
need to modify scripts (although you will see an error: `source: not found`)

### Configuration
In `config.yaml` change the values for:
- SECRET_KEY - generate a secure random string

#### Local Development
Nothing needs to be changed from the defaults

#### Deployment
- Change SERVER name to the hostname ex: "ancile.cs.vassar.edu"
- Change SERVER_DEBUG to false

#### Optional Configs
- LOGGING (default True): Setting to t/f enables or disables logs
- CACHE (default False): Setting to t/f enables or disables caching of user info and 
compiled programs

### Create a super user
From the ancile directory run:
```
source .env/bin/activate
python manage.py createsuperuser
```
and follower the prompts.

### Running the server locally
To run the server locally use `bash scripts/start_dev_server.sh`. This will run the server
and host the static files, but is not suitable for the deployment. When running this way
ensure `SERVER_DEBUG` is true. This will also make the \djadmin route available to assist
in development.

### Setup SSL and NGINX for remote deployment
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
                proxy_set_header X-Forwarded-Proto $scheme;
	}
```

Finally, we need to serve our static files by directing NGINX to them. Add the following
to the 443 server block.
```
	location /static/ {
		alias /HOME/ancile/ancile/web/static/;
	}
```

### Collect static files for deployment
Once NGINX is configured the static files can be collected. This is done by running
```
source .env/bin/activate
python manage.py collectstatic
```
from the ancile directory.

### (optional) Setup Supervisor [recommended for remote]
Setting up a supervisor process to run the server is recommended. First install
supervisor with `sudo apt-get install supervisor` (on debian based systems),
for other systems see their [site](http://supervisord.org/installing.html).

Create a new file in `/etc/supervisor/conf.d/` called `ancile`. Edit it such
that it contains the following:
```
[program:ancile]
command=bash scripts/start_prod_server.sh
directory=PATH_TO_ANCILE/ancile
user=YOUR_USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

Ancile can now be run with `sudo supervisorctl start ancile` and should reboot
on system start.

If necessary, the production server can be run in a terminal window with 
`bash scripts/start_prod_server.sh`
