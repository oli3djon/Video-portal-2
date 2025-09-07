import click
from app import create_app, db
from app.models import User

app = create_app()

@click.group()
def cli():
    pass

@cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        click.echo("База данных инициализирована.")

@cli.command("create-admin")
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin(username, password):
    with app.app_context():
        if User.query.filter_by(username=username).first():
            click.echo("Такой пользователь уже существует.")
            return
        u = User(username=username)
        u.set_password(password)
        from app import db
        db.session.add(u)
        db.session.commit()
        click.echo(f"Админ '{username}' создан.")

if __name__ == "__main__":
    cli()
