from pathlib import Path
import click
from .groups import cli
from .schemas import Project, ML, Observability, Config, Embeddings
from dotenv import load_dotenv
from pyapp.serve_integration import get_mlflow_embeddings_manager, get_mlflow_lm_manager

from .add_ml import add_ml
from .utils import read_config,write_config

@cli.command()
@click.option('--name', prompt='Project name', help='Name of the project')
@click.option('--version', prompt='Project version', help='Version of the project', default='0.0.1')
@click.option('--description', prompt='Project description', help='Description of the project', default='')
@click.option('--author', prompt='Project author', help='Author of the project', default='')
def init(name: str, version: str, description: str, author: str):
    """Initialize a new SLMOPS project."""
    config,config_dir = read_config(give_error=False)
    if config:
        click.echo("Appdeps.toml already exists")
        return
    project = Project(name=name, version=version, description=description, author=author)
    config["project"] = project.model_dump()
    write_config(config,config_dir)
    Path(config_dir.parent / "appdeps.env").touch(exist_ok=True)

@cli.command()
def run():
    """Install the project dependencies."""
    click.echo("Installing project dependencies...")
    config,config_dir = read_config()
    env_path = config_dir.parent / "appdeps.env"
    load_dotenv(env_path, override=True)
    # project = Project(**config["project"])
    if "observability" in config:
        from pyapp.observation.phoneix import observation
        observation.start()

    if "ml" in config:
        ml = ML(**config["ml"])
        manager = None
        status = None
        if ml.type == "llm":
            manager = get_mlflow_lm_manager(ml.model_dir)
            model = ml.serve
            port = ml.serve.port
        if ml.type == "embeddings":
            print(ml.model_dir)
            manager = get_mlflow_embeddings_manager(ml.model_dir)
            model = ml.embeddings
        status = manager.new_model_status(model.model_name,model.alias)
        if status: 
            click.echo(f"new version of the model `{model.model_name}` with alias `{model.alias}` is available. would you like to update to the latest version?")
            cli(["run-latest"], standalone_mode=False)
        elif manager is not None:
            if ml.type == "llm":
                manager.add_serve(model_name=model.model_name, alias=model.alias, port=port)
            if ml.type == "embeddings":
                manager.add_serve(model_name=model.model_name, alias=model.alias)
    
    

@cli.command()
@click.option('--latest', prompt='Latest Version update', help='Latest Version update', default=True)
def run_latest(latest:bool):
    """Install the project dependencies."""
    click.echo("Installing project dependencies...")
    config,config_dir = read_config()
    env_path = config_dir.parent / "appdeps.env"
    load_dotenv(env_path, override=True)
    manager = None
    if "ml" in config:
        ml = ML(**config["ml"])
        if ml.type == "llm":
            manager = get_mlflow_lm_manager(ml.model_dir)
            model = ml.serve
            port = ml.serve.port
        if ml.type == "embeddings":
            manager = get_mlflow_embeddings_manager(ml.model_dir)
            model = ml.embeddings
        if manager is not None:
            if ml.type == "llm":
                manager.update_model(model_name=model.model_name, alias=model.alias, port=port)
            if ml.type == "embeddings":
                manager.update_model(model_name=model.model_name, alias=model.alias)
        
@cli.command()
def add_observe():
    """Add a new observability to the project."""
    click.echo("Adding a new observability to the project...")
    config,config_dir = read_config()
    observability = Observability()
    config["observability"] = observability.model_dump()
    write_config(config,config_dir)

@cli.command()
def stop():
    """Stop the project."""
    from pyapp.observation.instance import PhoenixObservation
    observation = PhoenixObservation()
    """Stop the project."""
    observation.stop()
    
    from pyapp.model_connection.lm.langchain.litellm import get_lm_model_manager
    config,config_dir = read_config()
    env_path = config_dir.parent / "appdeps.env"
    load_dotenv(env_path, override=True)
    conf = Config(**config)
    if "ml" in config:
        ml = ML(**config["ml"])
        if ml.provider == "local" and ml.type == "llm":
            manager = get_mlflow_lm_manager(ml.model_dir)
            manager.stop_all_serve()
        if ml.provider == "local" and ml.type == "embeddings":
            manager = get_mlflow_embeddings_manager(ml.model_dir)
            manager.stop_all_serve()


@cli.command()
def remove():
    from pyapp.observation.instance import PhoenixObservation
    observation = PhoenixObservation()
    """Stop the project."""
    observation.remove()
    
    
    config,config_dir = read_config()
    env_path = config_dir.parent / "appdeps.env"
    load_dotenv(env_path, override=True)
    conf = Config(**config)
    if "ml" in config:
        ml = ML(**config["ml"])
        if ml.provider == "local" and ml.type == "llm":
            manager = get_mlflow_lm_manager(ml.model_dir)
            manager.delete_all_serve()
        if ml.provider == "local" and ml.type == "embeddings":
            manager = get_mlflow_embeddings_manager(ml.model_dir)
            manager.delete_all_serve()

# @cli.command()
# @click.option('--name', prompt='Dependency name', help='Name of the dependency')
# @click.option("--directory", prompt="Dependency directory", help="Directory of the dependency")
# def add_dep(name:str, directory:str):
#     directory = Path(directory)
#     if Path(directory).is_dir():
#         click.echo(f"Dependency {name} already exists")
#         if (directory / "appdeps.toml").exists():
#             click.echo(f"Dependency {name} already exists")
#             return

       



def main():
    cli()