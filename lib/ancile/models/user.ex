defmodule Ancile.Models.User do
  use Ecto.Schema
  use Pow.Ecto.Schema
  import Ecto.Changeset

  schema "users" do

    has_many :user_identities,
             Ancile.Models.UserIdentity,
             on_delete: :delete_all

    field :role, :string, default: "user"
    field :token, :string, default: nil

    pow_user_fields()

    timestamps()
  end

  def role_changeset(user_or_changeset, attrs) do
    user_or_changeset
    |> cast(attrs, [:role])
    |> validate_inclusion(:role, ~w(user admin pi app))
  end

  def token_changeset(user_or_changeset, attrs) do
    user_or_changeset
    |> cast(attrs, [:token])
  end

  def changeset(user_or_changeset, attrs) do
    user_or_changeset
    |> pow_changeset(attrs)
    |> role_changeset(attrs)
    |> token_changeset(attrs)

  end


end
