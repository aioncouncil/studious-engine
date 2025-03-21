# Generated by Django 5.0.12 on 2025-03-05 16:21

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_economic_layer'),
        ('experiences', '0002_experience_latitude_experience_longitude'),
        ('zones', '0003_remove_zonehappiness_friendships_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlocation',
            name='current_zone_id',
        ),
        migrations.AddField(
            model_name='userlocation',
            name='current_zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_players', to='zones.zone'),
        ),
        migrations.AlterField(
            model_name='playerprofile',
            name='economic_layer',
            field=models.CharField(choices=[('port', 'Port'), ('laws', 'Laws'), ('republic', 'Republic')], default='port', max_length=10),
        ),
        migrations.CreateModel(
            name='Artifact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('artifact_type', models.CharField(choices=[('document', 'Document'), ('image', 'Image'), ('video', 'Video'), ('audio', 'Audio'), ('model', '3D Model'), ('code', 'Code'), ('design', 'Design'), ('physical', 'Physical Object'), ('other', 'Other')], max_length=15)),
                ('media_url', models.URLField(blank=True)),
                ('media_file', models.FileField(blank=True, null=True, upload_to='artifacts/')),
                ('content', models.TextField(blank=True)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('is_public', models.BooleanField(default=False)),
                ('is_validated', models.BooleanField(default=False)),
                ('validation_date', models.DateTimeField(blank=True, null=True)),
                ('quality_rating', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('collaborators', models.ManyToManyField(blank=True, related_name='collaborated_artifacts', to='core.playerprofile')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_artifacts', to='core.playerprofile')),
                ('related_art', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='art_artifacts', to='core.art')),
                ('related_experience', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='experience_artifacts', to='experiences.experience')),
                ('validator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='validated_artifacts', to='core.playerprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MediaAsset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(upload_to='media_assets/')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='media_assets/thumbnails/')),
                ('media_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video'), ('audio', 'Audio'), ('document', 'Document'), ('other', 'Other')], max_length=10)),
                ('file_size', models.IntegerField(default=0)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('dimensions', models.CharField(blank=True, max_length=50)),
                ('mime_type', models.CharField(blank=True, max_length=100)),
                ('is_public', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_media', to='core.playerprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
