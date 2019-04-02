defmodule AncileWeb.Router do
  @moduledoc """
  Our routing file that controls access and resources.
  Each of the roles (Admin, User, App) will get separate dashboards.
  """

  use AncileWeb, :router
  use Pow.Phoenix.Router
  use PowAssent.Phoenix.Router



  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_flash
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  @doc """
  We should make it lightweight, so our API requests get processed faster.
  """
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
    resources "/policies", PolicyController
  end

  scope "/user" do
    pipe_through [:browser, :user_protected]

    pow_assent_routes()
  end

  scope "/app", AncileWeb do
    pipe_through [:browser, :app_protected]

    get "/dashboard", AppController, :app_dashboard
    get "/token", AppController, :get_token

  end

  scope "/user", AncileWeb do
    pipe_through [:browser, :user_protected]

    get "/dashboard", UserController, :user_dashboard
    resources "/policies", User.PolicyController, as: :user_policy
    resources "/identities", User.IdentityController, as: :user_identity
  end

  @doc """
  API endpoint to process data.
  """
  scope "/api", AncileWeb.API do
    pipe_through :api

    get "/", RunController, :api_test
    post "/run", RunController, :run_program
  end
end
