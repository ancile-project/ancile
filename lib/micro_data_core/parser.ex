defmodule MicroDataCore.Parser do
  require Logger
  @moduledoc false

  @doc """
  Uses Yacc/Lex parser to parse programs
  """
  def parse_program(text) do
    {:ok, tokens, _} = text
                       |> to_charlist()
                       |> :program_lexer.string()
    Logger.debug("input program text, tokens, and parsed program: #{inspect({text, tokens})}")
    {:ok, list} = :program_parser.parse(tokens)
    Logger.debug("input program text, tokens, and parsed program: #{inspect({text, tokens, list})}")
    list
  end

  @doc """
  Uses Yacc/Lex parser to parse policies
  """
  def parse_policy(text) do
    {:ok, tokens, _} = text
                       |> to_charlist()
                       |> :policy_lexer.string()
    {:ok, list} = :policy_parser.parse(tokens)
    Logger.debug("input policy text, tokens, and parsed policy: #{inspect({text, tokens, list})}")
    list
  end



end


