from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import login
from .models import Poll, Question, Choice, PollResponse, Answer, UserProfile
from .forms import PollForm, QuestionForm, ChoiceFormSet, PollResponseForm, AnswerForm, UserRegistrationForm, RespondentInfoForm, UserProfileForm, QuestionFormSet, QuestionWithChoicesFormSet
import json
from collections import Counter

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'register.html', {'form': form, 'profile_form': profile_form})

def home(request):
    if request.user.is_authenticated:
        # Показываем только опросы других пользователей
        polls = Poll.objects.exclude(author=request.user).order_by('-created_at')
    else:
        # Для неавторизованных пользователей показываем все опросы
        polls = Poll.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'polls': polls})

@login_required
def profile(request):
    created_polls = Poll.objects.filter(author=request.user)
    responses = PollResponse.objects.filter(poll__author=request.user).select_related('poll', 'user')
    return render(request, 'profile.html', {
        'created_polls': created_polls,
        'responses': responses
    })

@login_required
def create_poll(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.author = request.user
            poll.save()
            return redirect('add_questions', poll_id=poll.id)
    else:
        poll_form = PollForm()
    
    return render(request, 'create_poll.html', {'poll_form': poll_form})

@login_required
def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, author=request.user)
    
    if request.method == 'POST':
        poll_form = PollForm(request.POST, instance=poll)
        if poll_form.is_valid():
            poll_form.save()
            messages.success(request, 'Опрос успешно обновлен!')
            return redirect('profile')
    else:
        poll_form = PollForm(instance=poll)
    
    return render(request, 'edit_poll.html', {
        'poll_form': poll_form,
        'poll': poll
    })

@login_required
def edit_questions(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, author=request.user)
    questions = poll.questions.all().order_by('order')
    
    if request.method == 'POST':
        # Обработка удаления вопросов
        if 'delete_question' in request.POST:
            question_id = request.POST.get('question_id')
            question = get_object_or_404(Question, id=question_id, poll=poll)
            question.delete()
            messages.success(request, 'Вопрос успешно удален!')
            return redirect('edit_questions', poll_id=poll.id)
        
        # Обработка удаления варианта ответа
        if 'delete_choice' in request.POST:
            choice_id = request.POST.get('choice_id')
            choice = get_object_or_404(Choice, id=choice_id, question__poll=poll)
            choice.delete()
            messages.success(request, 'Вариант ответа успешно удален!')
            return redirect('edit_questions', poll_id=poll.id)
        
        # Обработка редактирования варианта ответа
        if 'edit_choice' in request.POST:
            choice_id = request.POST.get('choice_id')
            new_text = request.POST.get('edit_choice_text', '').strip()
            choice = get_object_or_404(Choice, id=choice_id, question__poll=poll)
            if new_text:
                choice.text = new_text
                choice.save()
                messages.success(request, 'Вариант ответа успешно изменен!')
            else:
                messages.error(request, 'Текст варианта не может быть пустым!')
            return redirect('edit_questions', poll_id=poll.id)
        
        # Обработка добавления варианта ответа
        if 'add_choice' in request.POST:
            question_id = request.POST.get('question_id')
            choice_text = request.POST.get('choice_text')
            question = get_object_or_404(Question, id=question_id, poll=poll)
            if choice_text:
                Choice.objects.create(question=question, text=choice_text)
                messages.success(request, 'Вариант ответа успешно добавлен!')
            return redirect('edit_questions', poll_id=poll.id)
        
        # Обработка добавления нового вопроса
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.poll = poll
            question.order = poll.questions.count() + 1
            question.save()
            
            messages.success(request, 'Вопрос успешно добавлен!')
            return redirect('edit_questions', poll_id=poll.id)
    else:
        question_form = QuestionForm()
    
    return render(request, 'edit_questions.html', {
        'poll': poll,
        'questions': questions,
        'question_form': question_form
    })

@login_required
def add_questions(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, author=request.user)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.poll = poll
            question.order = poll.questions.count() + 1
            question.save()
            
            if question.question_type in ['single_choice', 'multiple_choice']:
                choice_formset = ChoiceFormSet(request.POST, instance=question)
                if choice_formset.is_valid():
                    choice_formset.save()
            
            if 'add_another' in request.POST:
                return redirect('add_questions', poll_id=poll.id)
            return redirect('home')
    else:
        question_form = QuestionForm()
        choice_formset = ChoiceFormSet()
    
    return render(request, 'add_questions.html', {
        'poll': poll,
        'question_form': question_form,
        'choice_formset': choice_formset,
    })

