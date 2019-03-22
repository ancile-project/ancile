defmodule Ancile.PowAssentProviders.AncileOAuth2 do

  @moduledoc """
  OAuth 2.0 strategy.

  ## Usage

      config :my_app, :pow_assent,
        providers: [
          example: [
            client_id: "REPLACE_WITH_CLIENT_ID",
            client_secret: "REPLACE_WITH_CLIENT_SECRET",
            strategy: PowAssent.Strategy.OAuth2,
            site: "https://auth.example.com",
            authorization_params: [scope: "user:read user:write"],
            user_url: "https://example.com/api/user"
          ]
        ]
  """
  use PowAssent.Strategy

  alias Plug.Conn
  alias PowAssent.Strategy, as: Helpers
  alias PowAssent.{CallbackCSRFError, CallbackError, ConfigurationError, HTTPAdapter.HTTPResponse, RequestError}

  @doc false
  @spec authorize_url(Keyword.t(), Conn.t()) :: {:ok, %{conn: Conn.t(), state: binary(), url: binary()}}
  def authorize_url(config, conn) do
    state         = gen_state()
    conn          = Conn.put_private(conn, :pow_assent_state, state)
    redirect_uri  = config[:redirect_uri]
    params        = authorization_params(config, state: state, redirect_uri: redirect_uri)
    authorize_url = Keyword.get(config, :authorize_url, "/oauth/authorize")
    url           = Helpers.to_url(config[:site], authorize_url, params)

    {:ok, %{conn: conn, url: url, state: state}}
  end

  defp authorization_params(config, params) do
    client_id = Keyword.get(config, :client_id)
    default   = [response_type: "code", client_id: client_id]
    custom    = Keyword.get(config, :authorization_params, [])

    default
    |> Keyword.merge(custom)
    |> Keyword.merge(params)
    |> List.keysort(0)
  end

  @doc false
  @spec callback(Keyword.t(), Conn.t(), map(), atom()) :: {:ok, %{conn: Conn.t(), user: map(), token: map()}} | {:error, %{conn: Conn.t(), error: any()}}
  def callback(config, conn, params, strategy \\ __MODULE__) do
    state  = conn.private[:pow_assent_state]

    state
    |> check_state(params)
    |> get_access_token(params, config)
    |> fetch_user(config, conn, strategy)
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
    client_id     = Keyword.get(config, :client_id)
    params        = authorization_params(config, code: code, client_secret: client_secret, redirect_uri: redirect_uri, grant_type: "authorization_code")
    token_url     = Keyword.get(config, :token_url, "/oauth/token")

    response = case Keyword.get(config, :strategy) do
       PowAssent.Strategy.AzureOAuth2 ->
         url = Helpers.to_url(config[:site], token_url, [])
         body = URI.encode_query(params)
         :post
            |> Helpers.request(url, body, [{'content-type', 'application/x-www-form-urlencoded'}], config)
       _ ->
         url = Helpers.to_url(config[:site], token_url, params)
         :post
            |> Helpers.request(url, param_encoding(config, code), get_access_headers(config), config)
    end
    response
    |> Helpers.decode_response(config)
    |> process_access_token_response()
  end
  defp get_access_token({:error, error}, _params, _config), do: {:error, error}

  defp process_access_token_response({:ok, %HTTPResponse{status: 200, body: %{"access_token" => _} = token}}), do: {:ok, token}
  defp process_access_token_response(any), do: process_response(any)

  defp process_response({:ok, %HTTPResponse{} = response}), do: {:error, RequestError.unexpected(response)}
  defp process_response({:error, %HTTPResponse{} = response}), do: {:error, RequestError.invalid(response)}
  defp process_response({:error, error}), do: {:error, error}

  defp fetch_user({:ok, token}, config, conn, strategy) do
    config
    |> strategy.get_user(token)
    |> case do
      {:ok, user} -> {:ok, %{conn: conn, token: token, user: user}}
      {:error, error} -> {:error, %{conn: conn, error: error}}
    end
  end
  defp fetch_user({:error, error}, _config, conn, _strategy),
    do: {:error, %{conn: conn, error: error}}

  @doc """
  Makes a HTTP get request to the API.

  JSON responses will be decoded to maps.
  """
  @spec get(Keyword.t(), map(), binary(), map() | Keyword.t()) :: {:ok, map()} | {:error, term()}
  def get(config, token, url, params \\ []) do
    url     = Helpers.to_url(config[:site], url, params)
    headers = authorization_headers(config, token)

    :get
    |> Helpers.request(url, nil, headers, config)
    |> Helpers.decode_response(config)
  end

  @spec get_user(Keyword.t(), map(), map() | Keyword.t()) :: {:ok, map()} | {:error, term()}
  def get_user(config, token, params \\ []) do
    case config[:user_url] do
      nil ->
        {:error, %ConfigurationError{message: "No user URL set"}}

      user_url ->
        config
        |> get(token, user_url, params)
        |> process_user_response()
    end
  end

  @spec authorization_headers(Keyword.t(), map()) :: [{binary(), binary()}]
  def authorization_headers(_config, token) do
    access_token_type = Map.get(token, "token_type", "Bearer")
    access_token = token["access_token"]

    [{"authorization", "#{access_token_type} #{access_token}"}]
  end

  defp process_user_response({:ok, %HTTPResponse{status: 200, body: user}}), do: {:ok, user}
  defp process_user_response({:error, %HTTPResponse{status: 401}}), do: {:error, %RequestError{message: "Unauthorized token"}}
  defp process_user_response(any), do: process_response(any)

  defp gen_state do
    24
    |> :crypto.strong_rand_bytes()
    |> :erlang.bitstring_to_list()
    |> Enum.map(fn x -> :erlang.integer_to_binary(x, 16) end)
    |> Enum.join()
    |> String.downcase()
  end

  defp get_access_headers(config) do
    client_secret = Keyword.get(config, :client_secret)
    client_id = Keyword.get(config, :client_id)

     auth = case Keyword.fetch(config, :use_basic) do
      {:ok, True} -> [{"Authorization", 
      "Basic " <> Base.encode64(client_id <> ":" <> client_secret)}]
      _ -> []
    end

    form_encode = case Keyword.fetch(config, :param_encoding) do
      {:ok, True} -> [{'content-type', 'application/x-www-form-urlencoded'}]
      _ -> []
    end
    auth ++ form_encode
  end

  defp param_encoding(config, code) do
    client_secret = Keyword.get(config, :client_secret)
    client_id     = Keyword.get(config, :client_id)
    redirect_uri  = Keyword.get(config, :redirect_uri)
    case Keyword.fetch(config, :param_encoding) do
      {:ok, True} -> authorization_params(config, code: code, client_secret: client_secret, client_id: client_id,
                                        redirect_uri: redirect_uri, grant_type: "authorization_code") |> URI.encode_query
        _ -> ""
    end
  end

end
