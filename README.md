# Ancile


Documentation for Ancile: 


## Deployment

1. Setup
   [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04).
   Make sure that the `docker run hello-world` command works properly before
   proceeding.
2. From the top directory run `bash scripts/full_setup.sh`, this will assemble
   the virtual environment, docker containers, log folder, and configuration
   file templates needed to run ancile. If there are any errors, the process
   can be reversed by running `bash scripts/teardown.sh`. Please note that this
   will delete the configuration files and database. If docker is running
   slowly, the migrations can sometimes fail, if this occurs try running them
   separately with `bash scripts/setup/run_migrations.sh`.
3. Go to the config directory (`cd config`) and make edits to `config.yaml` and
   `oauth.yaml` both files will have been preloaded with some default values.
4. In `config.yaml` change the values for :
      - SERVER_NAME - ex: "ancile.cs.vassar.edu"
      - SECRET_KEY - generate a secure random string
      - SECURITY_PASSWORD_SALT - generate a secure random string
      - MAIL_SERVER - machine-dependent
      - MAIL_PORT - machine-dependent
      - MAIL_USERNAME - machine-dependent
      - MAIL_PASSWORD - machine-dependent
      - SECURITY_EMAIL_SENDER - ex: "ancile@ancile.cs.vassar.edu"
5. In `oauth.yaml` replace the values with your client IDs and secrets

### Create an admin user
Once the basic setup is done you can create an admin user by running the
following from the ancile directory.
```
source .env/bin/activate
python
import app
```
At this point you can run the `app._gen_admin(EMAIL)` function in the python
interpreter which will take the email of the admin user and return their
randomly generated password. Copy the password and store it somewhere. You may
change it later as needed.

You can now close the python interpreter

### (optional) Running Locally
The default configuration will work locally though registration will require
running an email server on the host machine. This can be done with minimal
difficulty.
```
python3 -m venv .env
source .env/bin/activate
pip install aiosmtpd
aiosmtpd -n
```
This will run a local mail server and capture any attempted output by Ancile
which can be used to grab the registration links while testing.

### (optional) Configure logging and cache
In the `config.yaml` file, you can enable caching or disable logging by editing
their respective entires under the `operational` section. By default caching is
turned off and logging is turned on.

### Deployment Setup
Use LetsEncrypt to get SSL certificates for the server and place NGINX in front
of Ancile. Redirect all requests through NGINX to the Ancile webserver.

## Running Ancile
Once everything is setup Ancile can be started by running:
```
bash scripts/start_server.sh
```
Setting up a supervisor process is recommended.
## Unit Tests:
To run the python unit tests:
```
ancile$  python -m unittest
```



## Development 

Let's just review each others code and verify that it works. 

Ideally, we will need to have better testing, but will see how it goes. 
