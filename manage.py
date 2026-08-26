from app import create_app, db

app = create_app()


@app.cli.command("seed")
def seed():
    """Create initial branch, roles, permissions and admin user."""
    from app.seed import seed_database
    seed_database()


if __name__ == "__main__":
    app.run(debug=True)
