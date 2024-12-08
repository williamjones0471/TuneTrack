# Generated by Django 5.1.3 on 2024-12-08 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("musicapp", "0002_rename_user_playlist_owner_playlist_spotify_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="album",
            name="album_id",
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="artist",
            name="artist_id",
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="song",
            name="song_id",
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
    ]