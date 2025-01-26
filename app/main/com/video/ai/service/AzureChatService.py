import os
from langchain.chat_models import AzureChatOpenAI

# Set this to `azure`
os.environ["OPENAI_API_TYPE"] = "call this from env-dev.json"
os.environ["OPENAI_API_VERSION"] = "call this from env-dev.json"
os.environ["OPENAI_API_BASE"] = "call this from env-dev.json"
os.environ["OPENAI_API_KEY"] = "call this from env-dev.json"

def connectAzureChat():
    model = AzureChatOpenAI(
    openai_api_base='call this from env-dev.json',
    openai_api_version="call this from env-dev.json",
    deployment_name="call this from env-dev.json",
    openai_api_key='call this from env-dev.json',
    openai_api_type = "call this from env-dev.json",
    )
    return model

def getModel():
    if(model == None):
        model = connectAzureChat()
    return model

