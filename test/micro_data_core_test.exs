defmodule MicroDataCoreTest do
  use ExUnit.Case
  #  doctest MicroDataCore

  test "first_test" do
    {:ok, policy_text} = File.read("test/policies/simple.txt")
    {:ok, program_text} = File.read("test/programs/simple.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
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
  test "err_wrong_func" do
    policy_text = "get_data.get_data.WRONG.remove_data.get_data.return_data"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end



  ##############################
  # NEGATION TESTS
  ##############################

  test "ok_neg_concat" do
    policy_text = "k.!((g.f)).k"
    program_text = "k\nf\ng\nk"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_concat" do
    policy_text = "!(g.f)"
    program_text = "g\nf"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_neg_concat_first_match" do
    policy_text = "!((g.f))"
    program_text = "g\nq"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end
#
  test "ok_neg_union" do
    policy_text = "!((g+f)).m"
    program_text = "d\nm"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_union" do
    policy_text = "!((g+f)).m.k"
    program_text = "f\nm\nk"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end


  test "ok_neg_star_inside" do
    policy_text = "!(a*)"
    program_text = "b\nb\nb"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_star_inside" do
    policy_text = "!(a*)"
    program_text = "a\na\na"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_neg_star_outside" do
    policy_text = "(!(a))*.m"
    program_text = "d\nm"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_outside" do
    policy_text = "(!(a))*.m"
    program_text = "a\na\nm"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "err_force_filter_get_data" do
    policy_text = "((!g)*.g.f.(!g)*)*"
    program_text = "s\ns\ng\nf\ns\ns\ns\ng"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end


  test "ok_zero" do
    policy_text = "!(0)"
    program_text = "a"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

end
