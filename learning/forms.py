from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Teacher, Student, Course, Unit, Material,LearningStyle, Quiz, Question, Answer
import uuid
#Formulario para registro de usuario
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Add a valid email address.')
    is_teacher = forms.BooleanField(required=False, label='Register as teacher')
    first_name = forms.CharField(required=True, max_length=255)
    last_name = forms.CharField(required=True, max_length=255)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_teacher']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            full_name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
            if self.cleaned_data['is_teacher']:
                Teacher.objects.create(id=uuid.uuid4(), name=full_name, email=self.cleaned_data['email'])
            else:
                Student.objects.create(id=uuid.uuid4(), name=full_name, email=self.cleaned_data['email'])
        return user
#Formato para creacion de curso
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'learning_styles', 'custom_learning_styles']
        widgets = {
            'learning_styles': forms.CheckboxSelectMultiple(),
            'custom_learning_styles': forms.CheckboxSelectMultiple()
        }

#Formato para creacion de unidad
class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['title', 'description','sequence_number']

#Formato para creacion de material
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['file'] 




#Formato para creacion de cuestionarios
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'passing_score','num_questions_to_display', 'num_answers_to_display']


#Formato para creacion de pregunta
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text',]
#Formato para creacion de respuesta
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct',]

QuestionFormSet = inlineformset_factory(
    Quiz, Question, fields=('text',), extra=3, can_delete=True)

AnswerFormSet = inlineformset_factory(
    Question, Answer, fields=('text', 'is_correct'), extra=4, can_delete=True)

