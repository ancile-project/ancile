defmodule Ancile.Models.Account do
  use Ecto.Schema
  use Pow.Ecto.Schema
  import Ecto.Changeset

  schema "accounts" do

    has_many :user_identities,
             Ancile.Models.UserIdentity,
             on_delete: :delete_all,
             foreign_key: :user_id

    field :role, :string, default: "user"
    field :api_token, :string, default: nil

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
    |> cast(attrs, [:api_token])
  end

  def changeset(user_or_changeset, attrs) do
    user_or_changeset
    |> pow_changeset(attrs)
    |> role_changeset(attrs)
    |> token_changeset(attrs)

  end


end
