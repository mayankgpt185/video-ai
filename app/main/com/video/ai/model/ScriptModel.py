from mongoengine import Document, EmbeddedDocument, StringField, BooleanField, IntField, EmbeddedDocumentListField

class ScriptImageEntryEntity(EmbeddedDocument):
    sceneImage = StringField(required=True)

class ScriptEntryEntity(EmbeddedDocument):
    scene = StringField(required=True)
    scriptImages = EmbeddedDocumentListField(ScriptImageEntryEntity)

class ScriptModel(Document):
    meta = {'collection': 'scripts', 'strict': False}
    isFailed = BooleanField(required=True)
    topic = StringField(required=True)
    script = EmbeddedDocumentListField(ScriptEntryEntity)
    sceneCount = IntField(required=True)
