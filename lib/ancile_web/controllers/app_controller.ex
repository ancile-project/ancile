defmodule AncileWeb.AppController do
  use AncileWeb, :controller
  alias Ancile.RepoControls

  @doc """
  just renders a dashboard.
  """
  def app_dashboard(conn, _params) do

    render(conn, "app_dashboard.html")
  end

  @doc """
  Generates a token that is then saved in DB (I am not sure it's a good practice).
  Redirects the app developer to a page, where it's presented.
  """
  def get_token(conn, _params) do
    app = conn.assigns.current_user
    token = RepoControls.get_token(app)
    render(conn, "get_token.html", token: token)
  end
end