defmodule MicroDataCore.PolicyParser do
  @moduledoc false
  

  use GenServer

  def start_link(state) do
    IO.puts("policy start")
    GenServer.start_link(__MODULE__, state,   name: __MODULE__)

  end

  def init(_opts) do
    {:ok, %{}}
  end

  def handle_call(_msg, _from, state) do
    IO.puts("policy hello")
    {:reply, :ok, state}
  end

  def handle_cast(msg, state) do
    IO.puts("Received program: " <> IO.inspect(msg))
    {:noreply, state}
  end


end