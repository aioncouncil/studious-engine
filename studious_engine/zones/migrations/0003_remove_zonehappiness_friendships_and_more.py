# Generated by Django 5.0.12 on 2025-03-05 06:07

import django.core.validators
from django.db import migrations, models

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0002_zone_city_zone_country_zone_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zonehappiness',
            name='friendships',
        ),
        migrations.RemoveField(
            model_name='zonehappiness',
            name='glory',
        ),
        migrations.RemoveField(
            model_name='zonehappiness',
            name='honors',
        ),
        migrations.RemoveField(
            model_name='zonehappiness',
            name='resources',
        ),
        migrations.RemoveField(
            model_name='zonehappiness',
            name='wealth',
        ),
        migrations.AddField(
            model_name='zonehappiness',
            name='endurance',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='zonehappiness',
            name='good_score',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='zonehappiness',
            name='happiness',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='zonehappiness',
            name='last_calculated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='zonehappiness',
            name='prosperity_score',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='zonehappiness',
            name='virtue_history',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='zonehappiness',
            name='beauty',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='zonehappiness',
            name='courage',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='zonehappiness',
            name='health',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='zonehappiness',
            name='justice',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='zonehappiness',
            name='strength',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='zonehappiness',
            name='temperance',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='zonehappiness',
            name='wisdom',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
