defmodule Ancile.Models.UserIdentity do
  use Ecto.Schema
  use PowAssent.Ecto.UserIdentities.Schema, user: Ancile.Models.User

  schema "user_identities" do

#    field :token, :string
#    field :scope, :string
#    field :data, :map

    pow_assent_user_identity_fields()


    timestamps(updated_at: false)
  end
end
