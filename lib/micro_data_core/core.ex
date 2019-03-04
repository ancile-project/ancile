defmodule MicroDataCore.Core do
  use Memoize
  require Logger

  alias MicroDataCore.Utilities.TypeTools
  require TypeTools

  @moduledoc false



  @doc """
  Main input for our Core module. It takes (policy, program, data)
  and recursively evaluates it, until the program is empty.
  """
  def process_request(policy, program, data, sensitive_data) do
    Logger.info("-----------------------------")
    Logger.info("Starting running (policy, program): #{inspect({policy, program})}")
    Logger.info("-----------------------------")
    var_scope = %{}
    case program_step(policy, program, data, var_scope, sensitive_data) do
      {_, [], _, _} -> Logger.info("No 'return' command specified in the end, returning nothing...")
                       {:error, []}
      {:error, msg} -> Logger.error("Error running program: #{inspect(msg)}")
                       {:error, msg}
      {:ok, data} -> Logger.info("Success. Received data: #{inspect(data)}")
                     {:ok, data}
    end
  end

  @doc """
  We use it to evaluate sub loops, like if/for/while and preserve state of
  variables. As well, we want to execute program, but don't need to return data.
  """
  def program_step(policy, [], data, var_scope, _sensitive_data) do
    {policy, [], data, var_scope}
  end

  @doc """
  Final step of the evaluation, requires `return`. If the policy passes E step
  MicroDataCore.Core.e_step/1 then we return data otherwise, fail.
  """
  def program_step(policy, [[:exec, :return]], data, _var_scope, _sensitive_data) do
    Logger.info("-----------------------------")
    Logger.info("Performing last step on (policy, program): #{inspect({policy, :return})}")
    Logger.info("-----------------------------")
    with {:ok, policy} <- d_step(policy, :return),
         1 <- e_step(policy) do
      {:ok, data}
    else
      {:error, msg} -> {:error, msg}
      _ -> {:error, "Couldn't advance policy."}
    end
  end

  @doc """
  Basic step to execute a command from the program.
  It doesn't use scope variables and just updates data.
  """
  def program_step(policy, [[:exec, command] | program], data, var_scope, sensitive_data) do
    Logger.info("-----------------------------")
    Logger.info("Performing step on (policy, program): #{inspect({policy, [command | program]})}")
    Logger.info("-----------------------------")
    case d_step(policy, command) do
      {:error, msg} -> {:error, msg}
      {:ok, 0} -> {:error, "Early stop."}
      {:ok, policy} ->
        case MicroDataCore.FunctionRunner.execute_command(command, data, sensitive_data) do
          {:error, msg} -> {:error, msg}
          {:ok, _, data} -> program_step(policy, program, data, var_scope, sensitive_data)
        end
    end
  end

  @doc """
  Uses x:= number/float to update variable scope.
  """
  def program_step(policy, [[:assign, var, value] | program], data, var_scope, sensitive_data)
      when is_number(value) or is_binary(value) do
    Logger.info("-----------------------------")
    Logger.info("Assignment: #{inspect({policy, [:assign, var, value]})}")
    Logger.info("-----------------------------")
    var_scope = Map.put(var_scope, var, value)
    Logger.error("Updated var_scope: #{inspect({var_scope, var, value})}")
    program_step(policy, program, data, var_scope, sensitive_data)
  end


  @doc """
  Uses x:= command to update variable scope.
  """
  def program_step(policy, [[:assign, var, command] | program], data, var_scope, sensitive_data) do
    Logger.info("-----------------------------")
    Logger.info("Assignment: #{inspect({policy, [:assign, var, command]})}")
    Logger.info("-----------------------------")
    with {:ok, policy} <- d_step(policy, command),
         {:ok, data, var_scope} <- assign_eval_result(var, command, data, var_scope, sensitive_data)
      do
      program_step(policy, program, data, var_scope, sensitive_data)
    else
      {:error, msg} -> {:error, msg}
    end
  end


  @doc """
  Implements `if clause do commands end` to update variable scope.
  After clause passes we evaluate `commands` in a new scope, after
  commands executed we evaluate the remaining program in the old scope.
  @TODO add else clause
  """
  def program_step(policy, [[:if, clause, commands] | program], data, var_scope, sensitive_data) do
    Logger.info("-----------------------------")
    Logger.info("If scope: #{inspect({policy, [:if, clause, commands]})}")
    Logger.info("-----------------------------")

    case eval_clause(policy, clause, data, var_scope) do
      {:error, msg} -> {:error, msg}
      false -> program_step(policy, program, data, var_scope, sensitive_data)
      true ->

        case program_step(policy, commands, data, var_scope, sensitive_data) do
          {:error, msg} -> {:error, msg}
          {policy, [], data, _} -> program_step(policy, program, data, var_scope, sensitive_data)
        end
    end
  end

  @doc """
  Implements `if clause do commands else else_commands end` to update variable scope.
  After clause passes we evaluate `commands` in a new scope, after
  commands executed we evaluate the remaining program in the old scope.
  
  If clause fails, we evaluate `else-commands` in a new scope and return to the 
  old scope after execution finishes.
  """
  def program_step(policy, [[:if, clause, commands, else_commands] | program], data, var_scope, sensitive_data) do
    Logger.info("-----------------------------")
    Logger.info("If scope: #{inspect({policy, [:if, clause, commands, else_commands]})}")
    Logger.info("-----------------------------")

    # NOTE: this feels a bit messy. We should probably see if there
    #  is a cleaner way to do this.
    case eval_clause(policy, clause, data, var_scope) do
      {:error, msg} -> {:error, msg}
      false ->
        case program_step(policy, else_commands, data, var_scope, sensitive_data) do
          {:error, msg} -> {:error, msg}
          {policy, [], data, _} -> program_step(policy, program, data, var_scope, sensitive_data)
        end

      true ->
        case program_step(policy, commands, data, var_scope, sensitive_data) do
          {:error, msg} -> {:error, msg}
          {policy, [], data, _} -> program_step(policy, program, data, var_scope, sensitive_data)
        end
    end
  end

  @doc """
  We run the command that returns {ok, value, data}. We then
  assign value to variable `var` and put them into `var_scope`.
  """
  def assign_eval_result(var, command, data, var_scope, sensitive_data) do
    Logger.debug("Assign value to `#{inspect(var)}` be running: `#{inspect(command)}`")
    case MicroDataCore.FunctionRunner.execute_command(command, data, sensitive_data) do
      {:error, msg} -> {:error, msg}
      {:ok, value, data} ->
        var_scope = Map.put(var_scope, var, value)
        Logger.error("var_scope: #{inspect({var_scope, var, value})}")
        {:ok, data, var_scope}
    end
  end

  @doc """
  Compute parameter fetch from variable scope and call comparator.
  @TODO: add int/float/string as left or right params
  """
  def eval_clause(_policy, [:comp, compare_symbol, var1, var2], _data, var_scope) do
    with {:ok, left_val} <- get_value_from_var(var1, var_scope),
         {:ok, right_val} <- get_value_from_var(var2, var_scope)
      do
      comparison(compare_symbol, left_val, right_val)
    else
      {:error, msg} -> {:error, msg}
    end
  end

  @doc """
  Compares two values.
  """
  def comparison(operation, val1, val2) when
        TypeTools.comparable(val1, val2) and
        TypeTools.valid_comparison_operator(operation) do
    Logger.debug("Evaluation comparison #{inspect(val1)} #{inspect(operation)} #{inspect(val2)}")
    # NOTE: We should think about whether we want strict comparisons 
    #  or guards since types can determine an ordering amongst unlike 
    #  things like an int and a string.
    #    This will, however, judge equivalent floats and ints to be 
    #  the same, which is probably good.
    case operation do
      '=' -> val1 == val2
      '>' -> val1 > val2
      '<' -> val1 < val2
      '>=' -> val1 >= val2
      '<=' -> val1 <= val2
      '!=' -> val1 != val2
    end
  end

  def comparison(operation, _val1, _val2) when
        not TypeTools.valid_comparison_operator(operation) do
    # This catches invalid comparison parameter and errors on them
    # first
    {:error, "Wrong comparison parameter: #{inspect(operation)}"}
  end

  def comparison(operation, val1, val2) do
    # If the operator is correct then this means the given
    # operands were incompatible
    {:error, "Incompatible operands #{val1} #{inspect(operation)} #{val2}"}
  end

  @doc """
  Fetches value from var scope. Returns error if no value found.
  """
  def get_value_from_var(var, var_scope) do
    case Map.get(var_scope, var) do
      nil -> {:error, "No variable with name #{inspect(var)} in scope #{inspect(var_scope)}"}
      val -> {:ok, val}
    end
  end


  @doc """
  Perform policy advancement step to decide if we can evaluate the program.
    D(0,_) = 0
    D(C, C') = if C != C' then 0 else 1
    D(P1 . P2, C) = D(P1,C) . P2 + E(P1) . D(P2, C)
    D(P1 + P2, C) = D(P1, C) + D(P2, C)
    D(P*, C) = D(P,C) . P*
    D(P1 & P2, C) = D(P1, C) & D(P2, C)
    D(!P, C) = !D(P,C)

    @TODO: I had to use elem(d_step(), 1) to drop :ok from the response, will need
    to fix it later. However, always returning, either {:ok, result} or
    {:error, msg} is really convenient.
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
            simplify([:concat, elem(d_step(p1, command), 1), p2]),
            simplify([:concat, e_step(p1), elem(d_step(p2, command), 1)])
          ]
        )
      [:union, p1, p2] -> simplify([:union, elem(d_step(p1, command), 1), elem(d_step(p2, command), 1)])
      [:star, p] -> simplify([:concat, elem(d_step(p, command), 1), [:star, p]])
      [:intersect, p1, p2] -> [:intersect, elem(d_step(p1, command), 1), elem(d_step(p2, command), 1)]
      [:neg, p] -> [:neg, elem(d_step(p, command), 1)]
      _ -> {:error, "Error parsing following policy: #{inspect(policy)}"}
    end
    Logger.debug("Output D step (REVERSE ORDER): #{inspect({policy, command, res})}")
    case res do
      {:error, msg} -> {:error, msg}
      policy -> {:ok, policy}
    end
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
    E(P1 . P2) = E(P1) /\ E(P2)
    E(P1 & P2) = E(P1) /\ E(P2)
    E(P1 + P2) = E(P1) \/ E(P2)
    E(P*) = 1
    E(!P) = !P
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
    case process_request(policy, program, %{:data => true}, %{}) do
      {:ok, data} -> Logger.info("Success. Received data: #{inspect(data)}")
                     {:ok, data}
      {:error, msg} -> Logger.error("Error evaluating program and policy. Message: #{inspect(msg)}")
                       {:error, %{}}
      _ -> Logger.error("Error")
           {:error, %{}}
    end
  end

  def phoenix_entry(policy_string, program_string, sensitive_data) do
    policy = MicroDataCore.Parser.parse_policy(policy_string)
    program = MicroDataCore.Parser.parse_program(program_string)
    Logger.info("policy: #{inspect(policy)}")
    Logger.info("program: #{inspect(program)}")
    case process_request(policy, program, %{}, sensitive_data) do
      {:ok, data} -> Logger.info("Success. Received data: #{inspect(data)}")
                     {:ok, data}
      {:error, msg} -> Logger.error("Error evaluating program and policy. Message: #{inspect(msg)}")
                       {:error, %{}}
      _ -> Logger.error("Error")
           {:error, %{}}
    end
  end

end
