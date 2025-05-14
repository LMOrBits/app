from pathlib import Path
import click
from pyapp.main import Pyapp
from .groups import cli
from pyapp.cli.schemas import PyappDependency, ML
import toml




pyapp_instance = Pyapp()

@cli.command()
@click.option('--name', prompt='Project name', help='Name of the project')
@click.option('--version', prompt='Project version', help='Version of the project', default='0.0.1')
@click.option('--description', prompt='Project description', help='Description of the project', default='')
@click.option('--author', prompt='Project author', help='Author of the project', default='')
def init(name: str, version: str, description: str, author: str):
    """Initialize a new SLMOPS project."""
    pyapp_instance.init(name, version, description, author)

@cli.command()
def run():
    """Install the project dependencies."""
    pyapp_instance.run()
    
    

@cli.command()
@click.option('--latest', prompt='Latest Version update', help='Latest Version update', default=True)
def run_latest(latest:bool):
    """Install the project dependencies."""
    pyapp_instance.run_latest(latest)
        
@cli.command()
def add_observe():
    """Add a new observability to the project."""
    pyapp_instance.add_observe()
    

@cli.command()
def stop():
    """Stop the project."""
    pyapp_instance.stop()


@cli.command()
def remove():
    """Remove the project."""
    pyapp_instance.remove()

@cli.command()
@click.option('--raw-data', prompt='Raw data (y/n)', help='Raw data', default="n", type=str)
def push_data(raw_data:str):
    """Ingest the data to the vector store."""
    raw_data = raw_data.lower() == "y"
    pyapp_instance.ingest_to_vectordb(raw_data=raw_data)

@cli.command()
@click.option('--use-commit-hash', prompt='Use commit hash if any (y/n)', help='Use commit hash', default="n", type=str)
@click.option('--force', prompt='Force to override if exists (y/n)', help='Force', default="n", type=str)
@click.option('--raw-data', prompt='Raw data (y/n)', help='Raw data', default="n", type=str)
def pull_data(use_commit_hash:str, force:str, raw_data:str):
    """Download the data from the vector store."""
    use_commit_hash = use_commit_hash.lower() == "y"
    force = force.lower() == "y"
    raw_data = raw_data.lower() == "y"
    pyapp_instance.download_from_vetordb(use_commit_hash=use_commit_hash,force=force,raw_data=raw_data)


@cli.command()
@click.option('--name', prompt='Dependency name', help='Name of the dependency', default="simple")
@click.option("--directory", prompt="Dependency directory", help="Directory of the dependency", default="./test")
def add_dep(name:str, directory:str):
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