# Generated by Django 3.2 on 2022-03-11 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=250, verbose_name='متن پیام')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date Created')),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sent_messages', related_query_name='sent_messages', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='received_messages', related_query_name='received_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
