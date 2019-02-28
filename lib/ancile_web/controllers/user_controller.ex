defmodule AncileWeb.UserController do
  use AncileWeb, :controller

  def user_dashboard(conn, _params) do
    render(conn, "user_dashboard.html")
  end

end