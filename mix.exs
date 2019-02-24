defmodule MicroDataCore.MixProject do
  use Mix.Project

  def project do
    [
      app: :core,
      version: "0.1.0",
      elixir: "~> 1.8",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [

      extra_applications: [:logger]
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:gen_stage, "~> 0.14.1"},
      {:memoize, "~> 1.3"},
      {:benchfella, "~> 0.3.0"},
      {:decorator, "~> 1.2"},
    {:dialyxir, "~> 1.0.0-rc.4", only: [:dev], runtime: false}
      # {:dep_from_hexpm, "~> 0.3.0"},
      # {:dep_from_git, git: "https://github.com/elixir-lang/my_dep.git", tag: "0.1.0"}
    ]
  end
end
