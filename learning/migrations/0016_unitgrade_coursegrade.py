# Generated by Django 4.2.7 on 2024-01-05 23:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0015_quizresponse_is_correct'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.FloatField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_grades', to='learning.student')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='learning.unit')),
            ],
            options={
                'unique_together': {('student', 'unit')},
            },
        ),
        migrations.CreateModel(
            name='CourseGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.FloatField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='learning.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_grades', to='learning.student')),
            ],
            options={
                'unique_together': {('student', 'course')},
            },
        ),
    ]
