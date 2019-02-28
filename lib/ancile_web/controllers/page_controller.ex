defmodule AncileWeb.PageController do
  use AncileWeb, :controller

  def index(conn, _params) do
    render(conn, "index.html")
  end

  def redirect_dashboard(conn, _params) do

    case conn.assigns.current_user do
      %{role: role} -> redirect(conn, to: "/#{role}/dashboard/")
      nil -> redirect(conn, to: "/session/new")
    end

  end

  def admin_dashboard(conn, _params) do
    render(conn, "admin_dashboard.html")
  end

  def app_dashboard(conn, _params) do
    render(conn, "app_dashboard.html")
  end

  def user_dashboard(conn, _params) do
    render(conn, "user_dashboard.html")
  end

end
