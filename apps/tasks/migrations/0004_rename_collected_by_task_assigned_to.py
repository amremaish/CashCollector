# Generated by Django 5.0.6 on 2024-07-03 23:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_alter_task_amount_due'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='collected_by',
            new_name='assigned_to',
        ),
    ]
