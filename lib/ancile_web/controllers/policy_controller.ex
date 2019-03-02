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
    app = conn.assigns.current_user.email
    render(conn, "new.html", changeset: changeset, users: users, app: app)
  end

  def create(
        conn,
        %{
          "policy" => %{
            "active" => active,
            "policy" =>

              policy,
            "purpose" => purpose,
            "user_id" => user_email
          }
        }
      ) do

    app_id = conn.assigns.current_user.id
    user_id = RepoControls.get_user_by_email(user_email)
    policy_binary = :erlang.term_to_binary(policy)
    object = %{app_id: app_id,
      user_id: user_id,
      policy: policy_binary, purpose: purpose, active: active
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
    policy = %{policy | policy: :erlang.binary_to_term(policy.policy),
              user_id: RepoControls.get_email_by_id(policy.user_id),
              app_id: RepoControls.get_email_by_id(policy.app_id)}
    IO.inspect(policy)

    render(conn, "show.html", policy: policy)
  end

  def edit(conn, %{"id" => id}) do
    policy = RepoControls.get_policy!(id)
    changeset = RepoControls.change_policy(policy)
    render(conn, "edit.html", policy: policy, changeset: changeset)
  end

  def update(conn, %{"id" => id, "policy" => policy_params}) do
    policy = RepoControls.get_policy!(id)

    case RepoControls.update_policy(policy, policy_params) do
      {:ok, policy} ->
        conn
        |> put_flash(:info, "Policy updated successfully.")
        |> redirect(to: Routes.policy_path(conn, :show, policy))

      {:error, %Ecto.Changeset{} = changeset} ->
        render(conn, "edit.html", policy: policy, changeset: changeset)
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
