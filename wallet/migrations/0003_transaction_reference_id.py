# Generated by Django 4.0.1 on 2022-01-06 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_alter_transaction_id_alter_wallet_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='reference_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
