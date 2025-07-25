# Generated by Django 3.2.25 on 2025-07-15 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jockey',
            fields=[
                ('jockey_id', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='騎手ID')),
                ('jockey_name', models.CharField(max_length=100, verbose_name='騎手名')),
            ],
            options={
                'verbose_name': '騎手',
                'verbose_name_plural': '騎手',
            },
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('race_id', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='レースID')),
                ('race_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='レース名')),
                ('race_date', models.DateField(blank=True, null=True, verbose_name='開催日')),
                ('venue', models.CharField(blank=True, max_length=50, null=True, verbose_name='開催地')),
                ('course_details', models.CharField(blank=True, max_length=50, null=True, verbose_name='コース')),
                ('ground_condition', models.CharField(blank=True, max_length=20, null=True, verbose_name='馬場状態')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
            ],
            options={
                'verbose_name': 'レース',
                'verbose_name_plural': 'レース',
                'ordering': ['-race_date'],
            },
        ),
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('trainer_id', models.CharField(help_text='netkeibaの調教師ID', max_length=20, primary_key=True, serialize=False)),
                ('trainer_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': '調教師',
                'verbose_name_plural': '調教師',
            },
        ),
        migrations.CreateModel(
            name='Horse',
            fields=[
                ('horse_id', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='馬ID')),
                ('horse_name', models.CharField(max_length=100, verbose_name='馬名')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='生年月日')),
                ('sex', models.CharField(blank=True, max_length=10, null=True, verbose_name='性別')),
                ('trainer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.trainer', verbose_name='調教師')),
            ],
            options={
                'verbose_name': '馬',
                'verbose_name_plural': '馬',
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('waku', models.IntegerField(blank=True, null=True, verbose_name='枠番')),
                ('umaban', models.IntegerField(blank=True, null=True, verbose_name='馬番')),
                ('weight_carried', models.FloatField(blank=True, null=True, verbose_name='斤量')),
                ('finish_rank', models.IntegerField(blank=True, null=True, verbose_name='着順')),
                ('odds', models.FloatField(blank=True, null=True, verbose_name='オッズ')),
                ('popularity', models.IntegerField(blank=True, null=True, verbose_name='人気')),
                ('horse_weight', models.IntegerField(blank=True, null=True, verbose_name='馬体重')),
                ('horse_weight_diff', models.IntegerField(blank=True, null=True, verbose_name='馬体重増減')),
                ('horse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='api.horse', verbose_name='馬')),
                ('jockey', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.jockey', verbose_name='騎手')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='api.race', verbose_name='レース')),
            ],
            options={
                'verbose_name': '出走情報',
                'verbose_name_plural': '出走情報',
                'ordering': ['race__race_date', 'umaban'],
            },
        ),
        migrations.CreateModel(
            name='HorsePastRace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_date', models.DateField(verbose_name='レース日')),
                ('venue', models.CharField(max_length=20, verbose_name='開催地')),
                ('race_name', models.CharField(max_length=100, verbose_name='レース名')),
                ('weather', models.CharField(blank=True, max_length=10, null=True, verbose_name='天気')),
                ('head_count', models.IntegerField(blank=True, null=True, verbose_name='頭数')),
                ('waku', models.IntegerField(blank=True, null=True, verbose_name='枠番')),
                ('umaban', models.IntegerField(blank=True, null=True, verbose_name='馬番')),
                ('odds', models.FloatField(blank=True, null=True, verbose_name='オッズ')),
                ('popularity', models.IntegerField(blank=True, null=True, verbose_name='人気')),
                ('rank', models.IntegerField(blank=True, null=True, verbose_name='着順')),
                ('jockey_name', models.CharField(max_length=100, verbose_name='騎手')),
                ('weight_carried', models.FloatField(blank=True, null=True, verbose_name='斤量')),
                ('distance', models.IntegerField(blank=True, null=True, verbose_name='距離(m)')),
                ('course_type', models.CharField(blank=True, max_length=10, null=True, verbose_name='馬場')),
                ('time', models.CharField(blank=True, max_length=20, null=True, verbose_name='タイム')),
                ('margin', models.CharField(blank=True, max_length=20, null=True, verbose_name='着差')),
                ('passing', models.CharField(blank=True, max_length=20, null=True, verbose_name='通過順')),
                ('pace', models.CharField(blank=True, max_length=20, null=True, verbose_name='ペース')),
                ('last_3f', models.CharField(blank=True, max_length=10, null=True, verbose_name='上がり3F')),
                ('body_weight', models.IntegerField(blank=True, null=True, verbose_name='馬体重')),
                ('body_weight_diff', models.IntegerField(blank=True, null=True, verbose_name='増減')),
                ('horse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='past_races', to='api.horse', verbose_name='馬')),
            ],
            options={
                'verbose_name': '過去走成績',
                'verbose_name_plural': '過去走成績',
                'ordering': ['-race_date'],
                'unique_together': {('horse', 'race_date', 'race_name')},
            },
        ),
        migrations.AddConstraint(
            model_name='entry',
            constraint=models.UniqueConstraint(fields=('race', 'horse'), name='unique_entry'),
        ),
    ]
