# Generated by Django 5.0.2 on 2024-02-13 12:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_alter_image_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="Traduction",
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
                ("phrase", models.CharField(max_length=200)),
                ("traduction", models.CharField(max_length=200)),
            ],
        ),
    ]