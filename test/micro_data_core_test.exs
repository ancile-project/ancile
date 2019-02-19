defmodule MicroDataCoreTest do
  use ExUnit.Case
  #  doctest MicroDataCore

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
  test "err_wrong_func" do
    policy_text = "get_data.get_data.WRONG.remove_data.get_data.return_data"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_neg" do
    policy_text = "a.b.!(a).c"
    program_text = "a\nb\nd\nc"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg" do
    policy_text = "a.b.!(a).c"
    program_text = "a\nb\na\nc"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_intersect" do
    policy_text = "(a&ANYF)"
    program_text = "a"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_intersect" do
    policy_text = "(a&b)"
    program_text = "a"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end



end
