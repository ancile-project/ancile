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

end
