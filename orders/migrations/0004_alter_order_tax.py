# Generated by Django 4.1 on 2022-12-24 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.FloatField(default=0),
        ),
    ]