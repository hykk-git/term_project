# Generated by Django 4.1 on 2024-05-21 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auto_manito", "0007_alter_muser_username"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="muser",
            options={},
        ),
        migrations.AlterUniqueTogether(
            name="muser",
            unique_together={("username", "group")},
        ),
    ]
