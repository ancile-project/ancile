defmodule Ancile.Repo.Migrations.CreateAccounts do
  use Ecto.Migration

  def change do
    create table(:accounts) do
      add :email, :string, null: false
      add :password_hash, :string
      add :role, :string
      add :api_token, :string, null: true

      timestamps()
    end

    create unique_index(:accounts, [:email])
  end
end
