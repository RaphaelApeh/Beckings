from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from ..models import get_token_model
from helpers.serializers import TokenLoginSerializer, TokenLogoutSerializer

Token = get_token_model()


class TokenBaseAPIView(GenericAPIView):

    model = Token
    serializer_class = None
    authentication_classes = ()
    permission_classes = ()

    def post(
        self, request: Request, *args: list[Any], **kwargs: dict[str, Any]
    ) -> Response:

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenLoginAPIView(TokenBaseAPIView):

    serializer_class = TokenLoginSerializer


class TokenLogoutAPIView(TokenBaseAPIView):

    serializer_class = TokenLogoutSerializer
