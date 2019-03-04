defmodule AncileWeb.API.RunController do
  use AncileWeb, :controller
  alias Ancile.RepoControls
  alias MicroDataCore.Core
  require Logger

  def api_test(conn, _params) do

    json(conn, %{id: 123})
  end

  def run_program(
        conn,
        %{
          "program" => program,
          "api_token" => api_token,
          "user" => user,
          "purpose" => purpose
        }
      ) do
    {:ok, app_id} = Phoenix.Token.verify(AncileWeb.Endpoint, "user salt", api_token, max_age: :infinity)
    user_id = RepoControls.get_user_by_email(user)
    Logger.debug("user_id: #{inspect(user_id)}")
    Logger.debug("app_id: #{inspect(app_id)}")
    Logger.debug("program: #{inspect(program)}")

    policies = RepoControls.get_policies(app_id, user_id, purpose)
    # join policies together:
    joined_policy = intersect_policies(policies)
    Logger.debug("Joined policy: #{inspect(joined_policy)}")

    sensitive_data = RepoControls.get_providers(user_id)
    {res, output} = Core.phoenix_entry(joined_policy, program, sensitive_data)
    json(
      conn,
      %{
        policies: joined_policy,
        program: program,
        result: res,
        output: output
      }
    )
  end

  def run_program(conn, params) do
    IO.inspect(params, label: "params: ")
    json(conn, %{error: "Send correct params"})
  end

  def intersect_policies([head | []]) do
    head
  end

  def intersect_policies([head | tail]) do
    "[" <> head <> "&" <> intersect_policies(tail) <> "]"
  end

end