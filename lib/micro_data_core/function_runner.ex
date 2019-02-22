defmodule MicroDataCore.FunctionRunner do
  @moduledoc false
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

end
