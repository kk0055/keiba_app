# Generated by Django 3.2.25 on 2025-07-17 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_horsepastrace_last_3f_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='horsepastrace',
            name='last_3f_rank',
            field=models.IntegerField(blank=True, null=True, verbose_name='上がり3Fの順番'),
        ),
    ]
