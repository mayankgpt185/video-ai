from mongoengine import *
from pydantic import BaseModel, Field, validator
from typing import List

class videoScript(BaseModel): 
    scripts: List[str] = Field(description="List of scripts")
