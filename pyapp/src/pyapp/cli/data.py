from .groups import cli
import click
from .schemas import VectorDB
from .utils import read_config, write_config
from pathlib import Path
@cli.group()
def data():
    pass

@cli.command()
@click.option("--name", type=str,prompt="Name of the vector store", help="Name of the vector store")
@click.option("--in-repo-path", type=str, prompt="Path to the vector store in the repository" , default="./data/vectordb")
@click.option("--branch-name", type=str, prompt="Name of the branch", default="main")
@click.option("--source-branch", type=str, prompt="Source branch", default="main")
def add_vectordb(name, in_repo_path, branch_name, source_branch):
    """Add a vector store to the project"""
    vector_db = VectorDB(name=name, inRepoPath=in_repo_path, branchName=branch_name, sourceBranch=source_branch)
    config,config_dir = read_config()
    config_dir_path = Path(config_dir.parent)
    in_repo_path = Path(in_repo_path)
    (config_dir_path/in_repo_path).mkdir(parents=True, exist_ok=True)
    config["vectordb"] = vector_db.model_dump()
    write_config(config,config_dir)

@data.command()
@click.option("--branch-name", type=str, help="Name of the branch", default="main")
@click.option("--source-branch", type=str, help="Source branch", default="main")
def change_branch(branch_name, source_branch):
    """Change the branch of the vector store"""
    config,config_dir = read_config()
    config["vectordb"]["branchName"] = branch_name
    config["vectordb"]["sourceBranch"] = source_branch
    write_config(config,config_dir)
