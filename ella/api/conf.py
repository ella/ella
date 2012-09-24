from ella.utils.settings import Settings

# master API switch
ENABLED = False

# photo formats to be included when serializing Publishables
PUBLISHABLE_PHOTO_FORMATS = []

# default formats that should be serialized for each Photo
DEFAULT_PHOTO_FORMATS = []

api_settings = Settings('ella.api.conf', 'API')
