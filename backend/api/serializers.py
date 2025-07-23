from rest_framework import serializers
from .models import Race, Entry, Horse, Jockey, HorsePastRace
from django.db.models import Sum

class HorsePastRaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorsePastRace
        fields = [
            "past_race_id",
            "race_date",
            "venue_name",
            "race_name",
            "race_grade_score",
            "weather",
            "head_count",
            "waku",
            "umaban",
            "odds",
            "popularity",
            "rank",
            "jockey_id",
            "jockey_name",
            "weight_carried",
            "distance",
            "ground_condition",
            "time",
            "margin",
            "passing",
            "pace",
            "last_3f",
            "last_3f_rank",
            "body_weight",
        ]


class HorseSerializer(serializers.ModelSerializer):
    past_races = HorsePastRaceSerializer(
        many=True, read_only=True
    )  # related_name="past_races"から

    class Meta:
        model = Horse
        fields = ["horse_id", "horse_name", "past_races"]


class JockeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Jockey
        fields = ["jockey_id", "jockey_name"]


class EntrySerializer(serializers.ModelSerializer):
    horse = HorseSerializer()
    jockey = JockeySerializer()
    win_place_count = serializers.IntegerField(read_only=True, default=0)
    horse_past_race_grade_score_total = serializers.SerializerMethodField()
    class Meta:
        model = Entry
        fields = [
            "waku",
            "umaban",
            "weight_carried",
            "odds",
            "popularity",
            "horse",
            "jockey",
            "win_place_count",
            "horse_past_race_grade_score_total",
        ]

    def get_horse_past_race_grade_score_total(self, obj: Entry) -> int:
        """
        この出走馬 (Entry) に関連する馬 (Horse) の過去のレースの
        race_grade_score の合計を計算して返します。
        """
        total_score = obj.horse.past_races.aggregate(total=Sum('race_grade_score'))['total']
        return total_score if total_score is not None else 0


class RaceSerializer(serializers.ModelSerializer):
    entries = EntrySerializer(many=True, read_only=True)

    class Meta:
        model = Race
        fields = [
            "race_id",
            "race_name",
            "race_number",
            "race_date",
            "venue",
            "course_details",
            "ground_condition",
            "entries",
        ]
