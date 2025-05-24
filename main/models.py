from django.db import models
from django.contrib.auth.models import User

class Poll(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название опроса')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

class Question(models.Model):
    QUESTION_TYPES = (
        ('single_choice', 'Один вариант ответа'),
        ('multiple_choice', 'Множественный выбор'),
        ('text', 'Текстовый ответ'),
    )

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='questions', verbose_name='Опрос')
    text = models.TextField(verbose_name='Текст вопроса')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name='Тип вопроса')
    order = models.IntegerField(default=0, verbose_name='Порядок вопроса')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='Вопрос')
    text = models.CharField(max_length=200, verbose_name='Текст варианта ответа')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

class PollResponse(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='responses', verbose_name='Опрос')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    respondent_name = models.CharField(max_length=100, blank=True, verbose_name='Имя')
    respondent_surname = models.CharField(max_length=100, blank=True, verbose_name='Фамилия')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Ответ от {self.user.username}"
        return f"Ответ от {self.respondent_name} {self.respondent_surname}"

    class Meta:
        verbose_name = 'Ответ на опрос'
        verbose_name_plural = 'Ответы на опросы'
        constraints = [
            models.UniqueConstraint(
                fields=['poll', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_poll_user'
            ),
            models.UniqueConstraint(
                fields=['poll', 'respondent_name', 'respondent_surname'],
                condition=models.Q(user__isnull=True),
                name='unique_poll_respondent'
            )
        ]

class Answer(models.Model):
    poll_response = models.ForeignKey(PollResponse, on_delete=models.CASCADE, related_name='answers', verbose_name='Ответ на опрос', null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Выбранный вариант')
    text_answer = models.TextField(null=True, blank=True, verbose_name='Текстовый ответ')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.choice:
            return self.choice.text
        return self.text_answer

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
