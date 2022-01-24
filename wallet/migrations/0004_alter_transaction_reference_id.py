# Generated by Django 4.0.1 on 2022-01-06 00:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0003_transaction_reference_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='reference_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
