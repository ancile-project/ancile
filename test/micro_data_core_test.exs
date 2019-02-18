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

  # succsessful tests
  test "exact_match" do
    policy_text = "get_data.get_data.filter_data.remove_data.get_data.return_data"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end


  test "anyf*_in_the_middle" do
    policy_text = "get_data.get_data.filter_data.ANYF*.return_data"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "single_anyf*" do
    policy_text = "ANYF*"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "reduce_repeated_func_with_*" do
    policy_text = "get_data*.filter_data.remove_data.get_data.return_data"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "force_filter_simple" do
    policy_text = "get_data.(filter_data+remove_data)*.return_data"
    program_text = "get_data\nfilter_data\nremove_data\nreturn_data"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  #unsuccessful tests
  test "wrong_func" do
    policy_text = "get_data.get_data.WRONG.remove_data.get_data.return_data"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "force_filter_get_data" do
    policy_text = "(skip*.(get_data.filter_data)*.skip*)*"
    program_text = "skip\nskip\nget_data\nfilter_data\nskip\nget_data\nskip"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end



end
