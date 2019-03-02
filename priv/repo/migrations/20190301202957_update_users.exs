defmodule Ancile.Repo.Migrations.UpdataUsers do
  use Ecto.Migration

  def change do
    alter table(:users) do
      add :token, :string, null: true

    end

  end
end
