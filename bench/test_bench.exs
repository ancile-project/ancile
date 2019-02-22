# bench/basic_bench.exs
defmodule BasicBench do
  use Benchfella
  require Logger


  setup_all do
    depth = :erlang.system_flag(:backtrace_depth, 100)
    {:ok, depth}
  end

  teardown_all depth do
    :erlang.system_flag(:backtrace_depth, depth)
  end

  @list Enum.to_list(1..10000)

  @doc """
  IMPORTANT:
    1. execution function should return the same value every time
    2. delete defmemo from function name, otherwise it fails. NEED TO INVESTIGATE.
  """
  bench "list reverse" do
    MicroDataCore.Core.entry_point(      ["[[[[[[a.a.m]*.return + [a.m]*]] * + [[[a.m*]* + [a.a.b.m]*]] *]]* + [[[[[a.b.m]* + [a.c]*]] * + [[[k.m*]* + [k.a.b.j]*]] *]]*]",
       "a; a; m; a; a; m; a; a; m; a; a; m; a; a; m; a; a; m; return;"])
  end
end