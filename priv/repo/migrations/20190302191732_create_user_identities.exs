defmodule Ancile.Repo.Migrations.CreateUserIdentities do
  use Ecto.Migration

  def change do
    create table(:user_identities) do
      add :provider, :string, null: false
      add :uid, :string, null: false
      add :token, :string, null: true
      add :scope, :string, null: true
      add :data, :map

      add :user_id, references("users"), on_delete: :nothing

      timestamps(updated_at: false)
    end

    create unique_index(:user_identities, [:uid, :provider])
  end
end
