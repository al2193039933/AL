from django.contrib import admin
from .models import Teacher, Student, LearningStyle, Material, Course, Unit, QuizQuestion, QuizAnswer, StudentResponse, LearningStyleAssessment, Quiz, Answer, Question, QuizResponse, Enrollment, UnitGrade

# Register your models here.
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(LearningStyle)
admin.site.register(Material)
admin.site.register(Course)
admin.site.register(Unit)
admin.site.register(QuizAnswer)
admin.site.register(StudentResponse)
admin.site.register(QuizQuestion)
admin.site.register(LearningStyleAssessment)
admin.site.register(Quiz)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(QuizResponse)
admin.site.register(Enrollment)
admin.site.register(UnitGrade)


