# Generated by Django 4.2.4 on 2023-10-01 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartapp', '0007_alter_coupon_valid_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
