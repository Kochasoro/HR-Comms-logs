import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User

@click.command("seed")
@click.option("--force", is_flag=True, help="Force reseed (delete existing users)")
@with_appcontext
def seed_command(force):
    """Seed the database with default users."""

    if force:
        User.query.delete()
        db.session.commit()
        click.echo("⚠️ Existing users deleted.")

    elif User.query.first():
        click.echo("Users already exist. Use --force to reseed.")
        return

    users = [
        User(username="Superadmin", password_hash=generate_password_hash("OJTAccess"), role="admin"),
        User(username="Admin", password_hash=generate_password_hash("Password"), role="admin"),
        User(username="secretary", password_hash=generate_password_hash("secret123"), role="secretary"),
    ]

    db.session.add_all(users)
    db.session.commit()

    click.echo("✅ Database seeded!")