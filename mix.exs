defmodule Ancile.MixProject do
  use Mix.Project

  def project do
    [
      app: :ancile,
      version: "0.1.0",
      elixir: "~> 1.8",
      elixirc_paths: elixirc_paths(Mix.env()),
      compilers: [:phoenix, :gettext] ++ Mix.compilers(),
      start_permanent: Mix.env() == :prod,
      aliases: aliases(),
      deps: deps()
    ]
  end

  # Configuration for the OTP application.
  #
  # Type `mix help compile.app` for more information.
  def application do
    [
      mod: {Ancile.Application, []},
      extra_applications: [:logger, :runtime_tools]
    ]
  end

  # Specifies which paths to compile per environment.
  defp elixirc_paths(:test), do: ["lib", "test/support"]
  defp elixirc_paths(_), do: ["lib"]

  # Specifies your project dependencies.
  #
  # Type `mix help deps` for examples and options.
  defp deps do
    [
      {:gen_stage, "~> 0.14.1"},
      {:memoize, "~> 1.3"},
      {:benchfella, "~> 0.3.0"},
      {:decorator, "~> 1.2"},
      {:dialyxir, "~> 1.0.0-rc.4", only: [:dev], runtime: false},

      {:pow, "~> 1.0.1"},
      {:phoenix, "~> 1.4.1"},
      {:phoenix_pubsub, "~> 1.1"},
      {:phoenix_ecto, "~> 4.0"},
      {:ecto_sql, "~> 3.0"},
      {:postgrex, ">= 0.0.0"},
      {:phoenix_html, "~> 2.11"},
      {:phoenix_live_reload, "~> 1.2", only: :dev},
      {:gettext, "~> 0.11"},
      {:jason, "~> 1.0"},
      {:plug_cowboy, "~> 2.0"},
      {:export, "~> 0.1.0"},

#      {:pow_assent, "~> 0.1"},

    {:pow_assent, git: "https://github.com/ebagdasa/pow_assent.git"},
      # Optional, but recommended for SSL validation with :httpc adapter
      {:certifi, "~> 2.4"},
      {:ssl_verify_fun, "~> 1.1"},
    {:mint, "~> 0.1.0"},
    {:oauth2, "~> 0.9"},

    # delete:
    {:poison, "~> 3.1"}
    ]
  end

  # Aliases are shortcuts or tasks specific to the current project.
  # For example, to create, migrate and run the seeds file at once:
  #
  #     $ mix ecto.setup
  #
  # See the documentation for `Mix` for more info on aliases.
  defp aliases do
    [
      "ecto.setup": ["ecto.create", "ecto.migrate", "run priv/repo/seeds.exs"],
      "ecto.reset": ["ecto.drop", "ecto.setup"],
      test: ["ecto.create --quiet", "ecto.migrate", "test"]
    ]
  end
end
