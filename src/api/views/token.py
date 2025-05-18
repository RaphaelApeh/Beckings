from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token

from helpers.serializers import TokenLoginSerializer


class TokenLoginAPIView(GenericAPIView):
    
	model = Token
	serializer_class = TokenLoginSerializer
	authentication_classes = ()

	def post(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
		
		serializer = self.get_serializer(data=request.data)

		if not serializer.is_valid():
			return Response({"errors": "Invalid Data :("}, status=status.HTTP_401_UNAUTHORIZED)
		
		return Response(serializer.validated_data, status=status.HTTP_200_OK)
	

	def get_serializer(self, *args, **kwargs) -> TokenLoginSerializer:
		return super().get_serializer(*args, **kwargs)
	


