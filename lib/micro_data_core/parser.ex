defmodule MicroDataCore.Parser do
  @moduledoc false

  @doc """
  Uses Yacc/Lex parser to parse programs
  """
  def parse_program(text) do
    {:ok, tokens, _} = text
                       |> to_charlist()
                       |> :program_lexer.string()
    {:ok, list} = :program_parser.parse(tokens)
    list
  end

  @doc """
  Uses Yacc/Lex parser to parse policies
  """
  def parse_policy(text) do
    IO.inspect(text, label: "input policy: ")
    {:ok, tokens, _} = text
                       |> to_charlist()
                       |> :policy_lexer.string()
    {:ok, list} = :policy_parser.parse(tokens)
    list
  end



end


