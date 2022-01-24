# Generated by Django 4.0.1 on 2022-01-05 17:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_address',
            field=models.TextField(blank=True, help_text='Customer Address', null=True, verbose_name='Customer Address'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=1, verbose_name='Customer Gender'),
        ),
        migrations.AddField(
            model_name='customer',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=17, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+9999999999'. Up to 10 digits allowed.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Customer Mobile Number'),
        ),
    ]