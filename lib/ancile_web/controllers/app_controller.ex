defmodule AncileWeb.AppController do
  use AncileWeb, :controller

  def app_dashboard(conn, _params) do
    render(conn, "app_dashboard.html")
  end

  def serve_add_page(conn, _params), do: render(conn, "add_program.html")

end