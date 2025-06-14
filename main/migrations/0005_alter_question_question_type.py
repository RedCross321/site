# Generated by Django 5.2 on 2025-05-24 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_pollresponse_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('single_choice', 'Один вариант ответа'), ('multiple_choice', 'Множественный выбор'), ('text', 'Текстовый ответ')], max_length=20, verbose_name='Тип вопроса'),
        ),
    ]
