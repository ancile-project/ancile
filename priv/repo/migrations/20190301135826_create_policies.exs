defmodule Ancile.Repo.Migrations.CreatePolicies do
  use Ecto.Migration

  def change do
    create table(:policies) do
      add :purpose, :string
      add :policy, :binary
      add :active, :boolean, default: false, null: false
      add :app_id, references(:users, on_delete: :nothing)
      add :user_id, references(:users, on_delete: :nothing)

      timestamps()
    end

    create index(:policies, [:app_id])
    create index(:policies, [:user_id])
  end
end
