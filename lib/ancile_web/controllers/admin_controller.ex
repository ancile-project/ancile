defmodule AncileWeb.AdminController do
  use AncileWeb, :controller

  def admin_dashboard(conn, _params) do
    render(conn, "admin_dashboard.html")
  end

end