from datetime import datetime, timedelta
import json
import subprocess
import time
from langchain.prompts import PromptTemplate
from moviepy.editor import *
import os
import glob
from moviepy.editor import *
import azure.cognitiveservices.speech as speechsdk
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import (HumanMessage,SystemMessage,AIMessage)
from langchain.chat_models import AzureChatOpenAI, BedrockChat
import openai
from openai import AzureOpenAI, OpenAIError
import pyjson5
import re

from app.main.com.video.ai.enum import PromptType
from app.main.com.video.ai.service.StableDiffusionImageGeneratorService import ImageGenerator
from ..model.PromptTemplates import PromptTemplates
from ..model.Scripts import Scripts
from ..model.ScriptModel import ScriptEntryEntity, ScriptImageEntryEntity, ScriptModel
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings

class VideoService(object):

    def __init__(self, appConfig):
        self.connection_string = appConfig['CONNECTION_STRING']
        self.api_base = appConfig['API_BASE']
        self.api_version = appConfig['API_VERSION']
        self.api_key = appConfig['API_KEY']
        self.container_name = appConfig['CONTAINER_NAME']
        self.azure_speech_subscription_key = appConfig['AZURE_SPEECH_SUBSCRIPTION_KEY']
        self.api_type = appConfig["OPENAI_API_TYPE"]
        self.table_name = appConfig["TABLE_ACCOUNT_NAME"]
        self.account_key = appConfig["TABLE_ACCOUNT_KEY"]
        self.open_api_key = appConfig["OPENAI_API_KEY"]
        self.open_api_base = appConfig["OPENAI_API_BASE"]
        # aai.settings.api_key = "assemblyai-api-key"#just trying this

    
    def createVideoScript(self, topic, sceneCount, appConfig):
        scriptParser = PydanticOutputParser(pydantic_object=Scripts)
        parser = scriptParser.get_format_instructions()
        scriptBatchMessage = self.createPromptForScenes(topic, sceneCount)
        model = self.buildAzureChatOpenAIConfig(appConfig)
        result = model.generate(scriptBatchMessage)
        output=result.generations[0][0].text

        scriptOutput = scriptParser.parse(output).json()
        scriptJson = json.loads(scriptOutput)
        print(scriptJson["script"])
        # json5Output = self.json5toJson(output)
        script_entries = []
        for script_data in scriptJson["script"]:
            script_entry = ScriptEntryEntity(
                scene=script_data["scene"],
                scriptImages=[
                    ScriptImageEntryEntity(sceneImage=image_data["sceneImage"]) for image_data in script_data["scriptImages"]
                ]
            )
            script_entries.append(script_entry)

        scriptObject = ScriptModel(
            isFailed=False,
            topic=topic,
            script=script_entries,
            sceneCount=sceneCount
        )
        # scriptObject = ScriptModel(script = script_entries,sceneCount = sceneCount, isFailed = False, topic = topic)
        scriptEntry = ScriptModel.save(scriptObject)
        print(scriptEntry)



        # image_base_dir = os.path.realpath("./images")
        # audio_base_dir = os.path.realpath("./audio")
        fps = 24
        result_map = {}
        audio_base_path = './audio/{}.mp3'
        video_clips = []
        # image_list = glob.glob(os.path.join(image_base_dir, '*'))

        # Print the list of sentences
        for i, sentence in enumerate(scriptJson["script"], 1):
            # generate 3 images for with each scene text
            imageList = []
            imageCount = len(sentence["scriptImages"])
            for j, images in enumerate(sentence["scriptImages"], 1):
                image_name = f"image{(i-1) * imageCount + j}.png"
                # uploaded_url = self.upload_blob_from_url(imageUrl["url"], image_name)
                
                uploaded_url = self.imageGeneratorService(images["sceneImage"], image_name, scriptEntry["scriptId"])
                imageList.append(uploaded_url)
            # use this for static images(just trying with local images whether it works or not)
            
            # image_base_dir = os.path.realpath("./images")
            # imageList = glob.glob(os.path.join(image_base_dir, '*'))
            
            print(f"Sentence {i}: {sentence}")
            audio_path = self.synthesise_voice(sentence["scene"], audio_base_path.format(i), 'en-US-JennyMultilingualNeural')
            audio_clips = self.split_audio(audio_base_path.format(i), imageCount)  # Split audio into imageCount parts

        # audio_list = glob.glob(os.path.join(audio_base_dir, '*'))
            start_index = (i - 1) * imageCount
        # Load the image as a clip
            for k, (image, audio_clip) in enumerate(zip(imageList[start_index:start_index+imageCount], audio_clips), 1):
                # audio_clip = AudioFileClip(a)
                image_clip = ImageClip(image, duration=self.get_audio_duration(audio_clip))
                video_clip = image_clip.set_audio(audio_clip)
                video_clips.append(video_clip)

        concat_clip = concatenate_videoclips(video_clips, method="compose")
        concat_clip.write_videofile("test.mp4", fps=fps)

        # bad idea
        # subtitle_clips = self.create_subtitle_clips(subtitles,concat_clip.size)
        # video_with_subtitles = CompositeVideoClip([concat_clip] + subtitle_clips)
        # video_with_subtitles = CompositeVideoClip([concat_clip])
        # codec = 'libx264'

        concat_clip.write_videofile(local_video_path, fps=fps)
        
        # adding background music to the video
        
        # audio_clip = AudioFileClip(background_audio_path)
        # output_video_clip = VideoFileClip(local_video_path)
        # trimmed_audio_clip = audio_clip.subclip(0, video_clip.duration)
        # lowered_audio = volumex(trimmed_audio_clip, 0.5)
        # Add the audio to the video
        # output_video_clip.set_audio(lowered_audio)

        # output_video_clip.write_videofile('./', codec="libx264", audio_codec="aac")
        
        # uploading video to blob
        blob_client_url = self.upload_video_to_blob(local_video_path, topic + ".mp4", scriptEntry["scriptId"])
        return blob_client_url
    
    def synthesise_voice(self, text, output_file_path, voice):
        # speaking_rate=1.25
        azure_speech_subscription_key = self.azure_speech_subscription_key
        print(text)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file_path)
        
        speech_config = speechsdk.SpeechConfig(
            subscription=azure_speech_subscription_key, region="eastus")
        
        speech_config.speech_synthesis_voice_name = voice
        # speech_config.set_speech_synthesis_voice_name(f'{voice}', speaking_rate=speaking_rate)
        # speech_config.set_speech
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config)
        # save audio

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    audio_data = speech_synthesis_result.audio_data
                    print(f"Speech synthesized for lesson ")
                    break
                elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = speech_synthesis_result.cancellation_details
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(self.sleep_seconds*retry_count)
                        print(f"Retrying... (Attempt {retry_count+1})")
                    else:
                        print(f"Audio generation failed")
                        audio_data = None
                        print(f"Speech synthesis canceled: {cancellation_details.reason}")
                        if cancellation_details.reason == speechsdk.CancellationReason.Error:
                            if cancellation_details.error_details:
                                print(format(cancellation_details.error_details))
            except Exception as e:
                # Error handling
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying... (Attempt {retry_count+1}) ")
                else:
                    print(f"Audio generation failed ")
                    audio_data = None
        return audio_data
        
    def get_audio_duration(self, audio_clip):
        duration_in_seconds = audio_clip.duration
        return duration_in_seconds
    
    def split_audio(self, audio_path, num_parts):
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        part_duration = duration / num_parts

        audio_clips = []
        for i in range(num_parts):
            start_time = i * part_duration
            end_time = (i + 1) * part_duration
            audio_part = audio_clip.subclip(start_time, end_time)
            audio_clips.append(audio_part)

        return audio_clips

    def createPromptForScenes(self, topic, sceneCount):
        scriptParser = PydanticOutputParser(pydantic_object=Scripts)

        systemPromptObject = self.getActivePromptByRoleAndName(
            "system", PromptType.SCRIPTWRITING.value
        )
        systemPrompt =  PromptTemplate(
            input_variables=["topic", "sceneCount"],
            template = systemPromptObject["prompt"],
            partial_variables = {"format_instructions":  scriptParser.get_format_instructions()}
        )

        _systemMessage = systemPrompt.format_prompt(
            topic = topic,
            sceneCount = sceneCount
        )
        
        humanPromptObject = self.getActivePromptByRoleAndName(
            "human", PromptType.SCRIPTWRITING.value
        )

        humanPrompt = PromptTemplate(
            input_variables=["topic"],
            template =humanPromptObject["prompt"]
        )
        _humanMessage = humanPrompt.format_prompt(
            topic = topic
        )

        # _humanMessageText =  systemPromptObject["example"]["humanMessage"]
        # _aiMessage = systemPromptObject["example"]["aiMessage"]

        batch_messages = [[
            SystemMessage(content=_systemMessage.to_string()),
            HumanMessage(content=_humanMessage.to_string())
        ]]
        print(batch_messages)
        return batch_messages
    
    def buildAzureChatOpenAIConfig(self, appConfig):
        model = AzureChatOpenAI(
            openai_api_base = appConfig['OPENAI_API_BASE'],
            openai_api_version = appConfig['OPENAI_API_VERSION'],
            deployment_name = appConfig['DEPLOYMENT_NAME'],
            openai_api_key=  appConfig['OPENAI_API_KEY'],
            openai_api_type = appConfig['OPENAI_API_TYPE']
        )
        return model
    
    def json5toJson(text: str):
                try:
                    # Greedy search for 1st json candidate.
                    match = re.search(
                        r"\{.*}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
                    )
                    json_str = ""
                    if match:
                        json_str = match.group()
                    json_object = pyjson5.loads(json_str, strict=False)
                    return pyjson5.dumps(json_object)
                except:
                    return text
                

    def getActivePromptByRoleAndName(self, role, type):
        result = PromptTemplates.objects(role=role, type=type, active=True).first()
        return result
 
    def imageGeneratorService(self,prompt, name, scriptId):
        image_name = name
        print(f"image_name: {image_name} and {name}")
        openai.api_base = self.api_base
        openai.api_version = self.api_version
        openai.api_key = self.api_key
        openai.api_version = self.api_version
        openai.api_type = self.api_type

        client = AzureOpenAI(
        api_version=self.api_version,
        azure_endpoint=self.api_base,
        api_key=self.api_key,
        )
        sleep_seconds = 30
        max_retries = 3
        retry_count = 0
        url = None
        while retry_count < max_retries:
            try:
                if retry_count >= 1:
                    # print(f"Sleeping for {sleep_seconds*retry_count} seconds...")
                    time.sleep(sleep_seconds * retry_count)
                try:
                    print(f"Calling image generation API")
                    # raise e
                    result = client.images.generate(
                        model="video-ai-dalle-dev", # the name of your DALL-E 3 deployment
                        prompt=prompt,
                        n=1,
                        size= "1024x1792"
                        )
                    print(f"image_name: {image_name} and {name}")
        
                    url = json.loads(result.model_dump_json())["data"][0]["url"]
                    uploaded_url = self.upload_blob_from_url(url, image_name, scriptId, True)
                    break
                except OpenAIError as e:
                    if "Your task failed as a result of our safety system." in str(e):
                        raise e
                    raise e
            except Exception as e:
                print(f"Error while generating image  {e} Prompt:  {prompt}")
                retry_count += 1
                if (retry_count < max_retries):
                    print(f"Retrying... (Attempt {retry_count+1})")
                else:
                    print(f"image_name: {image_name} and {name}")
        
                    print(
                        f"Maximum retries reached. or exiting DALLE due to failed safety system")
                    base64Image = ImageGenerator.stableImage(self, prompt)
                    uploaded_url = self.upload_blob_from_url(base64Image, image_name, scriptId, False)
                    break
        return uploaded_url

    
    def upload_blob_from_url(self, source_url, image_name):
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        blob = blob_service_client.get_blob_client(container=self.container_name, blob=image_name)
        blob.upload_blob_from_url(source_url)
        sas_token = generate_blob_sas(
            account_name=self.connection_string.split(";")[1].split("=")[1],
            container_name=self.container_name,
            blob_name=image_name,
            account_key=self.connection_string.split(";")[2].split("=")[1],
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)  # Adjust the expiry as needed
        )
        blob_url_with_sas = f"https://{self.connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{self.container_name}/{image_name}{sas_token}"

    def append_audio(self, output_file):
        audio_base_dir = os.path.realpath("./audio")
        ffmpeg_path = r"C:\Users\userName\Downloads\ffmpeg-2024-02-15-git-a2cfd6062c-full_build\bin\ffmpeg.exe"  # Replace with the actual path to ffmpeg

        audio_files = [os.path.join(audio_base_dir, file) for file in os.listdir(audio_base_dir) if file.endswith(".mp3")]
        audio_segments = [subprocess.run([ffmpeg_path, '-i', file, '-f', 'mp3', '-'], capture_output=True).stdout for file in audio_files]

        concatenated_audio = b''.join(audio_segments)

        with open(output_file, 'wb') as f:
            f.write(concatenated_audio)


    def create_subtitle_clips(self, subtitles, videosize,fontsize=80, font='Montserrat-bold', color='yellow', debug = False):
        subtitle_clips = []
        video_width, video_height = videosize
        subtitle_x_position = 'center'
        subtitle_y_position = video_height * 4/5
        base_text_clip_config = {
            'fontsize': fontsize,
            'color': color,
            'font': font,
            'method': 'caption',
            'align': 'center'
        }
        
        pre_rendered_subtitle_clips = []
        for subtitle in subtitles:
            # text_clip_stroke = TextClip(subtitle.text, stroke_color='black', stroke_width=30, size=(video_width*3/4 + 30, None), **base_text_clip_config)
            text_clip = TextClip(subtitle.text, **base_text_clip_config)
            # pre_rendered_subtitle_clips.append(CompositeVideoClip([text_clip_stroke, text_clip], size=videosize))
            pre_rendered_subtitle_clips.append(CompositeVideoClip([text_clip], size=videosize))

        # Batch rendering and position calculation
        for subtitle, pre_rendered_clip in zip(subtitles, pre_rendered_subtitle_clips):
            start_time = self.time_to_seconds(subtitle.start)
            end_time = self.time_to_seconds(subtitle.end)
            duration = end_time - start_time

            # Use pre-rendered clip
            subtitle_clip = pre_rendered_clip.set_duration(duration).set_start(start_time).set_position((subtitle_x_position, subtitle_y_position))
            subtitle_clips.append(subtitle_clip)

        return subtitle_clips
    
    def time_to_seconds(self, time_obj):
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000
    
    def upload_video_to_blob(self, video_path, blob_name, folder_name):
        # Upload the video to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=f"{folder_name}/{blob_name}")
        with open(video_path, "rb") as video_file:
            blob_client.upload_blob(video_file.read(), content_settings=ContentSettings(content_type='video/mp4'))
        return blob_client.url

