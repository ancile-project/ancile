defmodule AncileWeb.PageController do
  @moduledoc """
  Main entry for front end. Displays main page.
  """
  use AncileWeb, :controller


  def index(conn, _params) do

    render(conn, "index.html")
  end

  @doc """
  We need to redirect users based on their roles to the
  correct dashboard.
  """
  def redirect_dashboard(conn, _params) do

    case conn.assigns.current_user do
      %{role: role} -> redirect(conn, to: "/#{role}/dashboard/")
      nil -> redirect(conn, to: "/session/new")
    end

  end

end
