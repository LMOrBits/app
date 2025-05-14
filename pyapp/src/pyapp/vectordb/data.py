from data.vectordb import ingest_data as data_ingest_data,LakeFsEmbeding,Credentials, get_vectordb_data as data_get_vectordb_data
# from data.vectordb import LakeFsEmbeding, Credentials
from pyapp.utils.config import get_config
from pathlib import Path
from pyapp.cli.schemas import VectorDB
from typing import Optional
from pyapp.log.log_config import logger

def get_vectordb_from_config_dir(config_dir:Path, config_file_name:str) -> VectorDB:
    config = get_config(config_dir, config_file_name)
    if "vectordb" not in config:
        raise ValueError("ml not found in config")
    
    vectordb = VectorDB(**config["vectordb"])
    return vectordb 

def ingest_data_from_config_dir(config_dir:Path, config_file_name:Optional[str]="appdeps.toml", commit_message:str="ingested data via pyapp"):
    vectordb = get_vectordb_from_config_dir(config_dir, config_file_name)
    ingest_data(vectordb, config_dir, commit_message)

def get_vectordb_data_from_config_dir(config_dir:Path, config_file_name:Optional[str]="appdeps.toml", force:bool=False):
    vectordb = get_vectordb_from_config_dir(config_dir, config_file_name)
    data = get_vectordb_data(vectordb, config_dir, force)
    return data
  


def ingest_data(vectordb:VectorDB, main_dir:Path, commit_message:str="ingested data via pyapp", raw_data:bool=False):
    if raw_data:
        ingest_data_general(vectordb, main_dir, commit_message, "raw_data")
    return ingest_data_general(vectordb, main_dir, commit_message, "vectordb")

def ingest_data_general(vectordb:VectorDB, main_dir:Path, commit_message:str="ingested data via pyapp", prefix:str="vectordb"):
    credentials = Credentials.from_env()
    lakefs_dataset = LakeFsEmbeding( credentials=credentials,
                                project_name=vectordb.name, 
                                branch_name=vectordb.branchName,
                                source_branch=vectordb.sourceBranch,
                                prefix=prefix,
                              )

    # does it end with /vectordb?
    data_path = Path(main_dir / vectordb.inRepoPath)
    data_path_raw_data = data_path / prefix

    if not (data_path_raw_data).is_dir():
        raise ValueError(f"{data_path_raw_data} must be a directory")

    commit = data_ingest_data(
    lakefs_dataset=lakefs_dataset,
    data_path=data_path,
    commit_message=commit_message,
)
    logger.success(f"Ingested data to {vectordb.name} from {vectordb.inRepoPath}/{prefix} with commit hash {commit.id} into branch {vectordb.branchName}")
    return commit.id

def get_data(vectordb:VectorDB, main_dir:Path , force:bool=False , use_commit_hash:bool=False , raw_data:bool=False):
    if raw_data:
        get_data_general(vectordb, main_dir, force, use_commit_hash, "raw_data")
    
    get_data_general(vectordb, main_dir, force, use_commit_hash, "vectordb")
    
def get_data_general(vectordb:VectorDB, main_dir:Path , force:bool=False , use_commit_hash:bool=False , prefix:str="vectordb"):
    credentials = Credentials.from_env()
    lakefs_dataset = LakeFsEmbeding( credentials=credentials,
                                project_name=vectordb.name, 
                                branch_name=vectordb.branchName,
                                source_branch=vectordb.sourceBranch,
                                prefix=prefix,
                              )
    data_path = main_dir/vectordb.inRepoPath/prefix
    if not data_path.is_dir():
        data_path.mkdir(parents=True, exist_ok=True)
    args = {
        "lakefs_dataset":lakefs_dataset,
        "data_path":data_path,
        "force":force,
    }
    if use_commit_hash:
        args["commit_hash"] = vectordb.commitHash
    data = data_get_vectordb_data(**args)
    if use_commit_hash:
        logger.success(f"Downloaded data from {vectordb.name} from {vectordb.inRepoPath} with commit hash `{vectordb.commitHash}` into branch `{vectordb.branchName}`")
    else:
        logger.success(f"Downloaded data from {vectordb.name} from {vectordb.inRepoPath} from branch `{vectordb.branchName}`")
    return data
  