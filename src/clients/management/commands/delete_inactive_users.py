import logging
from typing import Dict

from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


UserModel = get_user_model()

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Delete inactive user"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--all", action="store_true")
        parser.add_argument("--database", default="default")

    def handle(self, **options: Dict) -> None:

        assert getattr(
            settings, "USE_ACCOUNT_ACTIVATION_VIEW", True
        ), "USE_ACCOUNT_ACTIVATION_VIEW is set to false.\n hint = USE_ACCOUNT_ACTIVATION_VIEW = True"

        using = options.get("database")
        default_timestamp = getattr(
            settings, "ACCOUNT_ACTIVATION_TIMESTAMP", timezone.timedelta(hours=23)
        )

        try:
            now = timezone.now()
            qs = UserModel._default_manager.using(using).filter(
                is_active=False, date_joined__date=(now - default_timestamp)
            )
            if count := len(qs):
                qs.delete()
                self.stdout.write(
                    self.style.SUCCESS("Deleted Inactive Users \n count: %s", count)
                )
            else:
                self.stdout.write(self.style.WARNING("No inactive users."))
        except Exception as e:
            logger.error(f"Error \n {str(e)}")
