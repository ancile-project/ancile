defmodule MicroDataCore.FunctionRegistry.General.Transform do
  @moduledoc """
    The idea is to add functions that will take data, parameters like OAuth tokens,
    and internal function scope. Instead of us deciding what data to give the
    function, we send the whole object, but the function will only pick required
    fields. Typespecs enforce the contract (run `mix dialyzer` to check type
    compliance).

    We assume that functions can be written by external users/developers and peer
    reviewed, but typespecs will be additionally checked by Ancile admins.
    The type system is not really strict, but it allows us to check
    pattern-matching rules.

    Specs will allow us to specify exact data fields needed for this function and
    allow us to add more clarity in usage of functions and their parameters.
    As well, it's supposed to be a good addition for documentation.

    Not sure, that exactly now we need support for typing, e.g. to convert all functions,
    but possibly worth doing later.

    The only problem I see is that nice naming of function parameters is gone as
    we do pattern matching.

    Function syntax:

    ``` function(data, oauth_tokens, function_scope) ```

    Data syntax:

    ``` data = %{:location => map(), :general => map(), ...} ```

    OAuth tokens need to be populated for each request separately for the exact
    user. I assume it can be done when application request received.
    OAuth syntax:

    ``` oauth_tokens = %{:location_token => String.t(), ....} ```

    Function scope should use ETS storage to be able to store and access state
    during multiple execution calls. It's helpful when we want to track contextual
    events or implement tools like Differential Privacy. There are two subscopes
    individual, i.e. only for the current user (Diff Priv), and combined scope,
    i.e. for all calls to *this* function but across multiple users (k-anonymity, etc)
    Function scope syntax:

    ``` function_scope = %{:user_scope => map(), :combined_scope => map()}


  """


  @spec test(
          %{:location => location :: map(), :general => general :: map()},
          %{:location_token => location_token :: String.t()},
          function_scope :: %{:user_scope => user_scope :: map()}
        ) :: {value :: number, %{:location => map(), :general => map()}, %{:user_scope => map()}}



  @doc """
  This function is doing nothing but takes `location` and `general` fields
  """
  def test(data, sensitive_data, _function_state) do
    IO.inspect(data)
    IO.inspect(sensitive_data)
    res = Enum.find(sensitive_data, fn x -> x.provider == "campus_data_service"  end)
    IO.inspect(res)
    {42, %{}}
  end


  def get_location_data(params, data, sensitive_data, _function_state) do
    IO.inspect(data)
#    IO.inspect(sensitive_data)
    res = Enum.find(sensitive_data, fn x -> x.provider == "campus_data_service"  end)
    {:ok, access_token} = IO.inspect(Map.fetch(res.tokens, "access_token"))


    client = OAuth2.Client.new(token: access_token)
    start = System.monotonic_time(:millisecond)
    {:ok, result} = OAuth2.Client.get(client, "https://campus.cornelltech.io/api/location/mostrecent/")
    IO.inspect(result.body)
    duration = System.monotonic_time(:millisecond) - start


    {%{"res" => result.body}, %{}}
  end


  def filter_floor({:params, params}, %{"res" => location}, sensitive_data, _function_state) do
    IO.inspect(location, label: "A@!!@H#@K!#H!@#H!@#!@J#H!@H#J@H#HJ!@#!J#H!@K#")
    IO.inspect(params)
    [[_, floor]] = params

    location = case Map.get(location, "floor_name") do
      ^floor -> Map.drop(location, ["sta_location_x", "sta_location_y"])
      _ -> location


    end

    {%{"res" => location}, %{}}
  end




end

