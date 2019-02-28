defmodule Ancile.Models.Policy do
  use Ecto.Schema
  import Ecto.Changeset
  @moduledoc false

  schema "policies" do
    field :app_id, :integer, default: nil
    field :user_id, :integer, default: nil
    field :purpose, :string, default: nil
    field :policy_text, :binary, default: <<131, 100, 0, 3, 110, 105, 108>> # nil
    field :active, :boolean, default: true

    timestamps()
  end


end
