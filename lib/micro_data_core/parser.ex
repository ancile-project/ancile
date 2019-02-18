defmodule MicroDataCore.Parser do
  @moduledoc false


  def parse_program(text) do
    {:ok, tokens, _} = text
                       |> to_charlist()
                       |> :program_lexer.string()
    {:ok, list} = :program_parser.parse(tokens)
    list
  end

  def parse_policy(text) do
    {:ok, tokens, _} = text
                       |> to_charlist()
                       |> :policy_lexer.string()
    {:ok, list} = :policy_parser.parse(tokens)
    list
  end



end


