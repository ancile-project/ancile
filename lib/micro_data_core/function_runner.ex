defmodule MicroDataCore.FunctionRunner do
#  use MicroDataCore.FunctionRegistry.General.Transform
  @moduledoc """

    This module would interact with function registry and pass required parameters.
    Check my notes in `general_use_functions.ex`.

    To store function state we will use `ETS` service that is in-memory map and
    is really fast and supports concurrency that we really need, as we expect
    that people will call same functions.

    To find appropriate functions we can just iterate over modules and use:

    ```MicroDataCore.FunctionRegistry.GeneralUseFunctions.__info__(:functions)```

    to get functions. However, maybe there are other better ways to populate functions.

  """
  require Logger

  @doc """
  We just mock the actual function execution. TBD
  """
  def execute_command(function, data) do


    Logger.debug("Function and data: #{inspect({function, data})}")
    case function do
      "error" -> {:error, "Error execution function :(."}
      _ -> {:ok, 42, Map.put(data, Time.utc_now(), {function})}
    end
  end

  def execute_command_new() do
    # dumb params
    function_name = :test
    function_scope_value = %{:user_scope => %{:c => 5}, :combined_scope => %{:d => 5}}
    data = %{:location=> %{:a => 5}, :general => %{:b => 9}}
    oauth_scopes = %{:location_token => %{:a => 5}, :email_token => %{:b => 9}}

    # use :ETS to store function session state. All fake for now.
    case :ets.whereis(:test) do
      :undefined ->
        :ets.new(function_name, [:set, :protected, :named_table])
      _ -> true
    end
    :ets.insert_new(function_name, {:function_scope, function_scope_value})


    ### Actual logic
    function_scope = :ets.lookup(function_name, :function_scope)[:function_scope]

    # @TODO parse function names as ATOMs. Really convenient to call them here:
    # @TODO lookup function name.
    {value, new_data, new_scope} = apply(MicroDataCore.FunctionRegistry.General.Transform , function_name, [data, oauth_scopes, function_scope])

    #overwrite existing function scope
    :ets.insert(function_name, {:function_scope, new_scope})

    {value, new_data, new_scope}
  end

end
