defmodule AncileWeb.AppController do
  use AncileWeb, :controller
  alias Ancile.RepoControls

  def app_dashboard(conn, _params) do

    render(conn, "app_dashboard.html")
  end

  def serve_add_page(conn, _params), do: render(conn, "add_program.html")

  def get_token(conn, _params) do
    app = conn.assigns.current_user
    token = RepoControls.get_token(app)
    render(conn, "get_token.html", token: token)
  end
end