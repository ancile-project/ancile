defmodule AncileWeb.API.RunController do
  @moduledoc """
    This is the controller that will process all incoming
    requests from apps to process user's data.
  """

  use AncileWeb, :controller
  use Export.Python
  alias Ancile.RepoControls
  alias MicroDataCore.Core
  alias AncileWeb.API.Helper
  require Logger

  @doc """
  We can use it to test that Phoenix is up.
  """
  def api_test(conn, _params) do
    json(conn, %{id: 123})
  end

  @doc """
  This is the main entrance point for now.
  Takes parameters and tries to run the program.

  NOTE: I don't have much of error handling (wrong tokens/wrong data) so
  it only works for the sunny day case.
  """
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
         {:ok, policies} <- Helper.get_joined_policy(app_id, user_id, purpose),
         joined_policies <- Helper.intersect_policies(policies),
         {:ok, sensitive_data} <- RepoControls.get_providers(user_id),
         {:ok, res} <- run_python_core(joined_policies, program, RepoControls.extract_tokens(sensitive_data))
      do
      Logger.debug("user_id: #{inspect(user_id)}")
      Logger.debug("app_id: #{inspect(app_id)}")
      Logger.debug("program: #{inspect(program)}")
      Logger.debug("policies: #{inspect(policies)}")
      Logger.debug("joined policy: #{inspect(policies)}")
      Logger.debug("sensitive_data: #{inspect(sensitive_data |> RepoControls.extract_tokens)}")
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

  @doc """
  Fail if provided JSON has wrong format.
  """
  def run_program(conn, params) do
    IO.inspect(params, label: "params: ")
    json(conn, %{error: "Send correct params"})
  end

  def run_python_core(policy, program, sensitive_data) do
    {:ok, pid} = Python.start(python_path: Path.expand("src/micro_data_core_python"))
    IO.inspect(pid, label: "PID: ")
    module = "core"
    method = "execute"
    params = [policy, program, sensitive_data]
    result = pid
             |> Python.call(module, method, params)
    IO.inspect(result)

    {:ok, result}
  end


end