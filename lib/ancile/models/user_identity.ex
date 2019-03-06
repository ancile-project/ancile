defmodule Ancile.Models.UserIdentity do
  use Ecto.Schema
  use PowAssent.Ecto.UserIdentities.Schema, user: Ancile.Models.Account

  schema "user_identities" do

    pow_assent_user_identity_fields()


    timestamps()
  end
end
