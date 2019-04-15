# Ancile


Documentation for Ancile: 


## Deployment

I think it's a good start to deploy Ancile locally first
and then move to the server version. Steps are similar 
except you need to obtain certificates differently. 

1. Setup [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04), [Elixir](https://elixir-lang.org/install.html) and [Node.JS](https://nodejs.org/en/download/package-manager/).
1. Install postgresql: `pip install postgres`.
1. Fetch dependencies: `mix deps.get` and build the project: `mix`.
1. Get SSL certificates (run `mix phx.gen.cert` locally and use LetsEncrypt remotely)
   1. For the local deployment just check SSL location in `dev.exs`
   1. Create empty `dev.secret.exs`. For remote deployment put the following config: 
   
        ```elixir
        config :ancile, AncileWeb.Endpoint,
          http: [port: 4000],
           https: [
              port: 4001,
              cipher_suite: :strong,
              keyfile: "/home/ubuntu/certs/privkey.pem",
              cacertfile: "/home/ubuntu/certs/chain.pem",
              certfile: "/home/ubuntu/certs/cert.pem"
               ],
           url: [
             host: "{your_hostname}"]
       ```
   1. Don't try to commit `dev.secret.exs`, as then we can have separate deployments
    running Ancile without code conflicts and will keep our keys private.
 
1. Add integration of Data Providers using configs from 
[LINK](https://github.com/ebagdasa/pow_assent)
(ask Eugene for help, ideally we should move it inside Ancile later)
   1. Register an app on CDS/GitHub/Azure
   1. You can have same apps for both desktop and 
   remote deployment, just make sure to update CallBack URL accordingly.
    Create/Modify `dev.secret.exs` and append the following config: 
   
        ```elixir
        config :ancile,
               :pow_assent,
               providers: [
                 github: [
                   client_id: "client_id",
                   client_secret: "client_secret",
                   strategy: PowAssent.Strategy.Github
                 ],
               campus_data_service: [
                    client_id: "client_id",
                    client_secret: "client_secret",
                    strategy: Ancile.PowAssentProviders.CampusDataService
                 ]
               ]
        ```
1. *NEW* Create similar file `/config/secret.yaml`:
   
   ```yaml
   campus_data_service:
   client_id: "client_id"
   client_secret: "client_secret"
   token_url: "https://campus.cornelltech.io/o/token/"
   authorize_url: "https://campus.cornelltech.io/o/authorize/"
   location_url: "https://campus.cornelltech.io/api/location/mostrecent/"

   azure:
     client_id: "client_id"
     client_secret: "client_id"

   ```
1. Configure PostgresSQL docker: `sh utils/postgres/create_docker_db.sh` 
1. Add new tables to your database: `mix ecto.migrate`
1. Install Node.js dependencies: `cd assets && npm install`. Don't forget to go back: `cd ..`.
1. Start the server: `mix phx.server`

## Python part. **NEW**
Currently there is a split between Elixir and Python. We are going to remove it
completely soon. We have the framework that will handle policy processing in Python
and Elixir for now only manages account creation and provider connection.   
 
1. Create new venv (Conda, Virtualenv, etc) with Python >= 3.6
1. Install dependencies `pip install -r src/requirements.txt`
1. Configure Redis docker: `sh utils/redis/create_docker_redis.sh`
1. Install RestrictedPython from GitHub master branch
    ```bash
    cd /tmp
    git clone https://github.com/zopefoundation/RestrictedPython.git
    cd RestrictedPython
    pip install .
    ```
1. Start the Python server: `python app.py`






## Development 

Let's just review each others code and verify that it works. 

Ideally, we will need to have better testing, but will see how it goes. 
