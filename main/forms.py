from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Poll, Question, Choice, PollResponse, Answer, UserProfile
from django.forms import modelformset_factory, formset_factory

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class RespondentInfoForm(forms.Form):
    respondent_name = forms.CharField(
        label='Имя',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    respondent_surname = forms.CharField(
        label='Фамилия',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
        }

ChoiceFormSet = forms.inlineformset_factory(
    Question, Choice, form=ChoiceForm,
    extra=3, can_delete=True,
    min_num=1, validate_min=True
)

class PollResponseForm(forms.ModelForm):
    class Meta:
        model = PollResponse
        fields = []

class AnswerForm(forms.ModelForm):
    multiple_choices = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Выберите варианты'
    )

    class Meta:
        model = Answer
        fields = ['choice', 'text_answer']
        widgets = {
            'text_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        if question:
            if question.question_type == 'single_choice':
                self.fields['choice'].widget = forms.RadioSelect()
                self.fields['choice'].queryset = question.choices.all()
                self.fields['choice'].empty_label = None
                self.fields['choice'].required = True
                self.fields['text_answer'].widget = forms.HiddenInput()
                self.fields['multiple_choices'].widget = forms.HiddenInput()
            elif question.question_type == 'multiple_choice':
                self.fields['multiple_choices'].queryset = question.choices.all()
                self.fields['multiple_choices'].required = True
                self.fields['choice'].widget = forms.HiddenInput()
                self.fields['text_answer'].widget = forms.HiddenInput()
            else:
                self.fields['choice'].widget = forms.HiddenInput()
                self.fields['multiple_choices'].widget = forms.HiddenInput()
                self.fields['text_answer'].required = True

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

QuestionFormSet = modelformset_factory(
    Question,
    form=QuestionForm,
    extra=1,
    can_delete=True
)

class QuestionWithChoicesForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices_fields = []
        for i in range(3):  # 3 варианта по умолчанию
            self.fields[f'choice_{i}'] = forms.CharField(
                required=False,
                label=f'Вариант {i+1}',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            self.choices_fields.append(f'choice_{i}')

QuestionWithChoicesFormSet = formset_factory(QuestionWithChoicesForm, extra=1, can_delete=True) 