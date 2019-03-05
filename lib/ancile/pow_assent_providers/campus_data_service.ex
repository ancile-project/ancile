defmodule Ancile.PowAssentProviders.CampusDataService do
  use PowAssent.Strategy.OAuth2.Base

  def default_config(_config) do
    [
      site: "https://campus.cornelltech.io",
      authorize_url: "https://campus.cornelltech.io/o/authorize/",
      token_url: "https://campus.cornelltech.io/o/token/",
#      user_url: "/user",
      authorization_paramks: [scope: "read"]
    ]
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
end