defmodule MicroDataCore.Parser do
  @moduledoc false


  def parse_program(file) do
    {:ok, text_program} = File.read(file)
    text_program
    |> String.downcase()
    |> parse_program([])

  end

  def parse_policy(file) do
    {:ok, text} = File.read(file)
    text
    |> String.downcase()
    |> parse_policy(10)
  end

  @doc """
  Just parses programs like:
    c1;
    c2;
    c3
  Will add more complex logic later
  """
  def parse_program(program, state) do
    #    IO.inspect(program)
    #    IO.inspect(state)
    program = String.split(program, ";\n", parts: 2, trim: true)
    #    IO.inspect(program)
    case program do
      [command, prog] -> [parse_program(command, nil) | parse_program(prog, state)]

      [command] ->
        case state do
          nil -> String.trim(command)
          _ -> [String.trim(command) | state]
        end

      _ -> raise "Syntax error. Check your program syntax."
    end

  end

  @doc """
  parse policies initial format:
  """
  def parse_policy(policy, counter) when counter > 0 do

    #    IO.inspect(policy, label: "policy: ")
    #    IO.inspect(counter, label: "counter: ")

    # match for concatenation
    case String.split(policy, ".", parts: 2, trim: true) do
      [p, sub_tree] -> [:concat, [parse_policy(p, counter - 1), parse_policy(sub_tree, counter - 1)]]
      [p] ->
        case  String.split(p, "+", parts: 2, trim: true) do
          [p, sub_tree] -> [:union, [parse_policy(p, counter - 1), parse_policy(sub_tree, counter - 1)]]
          ["0"] -> :null
          [p] ->
            cond  do
              String.ends_with?(p, "*") -> [:star, String.slice(p, 0..-2)]
              true ->
                [:exec, String.trim(p)]
            end

        end

      _ -> raise "Syntax error. Check your program syntax."

    end

  end

  def parse_policy(policy, counter) when counter == 0 do
    #    IO.inspect(policy, label: "last policy: ")
    policy
  end


  def entry_point([policy_file, program_file]) do
    policy = parse_policy(policy_file)
    program = parse_program(program_file)
    #    IO.inspect(policy, label: "policy: ")
    #    IO.inspect(program, label: "program: ")
    case process_request(policy, program, %{:data => true}) do
      {:ok, data} -> IO.inspect(data, label: "Success. Received data: ")
      {:error} -> IO.puts("Policy didn't match submitted program. ")
      _ -> IO.puts("Error")
    end

    IO.puts("completed")
    :ok
  end

  def entry_point(_param) do
    {:ok}
  end

  def process_request(policy, program, data) do
    IO.inspect({policy, program}, label: "Performing step on (policy, program): \n")
    with [hd | tl] <- program,
         {:one, policy} <- step(policy, hd) do
      process_request(policy, tl, execute_command(hd, data))
    else
      [] -> {:ok, data}
      {:error} -> {:error}
    end
  end



  def step(policy, command) do

    IO.inspect({policy, command}, label: "Performing step on (policy, program): \n")
    # [:exec, command] when command == hd(program) -> {:ok, execute_command(command, data)}

    {:one, []}

  end


  def execute_command(function, data) do
    IO.inspect({function, data}, label: "Function and data: ")
    #    %{data | :data => 200}
    Map.put(data, Time.utc_now(), {function})
  end


end

System.argv()
|> MicroDataCore.Parser.entry_point()