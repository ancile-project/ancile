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
      [p, sub_tree] -> [:concat, parse_policy(p, counter - 1), parse_policy(sub_tree, counter - 1)]
      [p] ->
        case  String.split(p, "+", parts: 2, trim: true) do
          [p, sub_tree] -> [:union, parse_policy(p, counter - 1), parse_policy(sub_tree, counter - 1)]
          ["0"] -> 0
          ["1"] -> 1
          ["0*"] -> 1
          ["ANYF"] -> :anyf
          [p] ->
            cond  do
              String.ends_with?(p, "*") -> [:star, String.slice(p, 0..-2)]
              true -> [:exec, String.trim(p)]
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

  def process_request(policy, [], data) do
    case e_step(policy) do
      1 -> {:ok, data}
      0 -> {:error}
    end
  end

  def process_request(policy, [command | program], data) do
    IO.puts("\n-----------------------------\n")
    IO.inspect({policy, [command | program]}, label: "Performing step on (policy, program): \n")
    IO.puts("\n-----------------------------\n")
    case d_step(policy, command) do
      :error -> {:error}
      0 -> IO.puts("Early stop. No need to proceed as policy doesn't match.")
           {:error}
      policy -> process_request(policy, program, execute_command(command, data))
      #           {:error}
    end
  end


  def d_step(policy, command) do
    IO.inspect({policy, command}, label: "D step on (policy, command): ")
    case policy do
      [:exec, c] when command == c -> 1
      [:exec, c] when command != c -> 0
      [:exec, :anyf] -> 1
      [:concat, p1, p2] ->
        simplify(
          [
            :union,
            simplify([:concat, d_step(p1, command), p2]),
            simplify([:concat, e_step(p1), d_step(p2, command)])
          ]
        )
      [:union, p1, p2] -> simplify([:union, d_step(p1, command), d_step(p2, command)])
      [:star, p] -> simplify([:concat, d_step([:exec, p], command), [:star, p]])
      1 -> 0
      # because D(1,C) = D(0*,C) = D(0, C).0* = 0.0* = 0
      0 -> 0
      _ -> :error
    end
  end

  def simplify(policy) do
    IO.inspect(policy, label: "reducing: ")
    case policy do
      [:concat, 0, _] -> 0
      [:concat, _, 0] -> 0
      [:concat, 1, p] -> simplify(p)
      [:concat, p, 1] -> simplify(p)
      [:concat, 1, 1] -> 1
      [:union, 0, p] -> simplify(p)
      [:union, p, 0] -> simplify(p)
      [:union, 1, _] -> 1
      [:union, _, 1] -> 1
      [:union, 0, 0] -> 0
      [:concat, p1, p2] -> [:concat, simplify(p1), simplify(p2)]
      [:union, p1, p2] -> [:union, simplify(p1), simplify(p2)]
      [:star, p] -> [:star, simplify(p)]
      p -> p
    end
  end

  def e_step(policy) do
    IO.inspect(policy, label: "E Step received: ")
    case policy do
      0 -> 0
      1 -> 1
      # conjunction
      [:concat, p1, p2] -> e_step(p1) * e_step(p2)
      # disjunction
      [:union, p1, p2] -> max(e_step(p1), e_step(p2))
      [:star, _] -> 1
      _ -> 0
    end
  end


  def execute_command(function, data) do
    IO.inspect({function, data}, label: "Function and data: ")
    Map.put(data, Time.utc_now(), {function})
  end


end

System.argv()
|> MicroDataCore.Parser.entry_point()