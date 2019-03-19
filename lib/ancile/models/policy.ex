defmodule Ancile.Models.Policy do
  use Ecto.Schema
  import Ecto.Changeset


  schema "policies" do
    field :active, :boolean, default: false
    field :policy, :binary, default: nil
    field :purpose, :string, default: nil
    field :provider, :string, default: nil
    field :app_id, :id, default: nil
    field :user_id, :id, default: nil

    timestamps()
  end

  @doc false
  def changeset(policy, attrs) do
    policy
    |> cast(attrs, [:app_id, :user_id, :purpose, :policy, :active, :provider])
    |> validate_required([:app_id, :user_id, :purpose, :policy, :active, :provider])
  end
end
