from typing import Any, Union, Optional

import cloudinary
import cloudinary.uploader
from django.conf import settings

from rest_framework import serializers


CLOUDINARY_NAME = settings.CLOUDINARY_NAME
CLOUDINARY_API_KEY = settings.CLOUDINARY_API_KEY
CLOUDINARY_SECRET_KEY = settings.CLOUDINARY_SECRET_KEY


def init_cloudinary() -> None:
          
    cloudinary.config( 
        cloud_name=CLOUDINARY_NAME, 
        api_key=CLOUDINARY_API_KEY, 
        api_secret=CLOUDINARY_SECRET_KEY 
    )


def use_cloudinary() -> bool:

    return all([CLOUDINARY_API_KEY, CLOUDINARY_NAME, CLOUDINARY_SECRET_KEY])



class CloudinaryImageField(serializers.Field):

    default_error_messages = {
        "invalid": "Invalid key {key}"
    }

    def __init__(self, *args, **kwargs) -> None:

        options = kwargs.pop("options", {})
        
        super().__init__(*args, **kwargs)
        self.options = options

    def to_internal_value(self, data) -> str:

        result = data # It can be a public_id or the url
        print(data)
        
        if hasattr(data, "read"):
            result = self.handle_image_upload(data)

        return result

    def handle_image_upload(self, data) -> str:
        returned_data = cloudinary.uploader.upload(data)
        try:
            return returned_data["url"] # or public_id
        except AttributeError:
            self.fail("invalid", key="url")

    def to_representation(self, value) -> Optional[Union[str, Any]]:
        
        print(value)
        
        if value is None:
            return None
        
        if hasattr(value, "url") and self.options is None:
            return value.url
        
        if hasattr(value, "build_url") and self.options:
            return value.build_url(**self.options)
                
        return value

