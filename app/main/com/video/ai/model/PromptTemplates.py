from mongoengine import *

class PromptTemplates(Document):
    meta = {'collection': 'promptTemplates'}
    prompt = StringField(None)
    role = StringField(None)
    active = BooleanField(None)
    type = StringField(None)
    
