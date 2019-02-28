# This file is responsible for configuring your application
# and its dependencies with the aid of the Mix.Config module.
#
# This configuration file is loaded before any dependency and
# is restricted to this project.

# General application configuration
use Mix.Config

config :ancile,
  ecto_repos: [Ancile.Repo]

# Configures the endpoint
config :ancile, AncileWeb.Endpoint,
  url: [host: "localhost"],
  secret_key_base: "Q/cCb7tnQcvkQVhszsvXXXPd+PFBRfIRSX1MLskZ7Y4PKgN07HMjKX5gw1QfAKmr",
  render_errors: [view: AncileWeb.ErrorView, accepts: ~w(html json)],
  pubsub: [name: Ancile.PubSub, adapter: Phoenix.PubSub.PG2]

# Configures Elixir's Logger
config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Use Jason for JSON parsing in Phoenix
config :phoenix, :json_library, Jason


config :ancile, :pow,
  user: Ancile.Users.User,
  repo: Ancile.Repo,
  web_module: AncileWeb,
  routes_backend: AncileWeb.Pow.Routes

# Import environment specific config. This must remain at the bottom
# of this file so it overrides the configuration defined above.
import_config "#{Mix.env()}.exs"


#config :logger,
#    backends: [:console],
#    compile_time_purge_level: :error