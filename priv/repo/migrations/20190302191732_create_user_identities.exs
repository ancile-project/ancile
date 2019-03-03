defmodule Ancile.Repo.Migrations.CreateUserIdentities do
  use Ecto.Migration

  def change do
    create table(:user_identities) do
      add :provider, :string, null: false
      add :uid, :string, null: false
      add :token, :text, null: true, default: nil
      add :scope, :string, null: true, default: nil
      add :data, :map, null: true, default: nil

      add :user_id, references("users"), on_delete: :nothing

      timestamps(updated_at: false)
    end


    create unique_index(:user_identities, [:uid, :provider])
  end
end
