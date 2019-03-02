defmodule Ancile.CoreTest do
  use Ancile.DataCase

  alias Ancile.Core

  describe "policies" do
    alias Ancile.Core.Policy

    @valid_attrs %{active: true, policy: "some policy", purpose: "some purpose"}
    @update_attrs %{active: false, policy: "some updated policy", purpose: "some updated purpose"}
    @invalid_attrs %{active: nil, policy: nil, purpose: nil}

    def policy_fixture(attrs \\ %{}) do
      {:ok, policy} =
        attrs
        |> Enum.into(@valid_attrs)
        |> Core.create_policy()

      policy
    end

    test "list_policies/0 returns all policies" do
      policy = policy_fixture()
      assert Core.list_policies() == [policy]
    end

    test "get_policy!/1 returns the policy with given id" do
      policy = policy_fixture()
      assert Core.get_policy!(policy.id) == policy
    end

    test "create_policy/1 with valid data creates a policy" do
      assert {:ok, %Policy{} = policy} = Core.create_policy(@valid_attrs)
      assert policy.active == true
      assert policy.policy == "some policy"
      assert policy.purpose == "some purpose"
    end

    test "create_policy/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Core.create_policy(@invalid_attrs)
    end

    test "update_policy/2 with valid data updates the policy" do
      policy = policy_fixture()
      assert {:ok, %Policy{} = policy} = Core.update_policy(policy, @update_attrs)
      assert policy.active == false
      assert policy.policy == "some updated policy"
      assert policy.purpose == "some updated purpose"
    end

    test "update_policy/2 with invalid data returns error changeset" do
      policy = policy_fixture()
      assert {:error, %Ecto.Changeset{}} = Core.update_policy(policy, @invalid_attrs)
      assert policy == Core.get_policy!(policy.id)
    end

    test "delete_policy/1 deletes the policy" do
      policy = policy_fixture()
      assert {:ok, %Policy{}} = Core.delete_policy(policy)
      assert_raise Ecto.NoResultsError, fn -> Core.get_policy!(policy.id) end
    end

    test "change_policy/1 returns a policy changeset" do
      policy = policy_fixture()
      assert %Ecto.Changeset{} = Core.change_policy(policy)
    end
  end
end
