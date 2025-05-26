from typing import Union

from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication

from .models import Token, get_token_model


class TokenAuthentication(BaseTokenAuthentication):
    """
    Overiding the base token authentication
    """    
    model: Union[Token, None] = get_token_model()


