defmodule MicroDataCore.Core do
  require Logger
  @moduledoc false


  @doc """
  Main input for our Core module. It takes (policy, program, data)
  and recursively evaluates it, until the program is empty.
  """
  def process_request(policy, [command | program], data) do
    Logger.info("-----------------------------")
    Logger.info("Performing step on (policy, program): #{inspect({policy, [command | program]})}")
    Logger.info("-----------------------------")
    case d_step(policy, command) do
      :error -> {:error}
      0 -> Logger.info("Early stop. No need to proceed as policy doesn't match.")
           {:error}
      policy -> process_request(policy, program, execute_command(command, data))
    end
  end

  @doc """
  Final step of the evaluation. If the policy passes E step
  MicroDataCore.Core.e_step/1 then we return data otherwise, fail
  """
  def process_request(policy, [], data) do
    case e_step(policy) do
      1 -> {:ok, data}
      0 -> {:error}
    end
  end

  @doc """
  Perform policy advancement step to decide if we can evaluate the program.
  """
  def d_step(policy, command) do
    Logger.debug("D step on (policy, command): #{inspect({policy, command})}")
    res = case policy do
      # because D(1,C) = D(0*,C) = D(0, C).0* = 0.0* = 0. Sorry :)
      1 -> 0
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
      _ -> throw "Error parsing"
    end
    Logger.debug("Output D step (REVERSE ORDER): #{inspect({policy, command, res})}")
    res
  end

  @doc """
  As we evaluate D(P,C) the policy grows very quickly.
  This is an effort to keep it small and readable by removing
  trivial logical expressions.
  """
  def simplify(policy) do
    Logger.debug("reducing: #{inspect(policy)}")
    case policy do
      [:concat, 0, _] -> 0
      [:concat, _, 0] -> 0
      [:concat, 1, p] -> simplify(p)
      [:concat, p, 1] -> simplify(p)
      [:concat, 1, 1] -> 1
      [:concat, p1, p2] -> [:concat, simplify(p1), simplify(p2)]

      [:intersect, 0, _] -> 0
      [:intersect, _, 0] -> 0
      [:intersect, 1, p] -> simplify(p)
      [:intersect, p, 1] -> simplify(p)
      [:intersect, 1, 1] -> 1
      [:intersect, p1, p2] -> [:intersect, simplify(p1), simplify(p2)]

      [:union, 0, p] -> simplify(p)
      [:union, p, 0] -> simplify(p)
      [:union, 1, _] -> 1
      [:union, _, 1] -> 1
      [:union, 0, 0] -> 0

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

  def e_step(policy) do

    res = case policy do
      0 -> 0
      # E(1) = E(0*) = 1, unlike D(1,C) = 0
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
    Map.put(data, Time.utc_now(), {function})
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
      {:error} -> Logger.error("Policy didn't match submitted program. ")
                  {:error, %{}}
      _ -> Logger.error("Error")
           {:error, %{}}

    end

  end

end
