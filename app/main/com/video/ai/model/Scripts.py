from typing import List
from mongoengine import *
from pydantic import Field, BaseModel, validator

class ScriptImageEntryEntity(BaseModel):
    sceneImage: str = Field(description="Scene image",required=True)

class ScriptEntryEntity(BaseModel):
    scene: str = Field(description="Scene",required=True)
    scriptImages: List[ScriptImageEntryEntity] = Field(description="List of script images")

class Scripts(BaseModel):
    script: List[ScriptEntryEntity] = Field(description="List of scripts")