def take_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    # Проверяем, не проходил ли пользователь этот опрос
    if request.user.is_authenticated:
        if PollResponse.objects.filter(poll=poll, user=request.user).exists():
            messages.warning(request, 'Вы уже проходили этот опрос')
            return redirect('home')
    else:
        # Для неавторизованных пользователей проверяем по имени и фамилии
        if 'respondent_name' in request.session and 'respondent_surname' in request.session:
            if PollResponse.objects.filter(
                poll=poll,
                respondent_name=request.session['respondent_name'],
                respondent_surname=request.session['respondent_surname']
            ).exists():
                messages.warning(request, 'Вы уже проходили этот опрос')
                return redirect('home')
    
    # Если пользователь не авторизован и не ввел имя/фамилию
    if not request.user.is_authenticated and 'respondent_name' not in request.session:
        if request.method == 'POST':
            form = RespondentInfoForm(request.POST)
            if form.is_valid():
                request.session['respondent_name'] = form.cleaned_data['respondent_name']
                request.session['respondent_surname'] = form.cleaned_data['respondent_surname']
                return redirect('take_poll', poll_id=poll.id)
        else:
            form = RespondentInfoForm()
        return render(request, 'respondent_info.html', {'form': form})
    
    if request.method == 'POST':
        with transaction.atomic():
            # Создаем запись о прохождении опроса
            poll_response = PollResponse.objects.create(
                poll=poll,
                user=request.user if request.user.is_authenticated else None,
                respondent_name=request.session.get('respondent_name', ''),
                respondent_surname=request.session.get('respondent_surname', '')
            )
            
            # Сохраняем ответы на вопросы
            for question in poll.questions.all():
                form = AnswerForm(request.POST, question=question, prefix=f'question_{question.id}')
                if form.is_valid():
                    if question.question_type == 'multiple_choice':
                        for choice in form.cleaned_data['multiple_choices']:
                            Answer.objects.create(
                                poll_response=poll_response,
                                question=question,
                                choice=choice
                            )
                    else:
                        answer = form.save(commit=False)
                        answer.poll_response = poll_response
                        answer.question = question
                        answer.save()
            
            # Очищаем сессию для неавторизованных пользователей
            if not request.user.is_authenticated:
                request.session.pop('respondent_name', None)
                request.session.pop('respondent_surname', None)
            
            messages.success(request, 'Спасибо за прохождение опроса!')
            return redirect('home')
    
    # Подготавливаем формы для каждого вопроса
    question_forms = []
    for question in poll.questions.all():
        form = AnswerForm(question=question, prefix=f'question_{question.id}')
        question_forms.append((question, form))
    
    return render(request, 'take_poll.html', {
        'poll': poll,
        'question_forms': question_forms
    })

@login_required
def poll_results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, author=request.user)
    responses = PollResponse.objects.filter(poll=poll).select_related('user').prefetch_related('answers')

    # Сбор статистики по вопросам
    questions_stats = []
    for question in poll.questions.all():
        stat = {'id': question.id, 'text': question.text, 'type': question.question_type}
        if question.question_type in ['single_choice', 'multiple_choice']:
            choices = list(question.choices.all())
            choice_counts = Counter()
            for response in responses:
                for answer in response.answers.all():
                    if answer.question_id == question.id and answer.choice:
                        choice_counts[answer.choice_id] += 1
            stat['choices'] = [
                {
                    'id': choice.id,
                    'text': choice.text,
                    'count': choice_counts[choice.id],
                } for choice in choices
            ]
            stat['total'] = sum(choice_counts.values())
        elif question.question_type == 'text':
            answers = []
            for response in responses:
                for answer in response.answers.all():
                    if answer.question_id == question.id and answer.text_answer:
                        answers.append(answer.text_answer)
            stat['answers'] = answers
            stat['total'] = len(answers)
        questions_stats.append(stat)

    return render(request, 'poll_results.html', {
        'poll': poll,
        'responses': responses,
        'questions_stats': json.dumps(questions_stats, ensure_ascii=False),
        'questions_stats_obj': questions_stats,
    })

@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, author=request.user)
    if request.method == 'POST':
        poll.delete()
        messages.success(request, 'Опрос успешно удалён!')
        return redirect('profile')
    return render(request, 'delete_poll_confirm.html', {'poll': poll})

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def create_poll_full(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        question_formset = QuestionFormSet(request.POST, queryset=Question.objects.none())
        if poll_form.is_valid() and question_formset.is_valid():
            poll = poll_form.save(commit=False)
            poll.author = request.user
            poll.save()
            for idx, question_form in enumerate(question_formset):
                if question_form.cleaned_data and not question_form.cleaned_data.get('DELETE', False):
                    question = question_form.save(commit=False)
                    question.poll = poll
                    question.order = idx + 1
                    question.save()
            messages.success(request, 'Опрос успешно создан!')
            return redirect('home')
    else:
        poll_form = PollForm()
        question_formset = QuestionFormSet(queryset=Question.objects.none())
    return render(request, 'create_poll_full.html', {
        'poll_form': poll_form,
        'question_formset': question_formset
    })

@login_required
def create_poll_full_v2(request):
    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        question_formset = QuestionWithChoicesFormSet(request.POST, prefix='questions')
        if poll_form.is_valid() and question_formset.is_valid():
            poll = poll_form.save(commit=False)
            poll.author = request.user
            poll.save()
            for idx, form in enumerate(question_formset):
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    question = form.save(commit=False)
                    question.poll = poll
                    question.order = idx + 1
                    question.save()
                    # Сохраняем варианты ответа
                    if question.question_type in ['single_choice', 'multiple_choice']:
                        for field_name in form.choices_fields:
                            text = form.cleaned_data.get(field_name)
                            if text:
                                Choice.objects.create(question=question, text=text)
            messages.success(request, 'Опрос успешно создан!')
            return redirect('home')
    else:
        poll_form = PollForm()
        question_formset = QuestionWithChoicesFormSet(prefix='questions')
    return render(request, 'create_poll_full_v2.html', {
        'poll_form': poll_form,
        'question_formset': question_formset
    })
