defmodule AncileWeb.Router do
  use AncileWeb, :router
  use Pow.Phoenix.Router


  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_flash
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  pipeline :admin_protected do
    plug AncileWeb.EnsureRolePlug, :admin
    plug Pow.Plug.RequireAuthenticated,
         error_handler: Pow.Phoenix.PlugErrorHandler
  end

  pipeline :app_protected do
    plug AncileWeb.EnsureRolePlug, :app
    plug Pow.Plug.RequireAuthenticated,
         error_handler: Pow.Phoenix.PlugErrorHandler
  end

  pipeline :user_protected do
    plug AncileWeb.EnsureRolePlug, :user
    plug Pow.Plug.RequireAuthenticated,
         error_handler: Pow.Phoenix.PlugErrorHandler
  end


  scope "/" do
    pipe_through :browser

    pow_routes()
  end

  scope "/", AncileWeb do
    pipe_through :browser

    get "/", PageController, :index
    get "/dashboard", PageController, :redirect_dashboard
  end


  scope "/admin", AncileWeb do
    pipe_through [:browser, :admin_protected]

    get "/dashboard", AdminController, :admin_dashboard
  end

  scope "/app", AncileWeb do
    pipe_through [:browser, :app_protected]

    get "/dashboard", AppController, :app_dashboard
    get "/program_add", AppController, :serve_add_page
  end

    scope "/user", AncileWeb do
    pipe_through [:browser, :user_protected]

    get "/dashboard", UserController, :user_dashboard
  end

  # Other scopes may use custom stacks.
  # scope "/api", AncileWeb do
  #   pipe_through :api
  # end
end
