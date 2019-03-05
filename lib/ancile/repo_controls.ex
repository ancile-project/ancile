defmodule Ancile.RepoControls do
  @moduledoc """
  The Core context.
  """

  import Ecto.Query, warn: false
  alias Ancile.Repo

  alias Ancile.Models.Policy
  alias Ancile.Models.User
  alias Ancile.Models.UserIdentity

  @doc """
  Returns the list of policies.

  ## Examples

      iex> list_policies()
      [%Policy{}, ...]

  """
  def list_policies do
    policies = Repo.all(Policy)
    Enum.map(
      policies,
      fn x ->
        %{
          x |
          policy: x.policy,
          user_id: get_email_by_id(x.user_id),
          app_id: get_email_by_id(x.app_id)
        }
      end
    )
  end

  @doc """
  Gets a single policy.

  Raises `Ecto.NoResultsError` if the Policy does not exist.

  ## Examples

      iex> get_policy!(123)
      %Policy{}

      iex> get_policy!(456)
      ** (Ecto.NoResultsError)

  """
  def get_policy!(id), do: Repo.get!(Policy, id)

  @doc """
  Creates a policy.

  ## Examples

      iex> create_policy(%{field: value})
      {:ok, %Policy{}}

      iex> create_policy(%{field: bad_value})
      {:error, %Ecto.Changeset{}}

  """
  def create_policy(attrs \\ %{}) do
    %Policy{}
    |> Policy.changeset(attrs)
    |> Repo.insert()
  end

  @doc """
  Updates a policy.

  ## Examples

      iex> update_policy(policy, %{field: new_value})
      {:ok, %Policy{}}

      iex> update_policy(policy, %{field: bad_value})
      {:error, %Ecto.Changeset{}}

  """
  def update_policy(%Policy{} = policy, attrs) do
    policy
    |> Policy.changeset(attrs)
    |> Repo.update()
  end

  @doc """
  Deletes a Policy.

  ## Examples

      iex> delete_policy(policy)
      {:ok, %Policy{}}

      iex> delete_policy(policy)
      {:error, %Ecto.Changeset{}}

  """
  def delete_policy(%Policy{} = policy) do
    Repo.delete(policy)
  end

  @doc """
  Returns an `%Ecto.Changeset{}` for tracking policy changes.

  ## Examples

      iex> change_policy(policy)
      %Ecto.Changeset{source: %Policy{}}

  """
  def change_policy(%Policy{} = policy) do
    Policy.changeset(policy, %{})
  end


  def list_policies(user_id) do
    query = from p in Policy, where: p.user_id == ^user_id
    policies = Repo.all(query)
    Enum.map(
      policies,
      fn x ->
        %{
          x |
          policy: x.policy,
          user_id: get_email_by_id(x.user_id),
          app_id: get_email_by_id(x.app_id)
        }
      end
    )
  end

  def get_by_role(role) do
    query = from u in User, where: u.role == ^role, select: u.email
    Repo.all(query)
  end

  def get_user_by_email(email) do
    query = from u in User, where: u.email == ^email, select: u.id
    res = Repo.one(query)
    case res do
      nil -> {:error, "No user registered with this email: #{inspect(email)}"}
      user -> {:ok, user}
    end
  end

  def get_email_by_id(iid) do
    query = from u in User, where: u.id == ^iid, select: u.email
    Repo.one(query)
  end

  def get_token(%User{} = app) do
    query = from u in User, where: u.id == ^app.id
    app = Repo.one(query)

    case app.api_token do
      nil ->
        api_token = Phoenix.Token.sign(AncileWeb.Endpoint, "user salt", app.id)
        User.token_changeset(app, %{"api_token" => api_token})
        |> Repo.update()
        api_token
      api_token -> api_token

    end
  end

  def get_policies(app_id, user_id, purpose) do
    query = from p in Policy,
                 where: p.user_id == ^user_id and p.app_id == ^app_id and p.purpose == ^purpose,
                 select: p.policy

    case Repo.all(query) do
      [] -> {:error, :no_policy_found}
      policies -> {:ok, policies}
    end
  end

  def get_providers(user_id) do
    query = from ui in UserIdentity,
                 where: ui.user_id == ^user_id,
                 select: [:provider, :tokens]
    case Repo.all(query) do
      [] -> {:error, "No data providers connected for user: #{inspect(get_email_by_id(user_id))}. Go to your dashboard and connect them there."}
      providers -> {:ok, providers}
    end
  end


end
