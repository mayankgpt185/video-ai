
from mongoengine import *

class ScriptDetails(EmbeddedDocument):
    scene  = StringField(None)
