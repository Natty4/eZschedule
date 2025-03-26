# Generated by Django 4.2 on 2025-02-27 11:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0031_alter_businesshour_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="business",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="business",
            name="name",
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="business",
            name="owner",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="businesses",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="business",
            name="phone_number",
            field=models.CharField(db_index=True, max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="start_date",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
