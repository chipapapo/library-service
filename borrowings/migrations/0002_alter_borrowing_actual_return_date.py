# Generated by Django 4.2.4 on 2023-08-06 11:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateField(blank=True),
        ),
    ]
