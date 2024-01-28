# learning/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import QuizForm, QuestionFormSet, AnswerFormSet, QuestionForm, AnswerForm
from .models import Teacher, Student, Course, Unit, Material, Quiz, Question, Answer, Enrollment, QuizQuestion, StudentResponse, LearningStyle, LearningStyleAssessment, QuizResponse, UnitGrade
from django.contrib.auth import login
from .forms import UserRegisterForm
from .forms import CourseForm, UnitForm, MaterialForm
from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from collections import Counter
from django.utils import timezone
import os
import random

#Funcion de registro
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesion del usuario
            return redirect('learning:login')  # Redirecciona al login
    else:
        form = UserRegisterForm()
    return render(request, 'learning/register.html', {'form': form})
#Funcion que re direcciona al usuario al panel correspondiente
def dashboard_redirect(request):
    user_email = request.user.email
    if Teacher.objects.filter(email=user_email).exists():
        return redirect('learning:teacher_dashboard')
    elif Student.objects.filter(email=user_email).exists():
        return redirect('learning:student_dashboard')
    else:
        #En caso de que no sea un estudiante ni un profesor (pendiente)
        return redirect('some_default_page')
# Función que brinda de la pantalla de bienvenida
def home(request):
    return render(request, 'learning/welcome.html')
#Funcion para mostrar el panel del profesor, requiere del inicio de sesión de uno
@login_required
def teacher_dashboard(request):
    teacher_email = request.user.email
    teacher = Teacher.objects.get(email=teacher_email)
    courses = Course.objects.filter(teacher=teacher)
    return render(request, 'learning/teacher_dashboard.html', {'courses': courses})
#Funcion para mostrar el panel del alumno, requiere que uno haya iniciado sesión
@login_required
def student_dashboard(request):
    student_email = request.user.email
    student = Student.objects.get(email=student_email)

    # Revisa si el estudiante ya completó el cuestionario de estilos de aprendizaje
    questionnaire_completed = StudentResponse.objects.filter(student=student).exists()

    # Pasa esta informacion al template
    return render(request, 'learning/student_dashboard.html', {'questionnaire_completed': questionnaire_completed})
#Permite al profesor crear un curso, depende de que el mismo haya iniciado sesión
@login_required
def create_course(request):
    teacher = Teacher.objects.get(email=request.user.email) 

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = teacher
            course.save()
            return redirect('learning:teacher_dashboard')
    else:
        form = CourseForm()

    return render(request, 'learning/create_course.html', {'form': form})

