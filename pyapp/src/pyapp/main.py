from functools import partial
from pathlib import Path
import click

from pyapp.cli.schemas import Project, ML, Observability, Config, Embeddings , VectorDB, TestData
from dotenv import load_dotenv

from typing import  Optional
from pyapp.cli.utils import read_config,write_config

from pyapp.config import find_config
from pyapp.vectordb.data import ingest_data , get_data , get_data_general, ingest_data_general
from pyapp.log.log_config import get_logger
logger = get_logger()
def trim_path(path:str):
    if path.startswith("./"):
        return path[2:]
    return path


class Pyapp:
    def __init__(self , config_path:Optional[str]=None):
        self.config_path = config_path if config_path else Path.cwd()
        self.read_config = partial(read_config, config_path=config_path)
        config,config_dir = self.read_config(give_error=False)
        self.load_env(config_path)
        self.dependencies = []
        if config:
            if config.get("project",{}).get("dependencies",None):
                self.dependencies = [Pyapp(config_path=Path(self.config_path / dependency["directory"]).resolve().absolute()) for dependency in config["project"]["dependencies"].values()]
            self.name = config.get("project",{}).get("name",None)
        self.load_env(config_dir)

    def load_env(self,config_dir:Path):
        try:
            appdeps_env = find_config(config_dir.parent, "appdeps.env")
            if appdeps_env:
                logger.info(f"Loading env file: {appdeps_env}")
                load_dotenv(appdeps_env, override=True)
        except Exception as e:
            # logger.warning(f"Error loading env file: {e}")
            pass

    def init(self,name: str, version: str, description: str, author: str):
        """Initialize a new SLMOPS project."""
        config,config_dir = self.read_config(give_error=False)
        if config:
            click.echo("Appdeps.toml already exists")
            return
        project = Project(name=name, version=version, description=description, author=author)
        config["project"] = project.model_dump()
        write_config(config,config_dir)
        Path(config_dir.parent / "appdeps.env").touch(exist_ok=True)
        Path(config_dir.parent / "pyapp.yaml").touch(exist_ok=True)
    
    def run(self, force:bool=False):
        if self.dependencies:
            for dependency in self.dependencies:
                dependency.run(force=True)
        """Install the project dependencies."""
        click.echo(f"Installing project dependencies {self.name} in {self.config_path}...")
        config,config_dir = self.read_config()
        # project = Project(**config["project"])
        if "observability" in config:
            from pyapp.observation.phoneix import observation
            observation.start()

        if "ml" in config:
            from pyapp.serve_integration import get_mlflow_embeddings_manager, get_mlflow_lm_manager
            ml = ML(**config["ml"])
            manager = None
            status = None
            if ml.provider == "local":
                if ml.type == "llm":
                    manager = get_mlflow_lm_manager(self.config_path / trim_path(ml.model_dir))
                    model = ml.serve
                    port = ml.serve.port
                if ml.type == "embeddings":
                    print(ml.model_dir)
                    manager = get_mlflow_embeddings_manager(self.config_path / trim_path(ml.model_dir))
                    model = ml.embeddings
                status = manager.new_model_status(model.model_name,model.alias)
                if status: 
                    click.echo(f"new version of the model `{model.model_name}` with alias `{model.alias}` is available. would you like to update to the latest version?")
                    #   cli(["run-latest"], standalone_mode=False)
                    self.run_latest(True)
                elif manager is not None:
                    if ml.type == "llm":
                        manager.add_serve(model_name=model.model_name, alias=model.alias, port=port)
                    if ml.type == "embeddings":
                        manager.add_serve(model_name=model.model_name, alias=model.alias)
        if force:
            if "vectordb" in config:
                self.download_from_vetordb(raw_data=False, force=True,use_commit_hash=False)

    def run_latest(self,latest:bool):
      """Install the project dependencies."""
    
      click.echo(f"Installing project dependencies {self.name} in {self.config_path}...")
      config,config_dir = self.read_config()
      manager = None
      if "ml" in config:
          from pyapp.serve_integration import get_mlflow_embeddings_manager, get_mlflow_lm_manager
          ml = ML(**config["ml"])
          if ml.provider == "local":
            if ml.type == "llm":
                manager = get_mlflow_lm_manager(self.config_path / trim_path(ml.model_dir))
                model = ml.serve
                port = ml.serve.port
            if ml.type == "embeddings":
                manager = get_mlflow_embeddings_manager(self.config_path / trim_path(ml.model_dir))
                model = ml.embeddings
            if manager is not None:
                if ml.type == "llm":
                    manager.update_model(model_name=model.model_name, alias=model.alias, port=port)
                if ml.type == "embeddings":
                    manager.update_model(model_name=model.model_name, alias=model.alias)
      
    def stop(self):
        """Stop the project."""
        from pyapp.observation.instance import PhoenixObservation
        observation = PhoenixObservation()
        """Stop the project."""
        observation.stop()
        
        if self.dependencies:
          for dependency in self.dependencies:
            dependency.stop()

        from pyapp.model_connection.lm.langchain.litellm import get_lm_model_manager
        click.echo(f"Stopping project dependencies {self.name} in {self.config_path}...")
        config,config_dir = self.read_config()
        conf = Config(**config)
        if "ml" in config:
            from pyapp.serve_integration import get_mlflow_embeddings_manager, get_mlflow_lm_manager
            ml = ML(**config["ml"])
            if ml.provider == "local":
                if ml.provider == "local" and ml.type == "llm":
                    manager = get_mlflow_lm_manager(self.config_path / trim_path(ml.model_dir))
                    manager.stop_all_serve()
                if ml.provider == "local" and ml.type == "embeddings":
                    manager = get_mlflow_embeddings_manager(self.config_path / trim_path(ml.model_dir))
                    manager.stop_all_serve()
      
    def remove(self):
        from pyapp.observation.instance import PhoenixObservation
        observation = PhoenixObservation()
        """Stop the project."""
        observation.remove()
        
        click.echo(f"Removing project dependencies {self.name} in {self.config_path}...")
        if self.dependencies:
          for dependency in self.dependencies:
            dependency.remove()
        config,config_dir = self.read_config()
        conf = Config(**config)
        if "ml" in config:
            from pyapp.serve_integration import get_mlflow_embeddings_manager, get_mlflow_lm_manager
            ml = ML(**config["ml"])
            if ml.provider == "local" and ml.type == "llm":
                manager = get_mlflow_lm_manager(self.config_path / trim_path(ml.model_dir))
                manager.delete_all_serve()
            if ml.provider == "local" and ml.type == "embeddings":
                manager = get_mlflow_embeddings_manager(self.config_path / trim_path(ml.model_dir))
                manager.delete_all_serve()
    
    def ingest_to_vectordb(self , raw_data:bool=False):
        for dependency in self.dependencies:
            dependency.ingest_to_vectordb(raw_data=raw_data)
        """Ingest the data to the vector store."""
        config,config_dir = self.read_config() 
        if "vectordb" in config:
            vectordb = VectorDB(**config["vectordb"])
            commit_id = ingest_data(vectordb,config_dir.parent,raw_data=raw_data)
            if commit_id:
                vectordb.commitHash = commit_id
                config["vectordb"] = vectordb.model_dump()
                write_config(config,config_dir)
        else: 
            logger.warning(f"No vector store found in {config_dir}")
    
    def download_from_vetordb(self,use_commit_hash:bool=False , force:bool=False , raw_data:bool=False):
        for dependency in self.dependencies:
            dependency.download_from_vetordb(use_commit_hash=use_commit_hash,force=force,raw_data=raw_data)
        config,config_dir = self.read_config() 
        if "vectordb" in config:
            vectordb = VectorDB(**config["vectordb"])
            if use_commit_hash:
                get_data(vectordb,main_dir=config_dir.parent,use_commit_hash=use_commit_hash,force=force,raw_data=raw_data)
            else:
                get_data(vectordb,main_dir=config_dir.parent,force=force,raw_data=raw_data)
        else:
            logger.warning(f"No vector store found in {config_dir}")
    
    def get_test_data(self, use_commit_hash:bool=False , force:bool=False ):
        for dependency in self.dependencies:
            dependency.get_test_data(use_commit_hash=use_commit_hash,force=force)
        config,config_dir = self.read_config() 
        if "test_data" in config:
            test_data = TestData(**config["test_data"])
            if use_commit_hash:
                get_data_general(test_data,main_dir=config_dir.parent,use_commit_hash=use_commit_hash,force=force,prefix="test_data")
            else:
                get_data_general(test_data,main_dir=config_dir.parent,force=force,prefix="test_data")
        else:
            logger.warning(f"No test data found in {config_dir}")
    
    def ingest_test_data(self):
        for dependency in self.dependencies:
            dependency.ingest_test_data()
        config,config_dir = self.read_config() 
        if "test_data" in config:
            test_data = TestData(**config["test_data"])
            ingest_data_general(test_data,config_dir.parent , prefix="test_data")
        else:
            logger.warning(f"No test data found in {config_dir}")


        

 
    


        




