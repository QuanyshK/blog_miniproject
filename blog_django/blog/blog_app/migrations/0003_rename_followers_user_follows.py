# Generated by Django 5.1.1 on 2024-10-06 22:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0002_user_followers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='followers',
            new_name='follows',
        ),
    ]
