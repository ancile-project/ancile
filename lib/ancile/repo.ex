defmodule Ancile.Repo do
  use Ecto.Repo,
    otp_app: :ancile,
    adapter: Ecto.Adapters.Postgres
end
