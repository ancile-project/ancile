defmodule Ancile.Mixfile do
  use Mix.Project

  def project do
    [
      app: :Ancile,
      version: "0.0.1",
      elixir: "~> 1.6",
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
      mod: {SmallDataCore.Application, []},
      extra_applications: [:logger, :runtime_tools, :httpoison, :export]
    ]
  end

  # # Specifies which paths to compile per environment.
  # defp elixirc_paths(:test), do: ["lib", "test/support"]
  # defp elixirc_paths(_), do: ["lib"]

  # Specifies your project dependencies.
  #
  # Type `mix help deps` for examples and options.
  defp deps do
    [
      {:phoenix, "~> 1.3.0"},
      {:phoenix_pubsub, "~> 1.0"},
      {:phoenix_ecto, "~> 3.2"},
      {:postgrex, ">= 0.0.0"},
      {:poison, "~> 3.1"},
      {:timex, "~> 3.1"},
      {:phoenix_html, "~> 2.10"},
      {:phoenix_live_reload, "~> 1.0", only: :dev},
      {:gettext, "~> 0.11"},
      {:cowboy, "~> 1.0"},
      {:shield, "~> 0.7.2", git: "https://github.com/mdgriffith/shield.git", branch: "master"},
      {:bamboo, "~> 1.0.0-rc.2", override: true},
      {:bamboo_smtp, "~> 1.5.0-rc.1"},
      {:oauth2, "~> 0.9"},
      {:annotatable, "~> 0.1.0"},
      {:distillery, "~> 1.5", runtime: false},
      {:elixir_make, "~> 0.4", runtime: false},
      {:exprotobuf, "~> 1.2.9"},
      {:socket, "~> 0.3"},
      {:slack, "~> 0.14.0"},
      {:httpotion, "~> 3.1.0"},
      {:logger_file_backend, "~> 0.0.10"},
      {:benchee, "~> 0.9", only: :dev},
      {:export, "~> 0.1.0"},
      {:cachex, "~> 3.1.0"},
      {:elixir_uuid, "~> 1.2"}
    ]
  end

  # Aliases are shortcuts or tasks specific to the current project.
  # For example, to create, migrate and run the seeds file at once:
  #
  #     $ mix ecto.setup
  #
  # See the documentation for `Mix` for more info on aliases.
  # defp aliases do
  #   [
  #     "ecto.setup": ["ecto.create", "ecto.migrate", "run priv/repo/seeds.exs"],
  #     "ecto.reset": ["ecto.drop", "ecto.setup"],
  #     test: ["ecto.create --quiet", "ecto.migrate", "test"]
  #   ]
  # end
end
