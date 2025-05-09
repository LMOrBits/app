from pathlib import Path
import click
from .groups import cli
from .schemas import Project, ML, Observability, Config
from dotenv import load_dotenv

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
def install():
    from dotenv import load_dotenv
    import os
    """Install the project dependencies."""
    click.echo("Installing project dependencies...")
    config,config_dir = read_config()
    env_path = config_dir.parent / "appdeps.env"
    load_dotenv(env_path, override=True)
    # project = Project(**config["project"])
    if "ml" in config:
        ml = ML(**config["ml"])
        if ml.provider == "local" and ml.type == "llm":
            from pyapp.model_connection.lm.langchain.litellm import get_model_mlflow_llamacpp, ModelConfig
            model_config = ModelConfig(
                model_name=ml.serve.model_name,
                alias=ml.serve.alias,
                port=ml.serve.port,
                gguf_relative_path=ml.serve.gguf_relative_path
            )
            litellm_config = ml.litellm.model_dump()
            model = get_model_mlflow_llamacpp(ml.serve.model_dir,model_config,stream=True,**litellm_config)
    
    if "observability" in config:
        from pyapp.observation.phoneix import observation
        observation.start()
    
        

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
    
    from pyapp.model_connection.lm.langchain.litellm import get_model_manager_from_config
    config,config_dir = read_config()
    env_path = config_dir.parent / "appdeps.env"
    load_dotenv(env_path, override=True)
    conf = Config(**config)
    if "ml" in config:
        ml = ML(**config["ml"])
        if ml.provider == "local" and ml.type == "llm":
            model_manager = get_model_manager_from_config(conf.ml.serve.model_dir)
            print(model_manager.model_config_manager.list_models())
            model_manager.stop_serve_model(ml.serve.model_name)


@cli.command()
def remove():
    from pyapp.observation.instance import PhoenixObservation
    observation = PhoenixObservation()
    """Stop the project."""
    observation.remove()
    
    from pyapp.model_connection.lm.langchain.litellm import get_model_manager_from_config
    config,config_dir = read_config()
    env_path = config_dir.parent / "appdeps.env"
    load_dotenv(env_path, override=True)
    conf = Config(**config)
    if "ml" in config:
        ml = ML(**config["ml"])
        if ml.provider == "local" and ml.type == "llm":
            model_manager = get_model_manager_from_config(conf.ml.serve.model_dir)
            model_manager.delete_all_serve_models()





def main():
    cli()