defmodule AncileWeb.PolicyController do
  use AncileWeb, :controller

  alias Ancile.RepoControls
  alias Ancile.Models.Policy

  def index(conn, _params) do
    policies = RepoControls.list_policies()
    render(conn, "index.html", policies: policies)
  end

  def new(conn, _params) do
    changeset = RepoControls.change_policy(%Policy{})
    users = RepoControls.get_by_role("user")
    apps = RepoControls.get_by_role("app")
    render(conn, "new.html", changeset: changeset, users: users, apps: apps)
  end

  def create(
        conn,
        %{
          "policy" => %{
            "active" => active,
            "policy" => policy,
            "purpose" => purpose,
            "user_id" => user_email,
            "app_id" => app_email
          }
        }
      ) do

    app_id = RepoControls.get_user_by_email(app_email)
    user_id = RepoControls.get_user_by_email(user_email)
    object = %{
      app_id: app_id,
      user_id: user_id,
      policy: policy,
      purpose: purpose,
      active: active
    }
    case RepoControls.create_policy(object) do
      {:ok, policy} ->
        conn
        |> put_flash(:info, "Policy created successfully.")
        |> redirect(to: Routes.policy_path(conn, :show, policy))

      {:error, %Ecto.Changeset{} = changeset} ->
        render(conn, "new.html", changeset: changeset)
    end
  end

  def show(conn, %{"id" => id}) do
    policy = RepoControls.get_policy!(id)
    policy = %{
      policy |
      policy: policy.policy,
      user_id: RepoControls.get_email_by_id(policy.user_id),
      app_id: RepoControls.get_email_by_id(policy.app_id)
    }
    IO.inspect(policy)

    render(conn, "show.html", policy: policy)
  end

  def edit(conn, %{"id" => id}) do
    policy = RepoControls.get_policy!(id)
    changeset = RepoControls.change_policy(policy)
    users = RepoControls.get_by_role("user")
    apps = RepoControls.get_by_role("app")
    render(conn, "edit.html", policy: policy, changeset: changeset, users: users, apps: apps)
  end

  def update(
        conn,
        %{
          "id" => id,
          "policy" => %{
            "active" => active,
            "policy" => policy_text,
            "purpose" => purpose,
            "user_id" => user_email,
            "app_id" => app_email
          }
        }
      ) do
    policy = RepoControls.get_policy!(id)
    app_id = RepoControls.get_user_by_email(app_email)
    user_id = RepoControls.get_user_by_email(user_email)
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
        |> redirect(to: Routes.policy_path(conn, :show, policy))

      {:error, %Ecto.Changeset{} = changeset} ->
        users = RepoControls.get_by_role("user")
        apps = RepoControls.get_by_role("app")
        render(conn, "edit.html", policy: policy, changeset: changeset, users: users, apps: apps)
    end
  end

  def delete(conn, %{"id" => id}) do
    policy = RepoControls.get_policy!(id)
    {:ok, _policy} = RepoControls.delete_policy(policy)

    conn
    |> put_flash(:info, "Policy deleted successfully.")
    |> redirect(to: Routes.policy_path(conn, :index))
  end
end
