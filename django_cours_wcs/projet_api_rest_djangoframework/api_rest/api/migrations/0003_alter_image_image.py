# Generated by Django 5.0.2 on 2024-02-13 08:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_image_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.ImageField(upload_to=""),
        ),
    ]