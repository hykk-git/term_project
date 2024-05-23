# Generated by Django 4.1 on 2024-05-18 08:38

import auto_manito.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auto_manito", "0003_alter_muser_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="muser",
            name="manito",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=auto_manito.models.reassign_manito,
                to="auto_manito.muser",
            ),
        ),
    ]
