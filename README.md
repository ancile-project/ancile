# Ancile


Documentation for Ancile: 


## Deployment

I think it's a good start to deploy Ancile locally first
and then move to the server version. Steps are similar 
except you need to obtain certificates differently. 

1. Setup [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)
 and [Elixir](https://elixir-lang.org/install.html)
1. Fetch dependencies: `mix deps.get` and build the project: `mix`.
1. Get SSL certificates (run `mix phx.gen.cert` locally and use LetsEncrypt remotely)
   1. For the local deployment just check SSL location in `dev.exs`
   1. For remote deployment create `dev.secret.exs` and put the new config: 
   
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
1. Configure PostgresSQL docker: `sh utils/postgres/create_docker_db.sh` 
1. Add new tables to your database: `mix ecto.migrate`
1. Start the server: `mix phx.server`


## Development 

Let's just review each others code and verify that it works. 

Ideally, we will need to have better testing, but will see how it goes. 