# Permite la edición del curso
def edit_course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('learning:teacher_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'learning/edit_course.html', {'form': form, 'course': course})


# Permite al profesor crear unidades dentro del curso.
def create_unit(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.course = course
            unit.save()
            return redirect('learning:edit_course', course_id=course_id)
    else:
        form = UnitForm()
    return render(request, 'learning/create_unit.html', {'form': form, 'course': course})

# Permite edición de unidades 
def edit_unit(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    selected_learning_styles = unit.course.learning_styles.all()
    quiz = Quiz.objects.filter(unit=unit).first()
    quiz_exists = quiz is not None

    all_materials_added = all(
        Material.objects.filter(unit=unit, learning_style=ls).exists()
        for ls in selected_learning_styles
    )

    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            # Redirecciona al panel de profesor tras guardar
            return redirect('learning:teacher_dashboard')
    else:
        form = UnitForm(instance=unit)

    return render(request, 'learning/edit_unit.html', {
        'form': form,  # Incluye el form en el contexto
        'unit': unit,
        'quiz_exists': quiz_exists,
        'all_materials_added': all_materials_added,
        'quiz': quiz,
    })




#Permite añadir material para cada uno de los estilos de aprendizaje seleccionados
def add_material(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    selected_learning_styles = unit.course.learning_styles.all()

    # Encuentra cuál es el primer estilo de aprendizaje que aún no tiene material asignado
    current_learning_style = None
    for ls in selected_learning_styles:
        if not Material.objects.filter(unit=unit, learning_style=ls).exists():
            current_learning_style = ls
            break

    if current_learning_style:
        if request.method == 'POST':
            form = MaterialForm(request.POST, request.FILES)
            if form.is_valid():
                material = form.save(commit=False)
                material.unit = unit
                material.learning_style = current_learning_style
                material.save()
                messages.success(request, f"Material for '{current_learning_style.name}' uploaded successfully.")
                return redirect('learning:add_material', unit_id=unit_id)
        else:
            form = MaterialForm()
    else:
        messages.info(request, "All selected learning styles have materials uploaded.")
        return redirect('learning:edit_unit', unit_id=unit_id)

    return render(request, 'learning/add_material.html', {
        'form': form, 'unit': unit, 'current_learning_style': current_learning_style
    })
#Permite borrar el archivo de material añadido a una unidad
def delete_file_if_exists(file_path):
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.isfile(full_path):
        os.remove(full_path)
        return True
    return False






# Permite edición del material una vez subido. Como borrar el archivo o reemplazarlo por otro
def edit_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    old_file_path = material.file.path if material.file else None

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            clear_file = 'file-clear' in request.POST

            if clear_file and old_file_path:
                # Elimina el archivo y lo borra del sistema
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                material.file = None
                material.save(update_fields=['file'])  # Guardar

            elif 'file' in request.FILES:
                # Si un nuevo archivo se sube, primero se guarda el form
                material = form.save()
                # Luego se borra el archivo anterior
                if old_file_path and os.path.exists(old_file_path):
                    os.remove(old_file_path)
            else:
                # Para guardar otros cambios si los hay
                form.save()

            messages.success(request, f"Material for '{material.learning_style.name}' updated successfully.")
            return redirect('learning:edit_unit', unit_id=material.unit.id)
    else:
        form = MaterialForm(instance=material)

    return render(request, 'learning/edit_material.html', {'form': form, 'material': material})




#Permite añadir una pregunta al cuestionario
def add_question_to_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('learning:edit_quiz_questions', quiz_id=quiz_id)
    else:
        form = QuestionForm()

    return render(request, 'learning/add_question.html', {'form': form, 'quiz': quiz})


#Permite crear un cuestionario dentro de una unidad
def create_quiz(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.unit = unit  # Marcar la unidad para este cuestionario
            quiz.save()
            return redirect('learning:edit_quiz_questions', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'learning/create_quiz.html', {'form': form, 'unit': unit})



def create_quiz(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.unit = unit  # Marcar la unidad para este cuestionario
            quiz.save()
            return redirect('learning:edit_quiz_questions', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'learning/create_quiz.html', {'form': form, 'unit': unit})


#Permite editar las preguntas del cuestionario
def edit_quiz_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)

    if request.method == 'POST':
        # Maneja passing_score (el puntaje necesario para aprobar)
        passing_score = request.POST.get('passing_score')
        if passing_score is not None:
            quiz.passing_score = int(passing_score)

        # Maneja num_questions_to_display (la cantidad de preguntas a mostrar)
        num_questions_to_display = request.POST.get('num_questions_to_display')
        if num_questions_to_display is not None:
            quiz.num_questions_to_display = int(num_questions_to_display)

        # Maneja num_answers_to_display (cantidad de respuestas por pregunta a mostrar)
        num_answers_to_display = request.POST.get('num_answers_to_display')
        if num_answers_to_display is not None:
            quiz.num_answers_to_display = int(num_answers_to_display)

        # Guarda el cuestionario con los cambios realizados
        quiz.save()

        # Redirecciona a la misma página para mostrar los cambios hechos al cuestionario
        return HttpResponseRedirect(request.path_info)

    return render(request, 'learning/edit_quiz_questions.html', {
        'quiz': quiz,
        'questions': questions
    })



#Añade una respuesta a una pregunta del cuestionario. Puede ser correcta o no. 
def add_answer_to_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('learning:edit_quiz_questions', quiz_id=question.quiz.id)
    else:
        form = AnswerForm()

    return render(request, 'learning/add_answer.html', {'form': form, 'question': question})

#Permite al profesor inscribir a los alumnos a un curso o des-inscribirlos.
def enroll_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.all()
    enrolled_students = Enrollment.objects.filter(course=course).values_list('student_id', flat=True)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id)

        if student.id in enrolled_students:
            # Expulsa al estudiante
            Enrollment.objects.filter(student=student, course=course).delete()
        else:
            # Inscribe al estudiante
            Enrollment.objects.create(student=student, course=course)

        return redirect('learning:enroll_students', course_id=course.id)

    context = {
        'course': course,
        'students': students,
        'enrolled_students': enrolled_students,
    }
    return render(request, 'learning/enroll_students.html', context)


def determine_learning_style(student_responses):
    # Cuenta le frecuencia de cada estilo de aprendizaje
    style_counts = Counter(response.answer.indicates_learning_style for response in student_responses)

    # Determina cual es el más común
    most_common_style = style_counts.most_common(1)[0][0]
    return most_common_style


def learning_style_quiz(request):
    if request.method == 'POST':
        student_email = request.user.email
        student_instance = Student.objects.get(email=student_email)

        # Procesa las respuestas del cuestionario de estilos de aprendizaje
        responses = []
        for key, value in request.POST.items():
            if key.startswith('question_'):
                answer_id = value
                responses.append(StudentResponse(student=student_instance, answer_id=answer_id))
        StudentResponse.objects.bulk_create(responses)

        # Determina el estilo de aprendizaje
        determined_style = determine_learning_style(responses)

        # Lo guarda en el modelo de la base de datos correspondiente
        LearningStyleAssessment.objects.update_or_create(
            student=student_instance,
            defaults={'learning_style': determined_style, 'assessment_date': timezone.now()}
        )

        return render(request, 'learning/learning_style_result.html', {'learning_style': determined_style})

    # Muestra las preguntas del cuestionario de estilos de aprendizaje
    questions = QuizQuestion.objects.all()
    return render(request, 'learning/learning_style_quiz.html', {'questions': questions})

#Muestra los cursos a los que el estudiante se encuentra inscrito.
def student_courses(request):
    student_email = request.user.email
    student = Student.objects.get(email=student_email)

    # Obtiene las inscripciones del aluno
    enrollments = Enrollment.objects.filter(student=student)

    # Obtiene los cursos de esas inscripciones
    courses = [enrollment.course for enrollment in enrollments]

    return render(request, 'learning/student_courses.html', {'courses': courses})

#Permite al estudiante interactuar con un curso.
def student_course_dashboard(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    student_email = request.user.email
    student = Student.objects.get(email=student_email)

    units = Unit.objects.filter(course=course).order_by('sequence_number')

    accessible_units = []
    for unit in units:
        if unit.sequence_number == 0:
            # La primer unidad (con sequence number 0) siempre esta disponible
            accessible_units.append(unit)
        else:
            # Intenta obtener la unidad previa (sequence_number-1)
            previous_unit = Unit.objects.filter(course=course, sequence_number=unit.sequence_number - 1).first()
            if previous_unit:
                quiz_for_previous_unit = Quiz.objects.filter(unit=previous_unit).first()
                if quiz_for_previous_unit:
                    student_grade = UnitGrade.objects.filter(student=student, unit=previous_unit).order_by('-attempt').first()
                    if student_grade and student_grade.grade >= quiz_for_previous_unit.passing_score:
                        accessible_units.append(unit)
                    else:
                        break  # Deja de añadir unidades si la unidad anterior no ha sido aprobada

    return render(request, 'learning/student_course_dashboard.html', {
        'course': course,
        'accessible_units': accessible_units
    })





    #Permite al estudiante interactuar con una unidad
def student_unit_dashboard(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    student_email = request.user.email
    student = Student.objects.get(email=student_email)

    # Obtiene el estilo de aprendizaje del alumno si este existe
    assessment = LearningStyleAssessment.objects.filter(student=student).last()
    if assessment:
        learning_style = assessment.learning_style
        # Obtiene los materiales para el estilo de aprendizaje correspondientes a esa unidad
        materials = Material.objects.filter(unit=unit, learning_style=learning_style)
    else:
        learning_style = None
        materials = []

    return render(request, 'learning/student_unit_dashboard.html', {'unit': unit, 'materials': materials, 'learning_style': learning_style})
#Permite al alumno responder el cuestionario de la unidad
def student_answer_quiz(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    quiz = get_object_or_404(Quiz, unit=unit)
    student_email = request.user.email
    student = get_object_or_404(Student, email=student_email)

    #Selecciona de forma aleatoria el numero de preguntas especificado
    total_questions_to_display = min(quiz.num_questions_to_display, quiz.questions.count())
    questions = random.sample(list(quiz.questions.all()), total_questions_to_display)

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_answer_id = request.POST.get('question_' + str(question.id))
            if selected_answer_id:
                selected_answer = get_object_or_404(Answer, id=selected_answer_id)
                is_correct = selected_answer.is_correct

                QuizResponse.objects.create(
                    student=student,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct
                )
                if is_correct:
                    score += 1
        #Califica las respuestas del alumno
        grade = round(score / total_questions_to_display * 100)
        passed = grade >= quiz.passing_score
        latest_grade = UnitGrade.objects.filter(student=student, unit=unit).order_by('-attempt').first()
        attempt_number = latest_grade.attempt + 1 if latest_grade else 1
        UnitGrade.objects.create(student=student, unit=unit, grade=grade, attempt=attempt_number)

        return redirect('learning:quiz_results', grade=grade, unit_id=unit.id, passed=passed)

    # Prepara respuestas de forma aleatoria para cada pregunta
    randomized_answers = {}
    for question in questions:
        answers = list(question.answers.all())
        correct_answers = [answer for answer in answers if answer.is_correct]
        incorrect_answers = [answer for answer in answers if not answer.is_correct]
        random.shuffle(incorrect_answers)  # Shuffle incorrect answers

        #  Se asegura de que solo una respuesta correcta sea incluida
        selected_answers = random.sample(correct_answers, 1)
        num_remaining_slots = min(quiz.num_answers_to_display, len(answers)) - 1
        selected_answers.extend(incorrect_answers[:num_remaining_slots])
        random.shuffle(selected_answers)  # Barajea aleatoriamente el set final de respuestas

        randomized_answers[question.id] = selected_answers

    return render(request, 'learning/student_answer_quiz.html', {'unit': unit, 'quiz': quiz, 'questions': questions, 'randomized_answers': randomized_answers})


#Muestra al alumno su resultado en ese cuestionario y por ende en la unidad
def quiz_results(request, grade, unit_id, passed):
    return render(request, 'learning/quiz_results.html', {'grade': grade, 'unit_id': unit_id, 'passed': passed})
