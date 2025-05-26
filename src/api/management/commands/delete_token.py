from typing import Any

from django.utils import timezone
from django.core.management.base import BaseCommand

from ...models import get_token_model


class Command(BaseCommand):

    help = "Delete expired token"

    def handle(self, *args: list[Any], **options: dict[str, Any]) -> None:
        
        token = get_token_model()

        token.objects.filter(expired_at__lte=timezone.now()).delete()



