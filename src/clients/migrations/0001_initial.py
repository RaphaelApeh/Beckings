# Generated by Django 5.2 on 2025-07-14 11:17

import django.core.validators
import django.db.models.deletion
import re
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("address", models.TextField(blank=True, default="")),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        null=True,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^(?:\\+234|0)[789][01]\\d{8}$"),
                                "Enter a Valid Phone Number",
                            )
                        ],
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
