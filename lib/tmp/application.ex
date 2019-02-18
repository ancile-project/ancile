#defmodule MicroDataCore.Application do
#  use Supervisor
#
#  @moduledoc """
#  Documentation for MicroDataCore.
#  """
#
#
#  def start(_type, _args) do
#    children = [
#      {MicroDataCore.PolicyParser, [:policy]},
#      {MicroDataCore.RequestGenerator, [:requests]}
#    ]
#    IO.puts("app start")
#    {:ok, pid} = Supervisor.start_link(children, strategy: :one_for_one, name: :policy)
#    IO.inspect(pid)
#
#    IO.inspect(Supervisor.which_children(pid))
#    IO.inspect(Supervisor.count_children(pid))
#    GenServer.call(MicroDataCore.RequestGenerator, "hello")
#    {:ok, pid}
#  end
#
#
#
#end
