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

    with {:ok, app_id} <- Phoenix.Token.verify(AncileWeb.Endpoint, "user salt", api_token, max_age: :infinity),
         {:ok, user_id} <- RepoControls.get_user_by_email(user),
         {:ok, policies} <- RepoControls.get_policies(app_id, user_id, purpose),
         joined_policies <- intersect_policies(policies),
         {:ok, sensitive_data} <- RepoControls.get_providers(user_id),
         {:ok, res} <- Core.phoenix_entry(joined_policies, program, sensitive_data)
      do
      Logger.debug("user_id: #{inspect(user_id)}")
      Logger.debug("app_id: #{inspect(app_id)}")
      Logger.debug("program: #{inspect(program)}")
      Logger.debug("policies: #{inspect(policies)}")
      Logger.debug("joined policy: #{inspect(policies)}")
      json(conn, %{policies: joined_policies, program: program, output: res})

    else
      {:error, error} ->
        conn
        |> put_status(:bad_request)
        |> json(%{error: error})
      error ->
        conn
        |> put_status(:bad_request)
        |> json(%{error: error})
    end

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