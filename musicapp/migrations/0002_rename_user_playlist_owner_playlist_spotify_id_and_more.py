# Generated by Django 5.1.3 on 2024-12-03 22:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("musicapp", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="playlist",
            old_name="user",
            new_name="owner",
        ),
        migrations.AddField(
            model_name="playlist",
            name="spotify_id",
            field=models.CharField(default="test", max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="song",
            name="release_year",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="artist",
            name="genre",
            field=models.CharField(default="Unknown", max_length=255),
        ),
        migrations.AlterField(
            model_name="song",
            name="genre",
            field=models.CharField(default="Unknown", max_length=255),
        ),
        migrations.CreateModel(
            name="QuizSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField(default=0)),
                ("total_questions", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "playlist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="musicapp.playlist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question_text", models.TextField()),
                ("correct_answer", models.CharField(max_length=255)),
                (
                    "user_answer",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("is_correct", models.BooleanField(null=True)),
                (
                    "song",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="musicapp.song"
                    ),
                ),
                (
                    "quiz_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="musicapp.quizsession",
                    ),
                ),
            ],
        ),
    ]
