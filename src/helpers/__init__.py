import cloudinary
from django.conf import settings


CLOUDINARY_NAME = settings.CLOUDINARY_NAME
CLOUDINARY_API_KEY = settings.CLOUDINARY_API_KEY
CLOUDINARY_SECRET_KEY = settings.CLOUDINARY_SECRET_KEY


def init_cloudinary() -> None:

    cloudinary.config(
        cloud_name=CLOUDINARY_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_SECRET_KEY,
    )


def use_cloudinary() -> bool:

    return all([CLOUDINARY_API_KEY, CLOUDINARY_NAME, CLOUDINARY_SECRET_KEY])
