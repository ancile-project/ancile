defmodule AncileWeb.API.Helper do
  @moduledoc false

  alias Ancile.RepoControls

  @doc """
  It tries to fetch policies for triple (app, user, purpose).
  If it fails to find it, it creates a new policy that allows everything: ANYF*,
  however it will return an error for that request with error message that
  describes creation of new policy.

  As I heard better ask for forgiveness than permission :)
  """
  def get_joined_policy(app_id, user_id, purpose) do
    case RepoControls.get_policies(app_id, user_id, purpose) do
      {:ok, policies} -> {:ok, policies}
      {:error, :no_policy_found} ->
        object = %{
          app_id: app_id,
          user_id: user_id,
          purpose: purpose,
          policy: "ANYF*",
          active: true
        }
        RepoControls.create_policy(object)
        {
          :error,
          """
          No policy for user: #{inspect(RepoControls.get_email_by_id(user_id))},
          app: #{inspect(RepoControls.get_email_by_id(app_id))}, purpose: #{inspect(purpose)}.
          We created a policy: `ANYF*` that allows everything. Please try calling your
          program again. If you want to change the policy modify it in the Dashboard.
          """
        }

    end
  end

  @doc """
  This is just to combine policies associated with the same triple.
  Better combine them more explicitly in future.
  """
  def intersect_policies([head | []]) do
    head
  end

  def intersect_policies([head | tail]) do
    "[" <> head <> "&" <> intersect_policies(tail) <> "]"
  end


end
