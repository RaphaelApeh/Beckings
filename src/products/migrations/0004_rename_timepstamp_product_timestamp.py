# Generated by Django 5.2 on 2025-05-12 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_rename_timpstamp_product_timepstamp"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="timepstamp",
            new_name="timestamp",
        ),
    ]
