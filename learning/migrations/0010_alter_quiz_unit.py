# Generated by Django 4.2.7 on 2023-12-26 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0009_remove_quiz_answers_remove_quiz_course_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='learning.unit'),
        ),
    ]