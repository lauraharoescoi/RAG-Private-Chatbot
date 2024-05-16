from bson import ObjectId

def convert_object_ids(document):
    if isinstance(document, dict):
        return {key: convert_object_ids(value) for key, value in document.items()}
    elif isinstance(document, list):
        return [convert_object_ids(element) for element in document]
    elif isinstance(document, ObjectId):
        return str(document)
    else:
        return document
