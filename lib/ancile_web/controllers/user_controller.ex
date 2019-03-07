defmodule AncileWeb.UserController do
  use AncileWeb, :controller

  @doc """
  Just renders a dashboard.
  """
  def user_dashboard(conn, _params) do

    render(conn, "user_dashboard.html")
  end

end