defmodule AncileWeb.PolicyControllerTest do
  use AncileWeb.ConnCase

  alias Ancile.Core

  @create_attrs %{active: true, policy: "some policy", purpose: "some purpose"}
  @update_attrs %{active: false, policy: "some updated policy", purpose: "some updated purpose"}
  @invalid_attrs %{active: nil, policy: nil, purpose: nil}

  def fixture(:policy) do
    {:ok, policy} = Core.create_policy(@create_attrs)
    policy
  end

  describe "index" do
    test "lists all policies", %{conn: conn} do
      conn = get(conn, Routes.policy_path(conn, :index))
      assert html_response(conn, 200) =~ "Listing Policies"
    end
  end

  describe "new policy" do
    test "renders form", %{conn: conn} do
      conn = get(conn, Routes.policy_path(conn, :new))
      assert html_response(conn, 200) =~ "New Policy"
    end
  end

  describe "create policy" do
    test "redirects to show when data is valid", %{conn: conn} do
      conn = post(conn, Routes.policy_path(conn, :create), policy: @create_attrs)

      assert %{id: id} = redirected_params(conn)
      assert redirected_to(conn) == Routes.policy_path(conn, :show, id)

      conn = get(conn, Routes.policy_path(conn, :show, id))
      assert html_response(conn, 200) =~ "Show Policy"
    end

    test "renders errors when data is invalid", %{conn: conn} do
      conn = post(conn, Routes.policy_path(conn, :create), policy: @invalid_attrs)
      assert html_response(conn, 200) =~ "New Policy"
    end
  end

  describe "edit policy" do
    setup [:create_policy]

    test "renders form for editing chosen policy", %{conn: conn, policy: policy} do
      conn = get(conn, Routes.policy_path(conn, :edit, policy))
      assert html_response(conn, 200) =~ "Edit Policy"
    end
  end

  describe "update policy" do
    setup [:create_policy]

    test "redirects when data is valid", %{conn: conn, policy: policy} do
      conn = put(conn, Routes.policy_path(conn, :update, policy), policy: @update_attrs)
      assert redirected_to(conn) == Routes.policy_path(conn, :show, policy)

      conn = get(conn, Routes.policy_path(conn, :show, policy))
      assert html_response(conn, 200) =~ "some updated purpose"
    end

    test "renders errors when data is invalid", %{conn: conn, policy: policy} do
      conn = put(conn, Routes.policy_path(conn, :update, policy), policy: @invalid_attrs)
      assert html_response(conn, 200) =~ "Edit Policy"
    end
  end

  describe "delete policy" do
    setup [:create_policy]

    test "deletes chosen policy", %{conn: conn, policy: policy} do
      conn = delete(conn, Routes.policy_path(conn, :delete, policy))
      assert redirected_to(conn) == Routes.policy_path(conn, :index)
      assert_error_sent 404, fn ->
        get(conn, Routes.policy_path(conn, :show, policy))
      end
    end
  end

  defp create_policy(_) do
    policy = fixture(:policy)
    {:ok, policy: policy}
  end
end
