from mongoengine import Document, EmbeddedDocument, fields
from mongoengine import *

class LanguageEntryEntity(EmbeddedDocument):
    name = StringField(None)
    voiceName  = StringField(None)