defmodule Ancile.PowAssentProviders.Google do  @moduledoc """
  Google OAuth 2.0 strategy.

  ## Usage

      config :my_app, :pow_assent,
        providers: [
          google: [
            client_id: "REPLACE_WITH_CLIENT_ID",
            client_secret: "REPLACE_WITH_CLIENT_SECRET",
            strategy: PowAssent.Strategy.Google
          ]
        ]
  """
  use PowAssent.Strategy.OAuth2.Base

  @spec default_config(Keyword.t()) :: Keyword.t()
  def default_config(_config) do
    [
      site: "https://www.googleapis.com",
      authorize_url: "https://accounts.google.com/o/oauth2/v2/auth",
      token_url: "https://www.googleapis.com/oauth2/v4/token",
      authorization_params: [scope: "https://www.googleapis.com/auth/calendar.readonly" ]
    ]
  end

  @spec normalize(Keyword.t(), map()) :: {:ok, map()}
  def normalize(_config, user) do
    {:ok, %{
      "uid"        => user["id"],
      "name"       => user["name"]}}
  end

  # def get_user(config, token) do
  #   IO.inspect(config, label: "get_user config: ")
  #   IO.inspect(token, label: "get_user token: ")
  #   user = %{
  #     "uid"        =>  token["refresh_token"], # this is stupid but CDS doesn't return user id
  #     "name" => "CDS, No data available. TODO: change it."}

  #     {:ok, user}
  # end
end
