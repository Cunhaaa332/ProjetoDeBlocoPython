# Generated by Django 3.2.3 on 2021-07-26 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gerenciador_de_tarefas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedtime',
            name='start_time',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='schedtime',
            name='stop_time',
            field=models.CharField(max_length=200),
        ),
    ]
