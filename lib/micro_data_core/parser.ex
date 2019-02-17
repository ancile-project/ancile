defmodule Parser do
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
    |> parse_policy([], 10)
  end

  @doc """
  Just parses programs like:
    c1;
    c2;
    c3
  Will add more complex logic later
  """
  def parse_program(program, state) do
    IO.inspect(program)
    IO.inspect(state)
    program = String.split(program, ";\n", parts: 2, trim: true)
    IO.inspect(program)
    case program do
      [command, prog] -> [parse_program(command, nil) | parse_program(prog,  state)]

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
  def parse_policy(policy, state, counter) when counter > 0 do

    policy = String.split(policy, ".", parts: 2, trim: true)
    IO.inspect(policy, label: "policy: ")
    IO.inspect(state, label: "state: ")
    IO.inspect(counter, label: "counter: ")

    case policy do
      [p, sub_tree ] -> [:concat, [parse_policy(p, nil, counter-1)  , parse_policy(sub_tree, nil, counter-1)  ]]
      [p] ->
        case  String.split(p, "+", parts: 2, trim: true) do
          [p, sub_tree ] -> [:union, [parse_policy(p, nil, counter-1), parse_policy(sub_tree, nil, counter-1)  ]]
          ["0"] -> :null
          [p] ->
            cond  do
              String.ends_with?(p, "*") -> [:star, p |> String.slice(0..-2)]
              true -> [:exec, String.trim(p)]
             end

        end

      _ -> raise "Syntax error. Check your program syntax."

    end

  end

  def parse_policy(policy, state, counter) when counter == 0 do
    IO.inspect(policy, label: "last policy: ")
    policy
    end


end

System.argv()
|> Parser.parse_policy()
|> IO.inspect()
