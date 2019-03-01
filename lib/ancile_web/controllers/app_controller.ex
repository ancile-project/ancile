defmodule AncileWeb.AppController do
  use AncileWeb, :controller

  def app_dashboard(conn, _params) do
    conn
    |> put_flash(:info, "Welcome to Phoenix, from flash info!")
    |> put_flash(:error, "Let's pretend we have an error.")
    |> render("app_dashboard.html")
  end

  def serve_add_page(conn, _params), do: render(conn, "add_program.html")

end