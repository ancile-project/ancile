use Mix.Config
## NOT WORKING!!!!! NEED TO CONFIGURE

# We don't run a server during test. If one is required,
# you can enable the server option below.
config :ancile, AncileWeb.Endpoint,
  http: [port: 4002],
  server: false

# Print only warnings and errors during test
config :logger, level: :warn

# Configure your database
config :ancile, Ancile.Repo,
  username: "postgres",
  password: "postgres",
  database: "ancile_test",
  hostname: "localhost",
  pool: Ecto.Adapters.SQL.Sandbox
