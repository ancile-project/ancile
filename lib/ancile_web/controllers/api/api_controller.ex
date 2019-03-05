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
         {:ok, policies} <- get_joined_policy(app_id, user_id, purpose),
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

  def get_joined_policy(app_id, user_id, purpose) do
    case RepoControls.get_policies(app_id, user_id, purpose) do
      {:ok, policies} -> {:ok, policies}
      {:error, :no_policy_found} ->
        object = %{
          app_id: app_id,
          user_id: user_id,
          purpose: purpose,
          policy: "ANYF*",
          active: true
        }
        RepoControls.create_policy(object)
        {
          :error,
          """
          No policy for user: #{inspect(RepoControls.get_email_by_id(user_id))},
          app: #{inspect(RepoControls.get_email_by_id(app_id))}, purpose: #{inspect(purpose)}.
          We created a policy: `ANYF*` that allows everything. Please try calling your
          program again. If you want to change the policy modify it in the Dashboard.
          """
        }

    end
  end

  def intersect_policies([head | []]) do
    head
  end

  def intersect_policies([head | tail]) do
    "[" <> head <> "&" <> intersect_policies(tail) <> "]"
  end

end