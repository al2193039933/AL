from django.db import models
from django.db.models import F, Max
import uuid

#Modelo para el profesor
class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

#Modelo para el alumno
class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

#Modelo para estilos de aprendizaje
class LearningStyle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

#Modelo para estilos de aprendizaje predeterminados. NO EN USO ACTUALMENTE
class CustomLearningStyle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

#Modelo para cursos 
class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    learning_styles = models.ManyToManyField(LearningStyle, blank=True)
    custom_learning_styles = models.ManyToManyField(CustomLearningStyle, blank=True)


    def __str__(self):
        return self.title

#Modelo para unidades
class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    sequence_number = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sequence_number']  

    def __str__(self):
        return self.title



#Modelo para cuestionarios
class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, related_name='quizzes')  
    title = models.CharField(max_length=255, null=True)
    passing_score = models.IntegerField(default=60)
    num_questions_to_display = models.PositiveIntegerField(default=5, help_text="Numero de preguntas a mostrar al alumno.")
    num_answers_to_display = models.PositiveIntegerField(default=4, help_text="Numero de respuestas a mostrar por pregunta.")

    def __str__(self):
        return self.title

#Modelo para preguntas
class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text
#Modelo para respuestas
class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text



#Modelo para material
class Material(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='materials', null=True, blank=True)
    learning_style = models.ForeignKey(LearningStyle, on_delete=models.CASCADE)
    file = models.FileField(upload_to='materials/', blank=True, null=True)  


    def __str__(self):
        return f"{self.unit.title} - {self.learning_style.name}"

#Modelo para inscripciones
class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')

#Modelo para camino de aprendizaje. NO EN USO
class LearningPath(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    learning_style = models.ForeignKey(LearningStyle, on_delete=models.CASCADE)
    custom_learning_style = models.ForeignKey(CustomLearningStyle, on_delete=models.CASCADE, null=True, blank=True)
    material_sequence = models.TextField()
    evaluation_sequence = models.TextField()

#Modelo para camino de aprendizaje de alumno. NO EN USO
class StudentLearningPath(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    progress = models.TextField()

#Modelo para asignacion de estilos de aprendizaje a alumno
class LearningStyleAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    learning_style = models.ForeignKey(LearningStyle, null=True, on_delete=models.CASCADE)
    assessment_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.student.name} - {self.learning_style.name}"

#Modelo de pregunta para el cuestionario de estilos de aprendizaje
class QuizQuestion(models.Model):
    text = models.TextField()  

    def __str__(self):
        return self.text


#Modelo de respuesta a las preguntas de estilo de aprendizaje
class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    indicates_learning_style = models.ForeignKey(LearningStyle, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

#Guarda las respuestas de los alumnos al cuestionario de estilo de aprendizaje
class StudentResponse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  
    answer = models.ForeignKey(QuizAnswer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'answer')

#Guarda las respuestas de los alumnos a los cuestionarios de las unidades.
class QuizResponse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.question.text} - {self.selected_answer.text}"

#Modelo para guardar las calificaciones del alumno
class UnitGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='unit_grades')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='grades')
    grade = models.FloatField()
    attempt = models.PositiveIntegerField(default=1)

    #class Meta:
     #   unique_together = ('student', 'unit')



    def __str__(self):
        return f"{self.student.name} - {self.unit.title}: Attempt {self.attempt}, Grade {self.grade}"

#Modelo para guardar calificacion del alumno en todo el curso. NO EN USO
class CourseGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    grade = models.FloatField()

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} - {self.course.title}: Overall Grade {self.grade}"
