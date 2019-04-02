defmodule AncileWeb.User.IdentityController do
  @moduledoc false

  use AncileWeb, :controller


  alias Ancile.RepoControls

  def index(conn, _params) do
    user_identities = RepoControls.list_user_identities(conn.assigns.current_user.id)
    render(conn, "index.html", user_identities: user_identities)
  end


  def show(conn, %{"id" => id}) do
    user_identity = RepoControls.get_user_identity!(id)
    user_identity = %{
      user_identity |
      data: Jason.encode!(user_identity.data)
    }
    IO.inspect(user_identity)

    render(conn, "show.html", user_identity: user_identity)
  end

  def edit(conn, %{"id" => id}) do
    user_identity = RepoControls.get_user_identity!(id)

    user_identity = %{
      user_identity |
      data: Jason.encode!(user_identity.data)
    }
    changeset = RepoControls.change_user_identity(user_identity)
#    changeset = %{
#      changeset |
#      data: ""
#    }
    render(conn, "edit.html", user_identity: user_identity, changeset: changeset)
  end

  def update(
        conn,
        %{
          "id" => id,
          "user_identity" => %{
            "data" => data
          }
        }
      ) do
    user_identity = RepoControls.get_user_identity!(id)
    object = %{
      data: Jason.decode!(data)
    }

    case RepoControls.update_user_identity(user_identity, object) do
      {:ok, user_identity} ->
        user_identity = %{
          user_identity |
          data: Jason.encode!(user_identity.data)
        }
        conn
        |> put_flash(:info, "User Identity updated successfully.")
        |> redirect(to: Routes.user_identity_path(conn, :show, user_identity))

      {:error, %Ecto.Changeset{} = changeset} ->
        user_identity = %{
          user_identity |
          data: Jason.encode!(user_identity.data)
        }
        render(
          conn,
          "edit.html",
          user_identity: user_identity,
          changeset: changeset
        )
    end
  end

end
