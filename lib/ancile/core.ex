defmodule Ancile.Core do
  @moduledoc """
  The Core context.
  """

  import Ecto.Query, warn: false
  alias Ancile.Repo

  alias Ancile.Core.Policy
  alias Ancile.Users.User

  @doc """
  Returns the list of policies.

  ## Examples

      iex> list_policies()
      [%Policy{}, ...]

  """
  def list_policies do
    policies = Repo.all(Policy)
    Enum.map(policies, fn x -> %{x |  policy: :erlang.binary_to_term(x.policy),
              user_id: get_email_by_id(x.user_id),
              app_id: get_email_by_id(x.app_id)} end)
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

  def get_by_role(role) do
    query = from u in User, where: u.role == ^role, select: u.email
    Repo.all(query)
  end

  def get_user_by_email(email) do
    query = from u in User, where: u.email == ^email, select: u.id
    Repo.one(query)
  end

  def get_email_by_id(iid) do
    query = from u in User, where: u.id == ^iid, select: u.email
    Repo.one(query)
  end
end
