from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# Добавили Favorite в импорт
from .models import Job, Profile, Application, Favorite 
from django.core.validators import RegexValidator
# SEC-004: CAPTCHA
try:
    from django_recaptcha.fields import ReCaptchaField
    from django_recaptcha.widgets import ReCaptchaV3
    HAS_RECAPTCHA = True
except ImportError:
    HAS_RECAPTCHA = False

# 1. Форма редактирования профиля (Умная фильтрация полей)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Убедись, что в models.py у тебя есть поле company_name или используй текущие
        fields = ['university', 'education', 'experience', 'skills', 'summary', 'bio', 'phone']
        widgets = {
            'university': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
            }),
            'education': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
                'rows': 3,
            }),
            'experience': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
                'rows': 4,
            }),
            'skills': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
                'rows': 3,
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
                'rows': 3,
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ЛОГИКА РАЗДЕЛЕНИЯ РОЛЕЙ:
        if self.instance and hasattr(self.instance, 'role'):
            if self.instance.role == 'employer':
                # Если это компания, меняем текст и подсказки
                self.fields['university'].label = "Название организации"
                self.fields['university'].widget.attrs.update({'placeholder': 'Введите название вашей компании'})
                self.fields['experience'].label = "О компании"
                self.fields['experience'].widget.attrs.update({'placeholder': 'Расскажите о вашей деятельности...'})
                self.fields['skills'].label = "Стек технологий"
                self.fields['skills'].widget.attrs.update({'placeholder': 'На чем работает ваша компания...'})
            else:
                # Если студент
                self.fields['university'].label = "Учебное заведение"
                self.fields['university'].widget.attrs.update({'placeholder': 'Ваш университет (например, AlmaU)'})
                self.fields['education'].label = "Образование"
                self.fields['education'].widget.attrs.update({'placeholder': 'Степень, специальность, годы обучения'})
                self.fields['experience'].label = "Опыт работы"
                self.fields['experience'].widget.attrs.update({'placeholder': 'Где вы работали или стажировались...'})
                self.fields['summary'].label = "Краткое резюме"
                self.fields['summary'].widget.attrs.update({'placeholder': 'Кратко опишите себя и ваши сильные стороны'})

# 2. Форма создания вакансии
class JobCreateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'salary', 'category', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all', 'placeholder': 'Python Developer'}),
            'company': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all', 'placeholder': 'Название компании'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all', 'placeholder': 'Алматы или Удаленка'}),
            'salary': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all', 'placeholder': 'Например, 300,000 - 500,000 ₸'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all', 'placeholder': 'IT / Маркетинг'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all', 'rows': 6, 'placeholder': 'Опишите задачи и требования...'}),
        }

# 3. Форма отклика
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
                'rows': 5,
                'placeholder': 'Расскажите, почему именно вы подходите на эту вакансию...'
            }),
        }

# 4. Регистрация
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
        'placeholder': 'example@mail.com'
    }))
    phone_validator = RegexValidator(regex=r'^\+?[0-9\s\-]{7,20}$', message='Enter a valid phone number.')
    phone = forms.CharField(required=False, max_length=20, validators=[phone_validator], widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
        'placeholder': '+7 701 000 0000'
    }))
    
    # SEC-004: Add reCAPTCHA v3 field
    if HAS_RECAPTCHA:
        captcha = ReCaptchaField(
            widget=ReCaptchaV3(attrs={'required_score': 0.5}),
            error_messages={'required': 'CAPTCHA verification failed'}
        )

    class Meta:
        model = User
        fields = ['username', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-200 outline-none focus:border-neutral-900 transition-all',
            'placeholder': 'Придумайте логин'
        })

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Ensure profile exists and save phone if provided
        phone = self.cleaned_data.get('phone')
        try:
            profile, _ = Profile.objects.get_or_create(user=user)
            if phone:
                profile.phone = phone
                profile.save()
        except Exception:
            # Don't let profile save errors break user creation
            pass
        return user