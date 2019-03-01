defmodule AncileWeb.PolicyController do
  use AncileWeb, :controller

  alias Ancile.Core
  alias Ancile.Core.Policy

  def index(conn, _params) do
    policies = Core.list_policies()
    render(conn, "index.html", policies: policies)
  end

  def new(conn, _params) do
    changeset = Core.change_policy(%Policy{})
    users = Core.get_by_role("user")
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
    user_id = Core.get_user_by_email(user_email)
    policy_binary = :erlang.term_to_binary(policy)
    object = %{app_id: app_id,
      user_id: user_id,
      policy: policy_binary, purpose: purpose, active: active
            }
    case Core.create_policy(object) do
      {:ok, policy} ->
        conn
        |> put_flash(:info, "Policy created successfully.")
        |> redirect(to: Routes.policy_path(conn, :show, policy))

      {:error, %Ecto.Changeset{} = changeset} ->
        render(conn, "new.html", changeset: changeset)
    end
  end

  def show(conn, %{"id" => id}) do
    policy = Core.get_policy!(id)
    policy = %{policy | policy: :erlang.binary_to_term(policy.policy),
              user_id: Core.get_email_by_id(policy.user_id),
              app_id: Core.get_email_by_id(policy.app_id)}
    IO.inspect(policy)

    render(conn, "show.html", policy: policy)
  end

  def edit(conn, %{"id" => id}) do
    policy = Core.get_policy!(id)
    changeset = Core.change_policy(policy)
    render(conn, "edit.html", policy: policy, changeset: changeset)
  end

  def update(conn, %{"id" => id, "policy" => policy_params}) do
    policy = Core.get_policy!(id)

    case Core.update_policy(policy, policy_params) do
      {:ok, policy} ->
        conn
        |> put_flash(:info, "Policy updated successfully.")
        |> redirect(to: Routes.policy_path(conn, :show, policy))

      {:error, %Ecto.Changeset{} = changeset} ->
        render(conn, "edit.html", policy: policy, changeset: changeset)
    end
  end

  def delete(conn, %{"id" => id}) do
    policy = Core.get_policy!(id)
    {:ok, _policy} = Core.delete_policy(policy)

    conn
    |> put_flash(:info, "Policy deleted successfully.")
    |> redirect(to: Routes.policy_path(conn, :index))
  end
end
