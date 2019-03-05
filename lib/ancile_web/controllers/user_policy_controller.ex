defmodule AncileWeb.User.PolicyController do
  use AncileWeb, :controller

  alias Ancile.RepoControls
  alias Ancile.Models.Policy

  def index(conn, _params) do
    policies = RepoControls.list_policies(conn.assigns.current_user.id)
    render(conn, "index.html", policies: policies)
  end

  def new(conn, _params) do
    changeset = RepoControls.change_policy(%Policy{})
    apps = RepoControls.get_by_role("app")

    render(conn, "new.html", changeset: changeset, apps: apps)
  end

  def create(
        conn,
        %{
          "policy" => %{
            "active" => active,
            "policy" => policy,
            "purpose" => purpose,
            "app_id" => app_email
          }
        }
      ) do

    {:ok, app_id} = RepoControls.get_user_by_email(app_email)
    object = %{
      app_id: app_id,
      user_id: conn.assigns.current_user.id,
      policy: policy,
      purpose: purpose,
      active: active
    }
    case RepoControls.create_policy(object) do
      {:ok, policy} ->
        conn
        |> put_flash(:info, "Policy created successfully.")
        |> redirect(to: Routes.user_policy_path(conn, :show, policy))

      {:error, %Ecto.Changeset{} = changeset} ->
        render(conn, "new.html", changeset: changeset)
    end
  end

  def show(conn, %{"id" => id}) do
    policy = RepoControls.get_policy!(id)
    policy = %{
      policy |
      policy: policy.policy,
      user_id: conn.assigns.current_user.email,
      app_id: RepoControls.get_email_by_id(policy.app_id)
    }
    IO.inspect(policy)

    render(conn, "show.html", policy: policy)
  end

  def edit(conn, %{"id" => id}) do
    policy = RepoControls.get_policy!(id)
    changeset = RepoControls.change_policy(policy)
    apps = RepoControls.get_by_role("app")
    render(conn, "edit.html", policy: policy, changeset: changeset, apps: apps)
  end

  def update(
        conn,
        %{
          "id" => id,
          "policy" => %{
            "active" => active,
            "policy" => policy_text,
            "purpose" => purpose,
            "app_id" => app_email
          }
        }
      ) do
    policy = RepoControls.get_policy!(id)
    {:ok, app_id} = RepoControls.get_user_by_email(app_email)
    user_id = conn.assigns.current_user.id
    object = %{
      app_id: app_id,
      user_id: user_id,
      policy: policy_text,
      purpose: purpose,
      active: active
    }

    case RepoControls.update_policy(policy, object) do
      {:ok, policy} ->
        conn
        |> put_flash(:info, "Policy updated successfully.")
        |> redirect(to: Routes.user_policy_path(conn, :show, policy))

      {:error, %Ecto.Changeset{} = changeset} ->
        apps = RepoControls.get_by_role("app")
        render(conn, "edit.html", policy: policy, changeset: changeset, apps: apps)
    end
  end

  def delete(conn, %{"id" => id}) do
    policy = RepoControls.get_policy!(id)
    {:ok, _policy} = RepoControls.delete_policy(policy)

    conn
    |> put_flash(:info, "Policy deleted successfully.")
    |> redirect(to: Routes.user_policy_path(conn, :index))
  end
end
