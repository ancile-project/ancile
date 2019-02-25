defmodule MicroDataCoreTest do
  use ExUnit.Case
  #  doctest MicroDataCore

  test "exact_match" do
    policy_text = "get_data.get_data.filter_data(limit: 40).remove_data.get_data.return"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "anyf*_in_the_middle" do
    policy_text = "get_data.get_data.filter_data(limit: 40).ANYF*.return"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "single_anyf*" do
    policy_text = "ANYF*.return"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "reduce_repeated_func_with_*" do
    policy_text = "get_data*.filter_data(limit: 40).remove_data.get_data.return"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_wrong_func" do
    policy_text = "get_data.get_data.WRONG.remove_data.get_data.return"
    {:ok, program_text} = File.read("test/programs/complex.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "force_filter_simple" do
    policy_text = "get_data.[filter_data+remove_data]*.return"
    program_text = "get_data; filter_data; remove_data; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "ok_neg" do
    policy_text = "a.b.![a].c.return"
    program_text = "a; b; d; c;return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg" do
    policy_text = "a.b.![a].c.return"
    program_text = "a; b; a; c;return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_intersect" do
    policy_text = "[a&ANYF].return"
    program_text = "a;return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "ok_intersect_union" do
    policy_text = "[a&[b+a]].d.return"
    program_text = "a; d; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_intersect" do
    policy_text = "[a&b].return"
    program_text = "a; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end



  ##############################
  # NEGATION TESTS
  ##############################

  test "ok_neg_concat" do
    policy_text = "k.![[g.f]].k.return"
    program_text = "k; f; g; k; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_concat" do
    policy_text = "![g.f].return"
    program_text = "g; f; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_neg_concat_first_match" do
    policy_text = "![[g.f]].return"
    program_text = "g; q; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end
  #
  test "ok_neg_union" do
    policy_text = "![[g+f]].m.return"
    program_text = "d; m; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_union" do
    policy_text = "![[g+f]].m.k.return"
    program_text = "f; m; k; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end


  test "ok_neg_star_inside" do
    policy_text = "![a*].return"
    program_text = "b; b; b; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_star_inside" do
    policy_text = "![a*].return"
    program_text = "a; a; a; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_neg_star_outside" do
    policy_text = "[![a]]*.m.return"
    program_text = "d; m; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_neg_outside" do
    policy_text = "[![a]]*.m.return"
    program_text = "a; a; m; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "big_case" do
    policy_text = "[[[[[a.a.m]*.return + [a.m]*]] * + [[[a.m*]* + [a.a.b.m]*]] *]]*.return"
    program_text = "a; a; m; a; a; m; a; a; m; a; a; m; a; a; m; a; a; m; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "big_case_2" do
    policy_text = "[[[[[[a.a.m]*.return + [a.m]*]] * + [[[a.m*]* + [a.a.b.m]*]] *]]* + [[[[[a.b.m]* + [a.c]*]] * + [[[k.m*]* + [k.a.b.j]*]] *]]*]"
    program_text = "a; a; m; a; a; m; a; a; m; a; a; m; a; a; m; a; a; m; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "ok_assignment" do
    policy_text = "return"
    program_text = "z := 4; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "ok_two_assignment" do
    policy_text = "return"
    program_text = "z := 4; j := 5; return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "ok_if_assignment" do
    policy_text = "a.return"
    program_text = "z := 5; j := 5; if z=j do a; end return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "err_if_assignment" do
    policy_text = "a.return"
    program_text = "z := 4; j := 5; if z=j do a; end return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "ok_nested_if_assignment" do
    policy_text = "a.b.return"
    program_text = "z := 4; j := 4; if z=j do a; q:=4; if z=q do b; end end return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "ok_scoping_test_assignment" do
    policy_text = "a.b.return"
    program_text = "z := 4; j := 4; if z=j do a; q:=4; end if z=q do b; end return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :error
  end

  test "function_params_check" do
    policy_text = "a(c:4, d:9).b(c:9, d:10).y().return"
    program_text = "a(c:4, d:9); b(c:9, d:10); y(); return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "function_params_check_small" do
    policy_text = "a(x:4, y:9).return"
    program_text = "a(x:4, y:9); return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "ok_test_small" do
    {result, _} = MicroDataCore.Core.entry_point(["a.b.return", "a; b; return;"])
    assert result == :ok
  end

  test "string_args" do
    {result, _} = MicroDataCore.Core.entry_point(["a.b(a:\"5\").return", "a;b(a:\"5\"); return;"])
    assert result == :ok
  end

  test "float args" do
    policy_text = "a(x:5.0, y:-9.7).return"
    program_text = "a(x:5.0, y:-9.7); return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "float args2" do
    policy_text = "a(x:+2.8121321, y:0.7).return"
    program_text = "a(x:2.8121321, y:0.7); return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "string args2" do
    policy_text = "a(x:\" 2552 \", y:\"?????\").return"
    program_text = "a(x:\" 2552 \", y:\"?????\"); return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "string args3" do
    policy_text = "a(x:\" abcdefghijklmnopqrstuv #()()() \", y:\"][][][][][][][][][}{}{}{}{}{}{}{}{\").return"
    program_text = "a(x:\" abcdefghijklmnopqrstuv #()()() \", y:\"][][][][][][][][][}{}{}{}{}{}{}{}{\"); return;"
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end

  test "else test" do
    policy_text = "nothing.yet_further_nothing.return"
    {:ok, program_text} = File.read("test/programs/else.txt")
    {result, _} = MicroDataCore.Core.entry_point([policy_text, program_text])
    assert result == :ok
  end
  
end
