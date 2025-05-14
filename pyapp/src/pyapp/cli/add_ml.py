from typing import Optional
from .groups import cli
import click
from .schemas import ML, Serve, Litellm, Embeddings, EmbeddingsLitellm
from .utils import read_config,write_config

@cli.group()
def ml():
    """🔧 Configure the model to the project."""
    pass

@cli.command()
@click.option('--type', prompt="Type of the model", help="Type of the model", default="llm", type=click.Choice(["llm", "embeddings"]))
@click.option('--provider', prompt="Provider of the model", help="Provider of the model", default="local", type=click.Choice(["local", "litellm"]))
def add_ml( type:str, provider:str):
    """🦄 Add the model to the project."""
    config,config_dir = read_config()
    ml_config = ML(type=type,provider=provider)
    config["ml"] = ml_config.model_dump()
    write_config(config,config_dir)
    click.echo("Configuring the model to the project...")
    if provider == "local":
        config["ml"]["serve"] = Serve(port=8080,model_name="model",alias="champion").model_dump()
        ml(["add-local-model"], standalone_mode=False)
    else:
        if type == "llm":
            config["ml"]["litellm"] = Litellm(model="openai/custom",api_key="none",api_base="http://localhost:8080/v1").model_dump()
            ml(["add-litellm"], standalone_mode=False)
        else:
            ml(["add-embeddings-litellm"], standalone_mode=False)

@ml.command()
@click.option(
    '--model-dir',
    prompt="Path to the model directory",
    help="Path to the model directory",
    type=str,
    default="./models"
)
def add_local_model(model_dir:str):
    config,config_dir = read_config()
    ml_schema = ML(**config["ml"])
    ml_schema.model_dir = model_dir
    config["ml"] = ml_schema.model_dump()
    write_config(config,config_dir)
    if ml_schema.type == "llm":
        ml(["add-lm-local"], standalone_mode=False)
    else:
        ml(["add-embeddings-local"], standalone_mode=False)

@ml.command()
@click.option(
    '--port',
    prompt="Port of the serve",
    help="Port of the serve",
    default=1111,
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
    "--serving-tech",
    prompt="Serving tech",
    help="Serving tech",
    type=click.Choice(["liteserve"]),
    default="liteserve"
)
def add_embeddings_local(port:int,model_name:str,alias:str,serving_tech:str):
    """Add a new serve to the project."""
    embeddings = Embeddings(port=port,model_name=model_name,alias=alias,serving_tech=serving_tech)
    config,config_dir = read_config()
    config["ml"]["embeddings"] = embeddings.model_dump()
    write_config(config,config_dir)
    click.echo("✅ Created embeddings serve")

@ml.command()
@click.option(
    '--model',
    prompt="Name of the model from https://docs.litellm.ai/docs/embedding/supported_embedding",
    help="Name of the model to be used ",
    type=str
)

def add_embeddings_litellm(model:str):
    """Add a new serve to the project."""
    embeddings = EmbeddingsLitellm(model=model)
    config,config_dir = read_config()
    config["ml"]["embeddings"] = embeddings.model_dump()
    write_config(config,config_dir)
    click.echo("✅ Created embeddings model please make sure if the model did not work checkout the litellm documentation and provide more details in this section if needed")

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
    "--serving-tech",
    prompt="Serving tech",
    help="Serving tech",
    type=click.Choice(["llamacpp"]),
    default="llamacpp"
)
@click.option(
    '--continue-setting',
    prompt="want to continue setting the decoder config?",
    help="want to continue setting the decoder config?",
    type=click.Choice(["y", "n"]),
    default="n"
)
def add_lm_local(port:int,model_name:str,alias:str,continue_setting:bool,serving_tech:str):
    """Add a new serve to the project."""
    serve = Serve(port=port,model_name=model_name,alias=alias,serving_tech=serving_tech)
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
    prompt="Model of the litellm , from https://docs.litellm.ai/docs/",
    help="Model of the litellm",
    type=str
)
@click.option(
    '--api-key',
    prompt="API key of the litellm , if not mentioned press enter",
    help="API key of the litellm",
    type=str,
    required=False,
    default=""
)
@click.option(
    '--api-base',
    prompt="API base of the litellm , if not mentioned press enter",
    help="API base of the litellm",
    type=str,
    required=False,
    default=""
)
@click.option(
    '--temperature' ,
    prompt="Temperature of the litellm",
    help="Temperature of the litellm",
    type=float,
    default=0
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
    args = {
        "model":model,
        "temperature":temperature,
        "max_tokens":max_tokens,
        "top_p":top_p,
        "top_k":top_k
    }
    if api_key :
        args["api_key"] = api_key
    if api_base :
        args["api_base"] = api_base

    litellm = Litellm(**args)
    config,config_dir = read_config()
    config["ml"]["litellm"] = litellm.model_dump()
    write_config(config,config_dir)
    click.echo("✅ Created litellm model")
    click.echo(f"please do not forget to update the appedeps.env based on the keys needed")