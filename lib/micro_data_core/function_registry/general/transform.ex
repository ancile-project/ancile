defmodule MicroDataCore.FunctionRegistry.General.Transform do
  @moduledoc """
    The idea is to add functions that will take data, parameters like OAuth tokens,
    and internal function state. Instead of us deciding what data to give the
    function, we send the whole object, but the function will only pick required
    fields (todo later).

    We assume that functions can be written by external users/developers and peer
    reviewed. We can try using typespecs to check pattern-matching rules.

    Function syntax:

    ``` function(params, data, sensitive_data, _function_state) ```

    Data syntax:

    ``` data = %{} ```

    OAuth tokens will be inside sensitive_data
    ``` sensitive_data = [ %Ancile.Models.UserIdentity{provider: "github", tokens: %{...}, ...} ]```

    The function will return:

    ``` {data, function_scope} ```

  """

  require Logger


  def get_location_data(params, data, sensitive_data, _function_state) do
    Logger.info("data: #{inspect(data)}")
    Logger.info("params: #{inspect(params)}")
    res = Enum.find(sensitive_data, fn x -> x.provider == "campus_data_service"  end)
    {:ok, access_token} = IO.inspect(Map.fetch(res.tokens, "access_token"))


    client = OAuth2.Client.new(token: access_token)
    {:ok, result} = OAuth2.Client.get(client, "https://campus.cornelltech.io/api/location/mostrecent/")

    Logger.info("result: #{inspect(result.body)}")

    {%{"res" => result.body}, %{}}
  end


  def filter_floor({:params, params}, %{"res" => location}, _sensitive_data, _function_state) do
    Logger.info("location: #{inspect(location)}")
    Logger.info("params: #{inspect(params)}")
    [[_, floor]] = params

    location = case Map.get(location, "floor_name") do
      ^floor -> Map.drop(location, ["sta_location_x", "sta_location_y"])
      _ -> location


    end

    {%{"res" => location}, %{}}
  end




end

