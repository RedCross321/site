# Generated by Django 5.2 on 2025-05-24 10:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_pollresponse_respondent_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pollresponse',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='pollresponse',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='pollresponse',
            constraint=models.UniqueConstraint(condition=models.Q(('user__isnull', False)), fields=('poll', 'user'), name='unique_poll_user'),
        ),
        migrations.AddConstraint(
            model_name='pollresponse',
            constraint=models.UniqueConstraint(condition=models.Q(('user__isnull', True)), fields=('poll', 'respondent_name', 'respondent_surname'), name='unique_poll_respondent'),
        ),
    ]
