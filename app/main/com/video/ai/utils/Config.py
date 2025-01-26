import boto3
from langchain.chat_models import AzureChatOpenAI, BedrockChat
# from langchain.chat_models import 

class Config:
    # u can change this based on your chosen service

    @staticmethod
    def createBedrockConnection(appConfig):
        bedrock_runtime = boto3.client(
                    service_name=appConfig["AWS"]["service_name"],
                    region_name=appConfig["AWS"]['region_name'],
                    aws_access_key_id=appConfig["AWS"]["ACCESS_KEY"],
                    aws_secret_access_key=appConfig["AWS"]["SECRET_KEY"]
                )
        return bedrock_runtime

    @staticmethod
    def buildAzureChatOpenAIConfig(appConfig:any)->AzureChatOpenAI:
        model = AzureChatOpenAI(
            openai_api_base = appConfig['OPENAI_API_BASE'],
            openai_api_version = appConfig['OPENAI_API_VERSION'],
            deployment_name = appConfig['DEPLOYMENT_NAME'],
            openai_api_key=  appConfig['OPENAI_API_KEY'],
            openai_api_type = appConfig['OPENAI_API_TYPE']
        )
        return model
    
    @staticmethod
    def createAnthropicConnection(appConfig: any):
        chat_bedrock = BedrockChat(
                client= Config.createBedrockConnection(appConfig),
                streaming = True,
                verbose = True,
                model_id = appConfig['MODEL_ID'], 
                model_kwargs = appConfig['MODEL_KWARGS'],
                region_name=appConfig["AWS"]['region_name'],
            )
        return chat_bedrock