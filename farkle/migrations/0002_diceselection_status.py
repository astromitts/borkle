# Generated by Django 3.1.2 on 2020-10-25 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farkle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='diceselection',
            name='status',
            field=models.CharField(choices=[('active', 'active'), ('locked', 'locked')], default='active', max_length=10),
        ),
    ]
