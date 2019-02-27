defmodule MicroDataCore.Utilities.TypeTools do
@moduledoc """
  A module containing ultility functions to help with 
  type evaluation. At the moment it just defines 
  basic guard macros
"""

  # This may or may not be useful
  # def type_of(val) when is_atom(val), do: :atom
  # def type_of(val) when is_binary(val), do: :binary
  # def type_of(val) when is_bitstring(val), do: :bitstring
  # def type_of(val) when is_boolean(val), do: :bool
  # def type_of(val) when is_float(val), do: :float
  # def type_of(val) when is_integer(val), do: :int
  # def type_of(val) when is_list(val), do: :list
  # def type_of(val) when is_map(val), do: :map
  # def type_of(val) when is_tuple(val), do: :tuple

  defguard comparable(val1, val2) when 
          (is_number(val1) and is_number(val2)) or
          (is_binary(val1) and is_binary(val2))

  defguard valid_comparison_operator(operation) when
          operation in ['<', '<=', '>', '>=', '!=', '=']

end