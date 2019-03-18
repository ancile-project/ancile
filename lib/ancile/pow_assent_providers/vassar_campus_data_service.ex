defmodule Ancile.PowAssentProviders.VassarCampusDataService do
  @moduledoc """
  Check Pow Assent library to see how it works.

  """
  use PowAssent.Strategy
  alias Plug.Conn
  alias PowAssent.Strategy, as: Helpers
  alias PowAssent.{CallbackCSRFError, CallbackError, ConfigurationError, HTTPAdapter.HTTPResponse, RequestError}
  require Logger

  def default_config(_config) do
    [
      site: "https://campusdataservices.cs.vassar.edu",
      authorize_url: "https://campusdataservices.cs.vassar.edu/oauth/authorize",
      token_url: "https://campusdataservices.cs.vassar.edu/oauth/token",
      authorization_params: [scope: "profile"],
    ]
  end

  @spec authorize_url(Keyword.t(), Conn.t()) :: {:ok, %{conn: Conn.t(), state: binary(), url: binary()}}
  def authorize_url(config, conn) do
    config = set_config(config)

    state         = gen_state()
    conn          = Conn.put_private(conn, :pow_assent_state, state)
    redirect_uri  = config[:redirect_uri]
    params        = authorization_params(config, state: state, redirect_uri: redirect_uri)
    authorize_url = Keyword.get(config, :authorize_url, "/oauth/authorize")

    Logger.debug(config[:site])
    url           = Helpers.to_url(config[:site], authorize_url, params)

    {:ok, %{conn: conn, url: url, state: state}}
  end

  def normalize(_config, user) do
    IO.inspect(user, label: "ASISIEOEE normalize: ")
    {:ok, user}
  end

  def get_user(config, token) do
    IO.inspect(config, label: "get_user config: ")
    IO.inspect(token, label: "get_user token: ")
    user = %{
      "uid"        =>  token["refresh_token"], # this is stupid but CDS doesn't return user id
      "name" => "CDS, No data available. TODO: change it."}

      {:ok, user}
  end

  def callback(config, conn, params) do
    config = set_config(config)
    state  = conn.private[:pow_assent_state]

    state
    |> check_state(params)
    |> get_access_token(params, config)
    |> fetch_user(config, conn)
  end

  defp check_state(_state, %{"error" => _} = params) do
    message   = params["error_description"] || params["error_reason"] || params["error"]
    error     = params["error"]
    error_uri = params["error_uri"]

    {:error, %CallbackError{message: message, error: error, error_uri: error_uri}}
  end

  defp check_state(state, %{"code" => _code} = params) do
    case params["state"] do
      ^state -> :ok
      _      -> {:error, %CallbackCSRFError{}}
    end
  end

  defp get_access_token(:ok, %{"code" => code, "redirect_uri" => redirect_uri}, config) do
    client_secret = Keyword.get(config, :client_secret)
    client_id = Keyword.get(config, :client_id)
    params        = authorization_params(config, code: code, client_secret: client_secret, redirect_uri: redirect_uri, grant_type: "authorization_code")
    token_url     = Keyword.get(config, :token_url, "/oauth/token")

    url = Helpers.to_url(config[:site], token_url, params)
    headers = [{"Authorization", 
    "Basic " <> Base.encode64(client_id <> ":" <> client_secret)}]

    response = Helpers.request(:post, url, "", headers, config)

    response
    |> Helpers.decode_response(config)
    |> process_access_token_response()
  end

  defp fetch_user({:ok, token}, config, conn) do
    config
    |> get_user(token)
    |> case do
      {:ok, user} -> {:ok, %{conn: conn, token: token, user: user}}
      {:error, error} -> {:error, %{conn: conn, error: error}}
    end
  end
  defp fetch_user({:error, error}, _config, conn),
    do: {:error, %{conn: conn, error: error}}


    defp authorization_params(config, params) do
      client_id = Keyword.get(config, :client_id)
      default   = [response_type: "code", client_id: client_id]
      custom    = Keyword.get(config, :authorization_params, [])
  
      default
      |> Keyword.merge(custom)
      |> Keyword.merge(params)
      |> List.keysort(0)
    end

  defp process_access_token_response({:ok, %HTTPResponse{status: 200, body: %{"access_token" => _} = token}}), do: {:ok, token}
  defp process_access_token_response(any), do: process_response(any)
  defp process_response({:ok, %HTTPResponse{} = response}), do: {:error, RequestError.unexpected(response)}
  defp process_response({:error, %HTTPResponse{} = response}), do: {:error, RequestError.invalid(response)}
  defp process_response({:error, error}), do: {:error, error}

  defp gen_state do
    24
    |> :crypto.strong_rand_bytes()
    |> :erlang.bitstring_to_list()
    |> Enum.map(fn x -> :erlang.integer_to_binary(x, 16) end)
    |> Enum.join()
    |> String.downcase()
  end

  defp set_config(config) do
    config
    |> default_config()
    |> Keyword.merge(config)
  end
end
