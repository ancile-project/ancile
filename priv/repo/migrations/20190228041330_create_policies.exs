defmodule Ancile.Repo.Migrations.CreatePolicies do
  use Ecto.Migration

  def change do
    create table(:policies) do
      add :app_id, :integer, null: true
      add :user_id, :integer, null: true
      add :purpose, :string, null: true
      add :policy, :binary, null: true
      add :active, :boolean, default: true

      timestamps()
    end

    create index(:policies, [:app_id])
    create index(:policies, [:user_id])
    create index(:policies, [:app_id, :user_id, :purpose])
  end
end
