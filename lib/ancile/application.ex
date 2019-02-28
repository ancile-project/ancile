defmodule Ancile.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  def start(_type, _args) do
    # List all child processes to be supervised
    children = [
      # Start the Ecto repository
      Ancile.Repo,
      # Start the endpoint when the application starts
      AncileWeb.Endpoint
      # Starts a worker by calling: Ancile.Worker.start_link(arg)
      # {Ancile.Worker, arg},
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: Ancile.Supervisor]
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  def config_change(changed, _new, removed) do
    AncileWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
