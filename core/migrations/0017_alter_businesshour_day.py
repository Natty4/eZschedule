# Generated by Django 4.2 on 2025-02-20 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_alter_service_employee"),
    ]

    operations = [
        migrations.AlterField(
            model_name="businesshour",
            name="day",
            field=models.CharField(
                choices=[
                    ("sunday", "Sunday"),
                    ("monday", "Monday"),
                    ("tuesday", "Tuesday"),
                    ("wednesday", "Wednesday"),
                    ("thursday", "Thursday"),
                    ("friday", "Friday"),
                    ("saturday", "Saturday"),
                ],
                max_length=10,
            ),
        ),
    ]
