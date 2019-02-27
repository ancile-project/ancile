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

  pipeline :protected do
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
  end

  scope "/dashboard", AncileWeb do
    pipe_through [:browser, :protected]

    get "/", PageController, :dashboard
  end

  # Other scopes may use custom stacks.
  # scope "/api", AncileWeb do
  #   pipe_through :api
  # end
end
