defmodule MicroDataCoreTest do
  use ExUnit.Case
#  doctest MicroDataCore

  test "first_test" do
    {:ok, policy_text} = File.read("test/policies/simple.txt")
    {:ok, program_text} = File.read("test/programs/simple.txt")
    {result, data} = MicroDataCore.Core.entry_point([policy_text, program_text])
    IO.inspect(data)
    assert result == :ok
  end


end
