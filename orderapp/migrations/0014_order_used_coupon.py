# Generated by Django 4.2.4 on 2023-10-03 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cartapp', '0014_alter_coupon_discount'),
        ('orderapp', '0013_remove_order_order_grand_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='used_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cartapp.coupon'),
        ),
    ]
