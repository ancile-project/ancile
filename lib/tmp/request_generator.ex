defmodule MicroDataCore.RequestGenerator do
  @moduledoc false
  

  use GenServer

  def start_link(state) do
    IO.puts("request start: ")
    IO.inspect(hd(state))
    GenServer.start_link(__MODULE__, state,  name: __MODULE__)
  end

  def init(_opts) do
    IO.puts("request init")
    MicroDataCore.PolicyParser
    {:ok, %{}}
  end

  def handle_call(_msg, _from, state) do
    IO.puts("request hello")
    IO.puts("starting parsing")
    parsed_program = MicroDataCore.Parser.parse_program(program)
    IO.puts("parsed program: ")
    IO.inspect(parsed_program)
#    GenServer.cast(MicroDataCore.PolicyParser, parsed_program)
    {:reply, :ok, state}
  end

  def handle_cast(_msg, state) do
    {:noreply, state}
  end
end