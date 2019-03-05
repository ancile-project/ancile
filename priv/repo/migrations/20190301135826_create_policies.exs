defmodule Ancile.Repo.Migrations.CreatePolicies do
  use Ecto.Migration

  def change do
    create table(:policies) do
      add :purpose, :string, null: true, default: nil
      add :policy, :text, null: true, default: nil
      add :active, :boolean, default: false, null: false
      add :app_id, references(:users, on_delete: :nothing), null: true, default: nil
      add :user_id, references(:users, on_delete: :nothing), null: true, default: nil
      add :creator_id, references(:users, on_delete: :nothing), null: true, default: nil

      timestamps()
    end

    create index(:policies, [:app_id])
    create index(:policies, [:user_id])
  end
end
