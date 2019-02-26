defmodule AncileWeb.PageController do
  use AncileWeb, :controller

  def index(conn, _params) do
    render(conn, "index.html")
  end
end
