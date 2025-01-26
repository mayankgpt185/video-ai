import json
import base64
import tempfile
import requests
import os
import io
from PIL import Image
import base64
import mimetypes
import random

class ImageGenerator:
    def __init__(self, appConfig):
        self.appConfig = appConfig
        
        # this is from aws bedrock api
    # def req_img(self, text, style):
    #     """
    #     Returns: image: base64 string of image
    #     """
    #     random_seed = random.randint(0, 10000000)
    #     body = {
    #         "text_prompts": [{"text": text}],
    #         "cfg_scale": 10,
    #         "seed": random_seed,
    #         "steps": 50,
    #         "style_preset": style,
    #     }
    #     if style == "None":
    #         del body["style_preset"]
    #     body = json.dumps(body)
    #     modelId = self.appConfig["AWS"]["STABLE_DIFFUSION"]["IMAGE_MODEL_NAME"]
    #     accept = "application/json"
    #     contentType = "application/json"
    #     bedrock_runtime = Config.createBedrockConnection(
    #         appConfig=self.appConfig)
    #     response = bedrock_runtime.invoke_model(
    #         body=body, modelId=modelId, accept=accept, contentType=contentType
    #     )
    #     response_body = json.loads(response.get("body").read())
    #     results = response_body.get("artifacts")[0].get("base64")
    #     return results    

    def stableImage(self, prompt):
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        body = {
        "steps": 50,
        "width":  768,
        "height": 1344,
        "seed": 49376049,
        "cfg_scale": 25,
        "samples": 1,
        "style_preset": 'cinematic',
        "text_prompts": [
            {
                "text": prompt, 
                "weight": 1
            },
            {
            "text": "far, unclear, distorted face, (text), poor eyes, not looking at camera, not centered, dirty teeth, duplicate, separate, out of frame, half person, cartoon, 3d, multiple frames, color background, low quality,((disfigured)), ((bad art)), ((deformed)),((extra limbs)), ((extra barrel)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), (((tripod))), (((tube))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, 3d render, (((umbrella))), (ugly eyes, deformed iris, deformed pupils, fused lips and teeth:1.2), (un-detailed skin, semi-realistic, 3d, render, sketch, cartoon, drawing, anime:1.2), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
            "weight": -1
            }
            ],
        }

        headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "call from env-dev.json(this is from stability.ai website, for this u have create your account)",
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()

        for i, image in enumerate(data["artifacts"]):
            base64Image = base64.b64decode(image["base64"])

        return base64Image
