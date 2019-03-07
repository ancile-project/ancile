defmodule AncileWeb.AdminController do
  use AncileWeb, :controller

  @doc """
  just renders a dashboard.
  """
  def admin_dashboard(conn, _params) do
    render(conn, "admin_dashboard.html")
  end

end