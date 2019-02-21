defmodule MicroDataCore.Core do
  use Memoize
  require Logger
  @moduledoc false


  @doc """
  Main input for our Core module. It takes (policy, program, data)
  and recursively evaluates it, until the program is empty.
  """
  def process_request(policy, program, data) do
    Logger.info("-----------------------------")
    Logger.info("Starting running (policy, program): #{inspect({policy, program})}")
    Logger.info("-----------------------------")
    var_scope = %{}
    case program_step(policy, program, data, var_scope) do
      {:error, msg} -> Logger.error("Error running program: #{inspect(msg)}")
                       {:error, msg}
      {:ok, data} -> Logger.info("Success. Received data: #{inspect(data)}")
                     {:ok, data}
    end
  end

  def program_step(policy, [[:exec, command] | program], data, var_scope) do
    Logger.info("-----------------------------")
    Logger.info("Performing step on (policy, program): #{inspect({policy, [command | program]})}")
    Logger.info("-----------------------------")
    case d_step(policy, command) do
      {:error, msg} -> {:error, msg}
      0 -> {:error, "Early stop."}
      policy ->
        case execute_command(command, data) do
          {:error, msg} -> {:error, msg}
          {:ok, _, data} -> program_step(policy, program, data, var_scope)
        end
    end
  end

  def program_step(policy, [[:assign, var, command] | program], data, var_scope) do
    Logger.info("-----------------------------")
    Logger.info("Assignment: #{inspect({policy, [:assign, var, command]})}")
    Logger.info("-----------------------------")
    case d_step(policy, command) do
      {:error, msg} -> {:error, msg}
      0 -> {:error, "Early stop."}
      policy ->
        case execute_command(command, data) do
          {:error, msg} -> {:error, msg}
          {:ok, value, data} ->
            var_scope = Map.put(var_scope, var, value)
            Logger.error("var_scope: #{inspect({var_scope, var, value})}")
            program_step(policy, program, data, var_scope)
        end
    end
  end

  @doc """
  Final step of the evaluation. If the policy passes E step
  MicroDataCore.Core.e_step/1 then we return data otherwise, fail
  """
  def program_step(policy, [], data, _var_scope) do
    case e_step(policy) do
      1 -> {:ok, data}
      0 -> {:error, "Couldn't advance policy."}
    end
  end

  @doc """
  Perform policy advancement step to decide if we can evaluate the program.
  """
  defmemo d_step(policy, command) do
    Logger.debug("D step on (policy, command): #{inspect({policy, command})}")
    res = case policy do
      1 -> 1
      0 -> 0

      [:exec, :anyf] -> 1
      [:exec, c] when command == c -> 1
      [:exec, c] when command != c -> 0
      [:concat, p1, p2] ->
        simplify(
          [
            :union,
            simplify([:concat, d_step(p1, command), p2]),
            simplify([:concat, e_step(p1), d_step(p2, command)])
          ]
        )
      [:union, p1, p2] -> simplify([:union, d_step(p1, command), d_step(p2, command)])
      [:star, p] -> simplify([:concat, d_step(p, command), [:star, p]])
      [:intersect, p1, p2] -> [:intersect, d_step(p1, command), d_step(p2, command)]
      [:neg, p] -> [:neg, d_step(p, command)]
      _ -> {:error, "Error parsing following policy: #{inspect(policy)}"}
    end
    Logger.debug("Output D step (REVERSE ORDER): #{inspect({policy, command, res})}")
    res
  end

  @doc """
  As we evaluate D(P,C) the policy grows very quickly.
  This is an effort to keep it small and readable by removing
  trivial logical expressions.
  """
  defmemo simplify(policy) do
    Logger.debug("reducing: #{inspect(policy)}")
    case policy do

      # if it changes, i.e. we add XOR, need to be specific
      [_, 0, 0] -> 0
      [_, 1, 1] -> 1

      [:concat, 0, _] -> 0
      [:concat, _, 0] -> 0
      [:concat, 1, p] -> simplify(p)
      [:concat, p, 1] -> simplify(p)
      [:concat, p1, p2] -> [:concat, simplify(p1), simplify(p2)]

      [:intersect, 0, _] -> 0
      [:intersect, _, 0] -> 0
      [:intersect, 1, p] -> simplify(p)
      [:intersect, p, 1] -> simplify(p)
      [:intersect, p, p] -> simplify(p)
      [:intersect, [c, p1, p2], [c, p2, p1]] when c in [:union, :intersect] -> simplify([c, p1, p2])
      [:intersect, p1, p2] -> [:intersect, simplify(p1), simplify(p2)]

      [:union, 0, p] -> simplify(p)
      [:union, p, 0] -> simplify(p)
      [:union, 1, _] -> 1
      [:union, _, 1] -> 1
      [:union, p, p] -> simplify(p)
      [:union, [c, p1, p2], [c, p2, p1]] when c in [:union, :intersect] -> simplify([c, p1, p2])
      [:union, p1, p2] -> [:union, simplify(p1), simplify(p2)]

      [:star, p] -> [:star, simplify(p)]

      p -> p
    end
  end

  @doc """
  Rules to allow data release:
    E(0) = E(C) = 0
    E(1) = 1
    E(P1 . P2) = E(P1) . E(P2)
    E(P1 + P2) = E(P1) + E(P2)
    E(P*) = 1
  """

  defmemo e_step(policy) do

    res = case policy do
      0 -> 0
      1 -> 1
      [:concat, p1, p2] -> e_step(p1) * e_step(p2)
      [:intersect, p1, p2] -> e_step(p1) * e_step(p2)
      [:union, p1, p2] -> max(e_step(p1), e_step(p2))
      [:star, _] -> 1
      [:neg, p] -> abs(e_step(p) - 1)
      _ -> 0
    end
    Logger.debug("E Step received [policy, res] (REVERSE ORDER!): #{inspect({policy, res})}")
    res
  end

  @doc """
  We just mock the actual function execution. TBD
  """
  def execute_command(function, data) do
    Logger.debug("Function and data: #{inspect({function, data})}")
    case function do
      "error" -> {:error, "Error execution function :(."}
      _ -> {:ok, 42, Map.put(data, Time.utc_now(), {function})}
    end
  end

  @doc """
  Used to execute cli commands. For debugging
  """
  def start() do
    [policy_file, program_file] = System.argv()
    {:ok, policy_text} = File.read(policy_file)
    {:ok, program_text} = File.read(program_file)
    entry_point([policy_text, program_text])
  end

  @doc """
  Still used for debugging purposes: reads policies and programs
  and evaluates them.
  """
  def entry_point([policy_string, program_string]) do
    policy = MicroDataCore.Parser.parse_policy(policy_string)
    program = MicroDataCore.Parser.parse_program(program_string)
    Logger.info("policy: #{inspect(policy)}")
    Logger.info("program: #{inspect(program)}")
    case process_request(policy, program, %{:data => true}) do
      {:ok, data} -> Logger.info("Success. Received data: #{inspect(data)}")
                     {:ok, data}
      {:error, msg} -> Logger.error("Error evaluating program and policy. Message: #{inspect(msg)}")
                       {:error, %{}}
      _ -> Logger.error("Error")
           {:error, %{}}

    end
  end

end
