defmodule MicroDataCore.Core do
  @moduledoc false


  def entry_point([policy_string, program_string]) do
    policy = MicroDataCore.Parser.parse_policy(policy_string)
    program = MicroDataCore.Parser.parse_program(program_string)
    IO.inspect(policy, label: "policy: ")
    IO.inspect(program, label: "program: ")
    case process_request(policy, program, %{:data => true}) do
      {:ok, data} -> IO.inspect(data, label: "Success. Received data: ")
                     {:ok, data}
      {:error} -> IO.puts("Policy didn't match submitted program. ")
                  {:error, %{}}
      _ -> IO.puts("Error")
           {:error, %{}}

    end

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
      [:star, p] -> simplify([:concat, d_step([:exec, p], command), [:star, p]])
      1 -> 0
      # because D(1,C) = D(0*,C) = D(0, C).0* = 0.0* = 0. Sorry :)
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
      # E(1) = E(0*) = 1, unlike D(1,C) = 0
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

  def start() do
    [policy_file, program_file] = System.argv()
    {:ok, policy_text} = File.read("test/policies/simple.txt")
    {:ok, program_text} = File.read("test/programs/simple.txt")
    entry_point([policy_text, program_text])
  end

end
