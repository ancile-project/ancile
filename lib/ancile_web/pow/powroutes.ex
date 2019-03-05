defmodule AncileWeb.Pow.Routes do
  use Pow.Phoenix.Routes
  alias AncileWeb.Router.Helpers, as: Routes

  def after_sign_out_path(conn), do: Routes.page_path(conn, :index)
  def after_sign_in_path(conn), do: Routes.page_path(conn, :redirect_dashboard)
  def user_already_authenticated_path(conn), do: Routes.page_path(conn, :redirect_dashboard)

end
