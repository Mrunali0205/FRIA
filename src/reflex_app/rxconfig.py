import reflex as rx

config = rx.Config(
    app_name="main",
    frontend_port=3000,
    backend_port=3001,
    api_url="http://localhost:3001",
    deploy_url="http://localhost:3000",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
