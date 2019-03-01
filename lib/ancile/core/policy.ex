defmodule Ancile.Core.Policy do
  use Ecto.Schema
  import Ecto.Changeset


  schema "policies" do
    field :active, :boolean, default: false
    field :policy, :binary
    field :purpose, :string
    field :app_id, :id
    field :user_id, :id

    timestamps()
  end

  @doc false
  def changeset(policy, attrs) do
    policy
    |> cast(attrs, [:app_id, :user_id, :purpose, :policy, :active])
    |> validate_required([:app_id, :user_id, :purpose, :policy, :active])
  end
end
