from .groups import cli
import click
from .schemas import ML, Serve, Litellm
from .utils import read_config,write_config

@click.group()
def ml():
    """Config the model to the project."""
    pass

@cli.command()
@click.option('--type', prompt="Type of the model", help="Type of the model", default="llm", type=click.Choice(["llm", "embeddings"]))
@click.option('--provider', prompt="Provider of the model", help="Provider of the model", default="local", type=click.Choice(["local", "litellm"]))
def add_ml( type:str, provider:str):
    """Add a the model to the project."""
    config,config_dir = read_config()
    ml = ML(type=type,provider=provider)
    config["ml"] = ml.model_dump()
    click.echo("Configuring the model to the project...")
    if provider == "local":
        # Call CLI again with subcommand name
        config["ml"]["serve"] = Serve(port=8080,model_name="model",alias="champion").model_dump()
        write_config(config,config_dir)
        ml(["add-serve"], standalone_mode=False)
    else:
        config["ml"]["litellm"] = Litellm(model="openai/custom",api_key="none",api_base="http://localhost:8080/v1").model_dump()
        write_config(config,config_dir)
        ml(["add-litellm"], standalone_mode=False)

@ml.command()
@click.option(
    '--port',
    prompt="Port of the serve",
    help="Port of the serve",
    default=8080,
    type=int
)
@click.option(
    '--model-name',
    prompt="Name of the model",
    help="Name of the model",
    type=str
)
@click.option(
    '--alias',
    prompt="Alias of the model",
    help="Alias of the model",
    type=str,
    default="champion"
)
@click.option(
    '--model-dir',
    prompt="Path to the model directory",
    help="Path to the model directory",
    type=str,
    default="./"
)
@click.option(
    '--continue-setting',
    prompt="want to continue setting the decoder config?",
    help="want to continue setting the decoder config?",
    type=click.Choice(["y", "n"]),
    default="n"
)
def add_serve(port:int,model_name:str,alias:str,model_dir:str,continue_setting:bool):
    """Add a new serve to the project."""
    serve = Serve(port=port,model_name=model_name,alias=alias,model_dir=model_dir)
    config,config_dir = read_config()
    config["ml"]["serve"] = serve.model_dump()
    config["ml"]["litellm"] = Litellm(model="openai/custom",api_key="none",api_base=f"http://localhost:{port}/v1").model_dump()
    write_config(config,config_dir)
    if continue_setting == "y":
        ml(["add-litellm-serve"], standalone_mode=False)
    else:
        click.echo("✅ Created serve")

@ml.command()
@click.option(
    '--temperature' ,
    prompt="Temperature of the litellm",
    help="Temperature of the litellm",
    type=float,
    default=0.5
)
@click.option(
    '--max-tokens',
    prompt="Max tokens of the litellm",
    help="Max tokens of the litellm",
    type=int,
    default=1000
)
@click.option(
    '--top-p',
    prompt="Top p of the litellm",
    help="Top p of the litellm",
    type=float,
    default=1.0
)
@click.option(
    '--top-k',
    prompt="Top k of the litellm",
    help="Top k of the litellm",
    type=int,
    default=50
)
def add_litellm_serve(temperature:float,max_tokens:int,top_p:float,top_k:int):
    """Config the decoding parameters of the litellm."""
    litellm = Litellm(temperature=temperature,max_tokens=max_tokens,top_p=top_p,top_k=top_k)  
    config,config_dir = read_config()
    config["ml"]["litellm"] = litellm.model_dump()
    write_config(config,config_dir)
    click.echo("✅ Created litellm serve")

@ml.command()
@click.option(
    '--model',
    prompt="Model of the litellm",
    help="Model of the litellm",
    type=str
)
@click.option(
    '--api-key',
    prompt="API key of the litellm",
    help="API key of the litellm",
    type=str
)
@click.option(
    '--api-base',
    prompt="API base of the litellm",
    help="API base of the litellm",
    type=str
)
@click.option(
    '--temperature' ,
    prompt="Temperature of the litellm",
    help="Temperature of the litellm",
    type=float,
    default=0.5
)
@click.option(
    '--max-tokens',
    prompt="Max tokens of the litellm",
    help="Max tokens of the litellm",
    type=int,
    default=1000
)
@click.option(
    '--top-p',
    prompt="Top p of the litellm",
    help="Top p of the litellm",
    type=float,
    default=1.0
)
@click.option(
    '--top-k',
    prompt="Top k of the litellm",
    help="Top k of the litellm",
    type=int,
    default=50
)
def add_litellm(model:str,api_key:str,api_base:str,temperature:float,max_tokens:int,top_p:float,top_k:int):
    """Config the litellm to the project."""
    litellm = Litellm(model=model,api_key=api_key,api_base=api_base,temperature=temperature,max_tokens=max_tokens,top_p=top_p,top_k=top_k)
    config,config_dir = read_config()
    config["ml"]["litellm"] = litellm.model_dump()
    write_config(config,config_dir)