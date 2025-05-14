from pathlib import Path
import click
from pyapp.main import Pyapp
from .groups import cli
from pyapp.cli.schemas import PyappDependency, ML, Observability
from pyapp.cli.utils import read_config,write_config
import toml




pyapp_instance = Pyapp()

@cli.command()
@click.option('--name', prompt='Project name', help='Name of the project')
@click.option('--version', prompt='Project version', help='Version of the project', default='0.0.1')
@click.option('--description', prompt='Project description', help='Description of the project', default='')
@click.option('--author', prompt='Project author', help='Author of the project', default='')
def init(name: str, version: str, description: str, author: str):
    """🚀 Initialize a new SLMOPS project with the specified configuration."""
    pyapp_instance.init(name, version, description, author)

@cli.command()
def run():
    """▶️ Run all project dependencies including observability, models, data, serve, and subprojects."""
    pyapp_instance.run()
    
    

@cli.command()
@click.option('--latest', prompt='Latest Version update', help='Latest Version update', default=True)
def run_latest(latest:bool):
    """🔄 Run the project with the latest available model version."""
    pyapp_instance.run_latest(latest)
        
@cli.command()
def add_observe():
    """🔄 Run the project with the latest available model version."""
    click.echo("Adding a new observability to the project...")
    config,config_dir = read_config()
    observability = Observability()
    config["observability"] = observability.model_dump()
    write_config(config,config_dir)
    

@cli.command()
def stop():
    """⏹️ Stop all running components including observability and serve services."""
    pyapp_instance.stop()


@cli.command()
def remove():
    """🗑️ Remove all running or previously running components including observability and serve services."""
    pyapp_instance.remove()

@cli.command()
@click.option('--raw-data', prompt='Raw data (y/n)', help='Raw data', default="n", type=str)
def push_data(raw_data:str):
    """🔺 Ingest data (raw data or vector database) into the vector store."""
    raw_data = raw_data.lower() == "y"
    pyapp_instance.ingest_to_vectordb(raw_data=raw_data)

@cli.command()
@click.option('--use-commit-hash', prompt='Use commit hash if any (y/n)', help='Use commit hash', default="n", type=str)
@click.option('--force', prompt='Force to override if exists (y/n)', help='Force', default="n", type=str)
def pull_test_data(use_commit_hash:str, force:str):
    """🔻 Download test data from the data repository with optional commit hash and force override."""
    use_commit_hash = use_commit_hash.lower() == "y"
    force = force.lower() == "y"
    pyapp_instance.get_test_data(use_commit_hash=use_commit_hash,force=force)

@cli.command()
def push_test_data():
    """🔺 Ingest test data into the data repository."""
    pyapp_instance.ingest_test_data()

@cli.command()
@click.option('--use-commit-hash', prompt='Use commit hash if any (y/n)', help='Use commit hash', default="n", type=str)
@click.option('--force', prompt='Force to override if exists (y/n)', help='Force', default="n", type=str)
@click.option('--raw-data', prompt='Raw data (y/n)', help='Raw data', default="n", type=str)
def pull_data(use_commit_hash:str, force:str, raw_data:str):
    """🔻 Download data (raw data or vector database) from the data repository with optional commit hash and force override."""
    use_commit_hash = use_commit_hash.lower() == "y"
    force = force.lower() == "y"
    raw_data = raw_data.lower() == "y"
    pyapp_instance.download_from_vetordb(use_commit_hash=use_commit_hash,force=force,raw_data=raw_data)


@cli.command()
@click.option('--name', prompt='Dependency name', help='Name of the dependency', default="simple")
@click.option("--directory", prompt="Dependency directory", help="Directory of the dependency", default="./test")
def add_dep(name:str, directory:str):
    """🎸 Add another project as a dependency with specified name and directory."""
    path_directory = Path(directory).resolve()
    if Path(directory).is_dir():
        if (path_directory / "appdeps.toml").exists():
            with open(path_directory / "appdeps.toml", "r") as f:
                dep_config = toml.load(f)
                if "ml" in dep_config:
                    ml = ML(**dep_config["ml"])
                else: 
                    return
                ml = ML(**dep_config["ml"])
            assert dep_config["project"]["name"] == name, 'Dependency name does not match'
            config,config_dir = pyapp_instance.read_config()
            if config.get("project",{}).get("dependencies",None):
                deps = config["project"]["dependencies"]
            else:
                deps = {}
            if name not in deps:
                deps[name] = PyappDependency(name=name, directory=str(directory)).model_dump()
                config["project"]["dependencies"] = deps
                with open(config_dir, "w") as f:
                    toml.dump(config, f)
            else:
                click.echo(f"Dependency {name} already exists")
        else:
            click.echo(f"appdeps.toml does not exist in {directory}")
    else:
        click.echo(f"Directory {directory} does not exist")


def main():
    cli()