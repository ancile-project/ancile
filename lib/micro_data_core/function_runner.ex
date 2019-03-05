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
  def execute_command_mock({function, _params}, data, _sensitive_data) do


    Logger.debug("Function and data: #{inspect({function, data})}")
    case function do
      "error" -> {:error, "Error execution function :(."}
      _ -> {:ok, 42, Map.put(data, Time.utc_now(), to_string(function))}
    end
  end

  @doc """
  This is very simple and dumb implementation of how we should call functions
  with parameters.
  """
   def execute_command({function_name, params}, data, sensitive_data) do
    IO.inspect(function_name)
    function_atom = String.to_atom(to_string(function_name))
    {new_data, _} = apply(MicroDataCore.FunctionRegistry.General.Transform ,  function_atom, [params, data, sensitive_data, %{}])
    {:ok, 42, new_data}
     end

end
