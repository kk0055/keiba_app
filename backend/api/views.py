from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RaceSerializer
from django.shortcuts import get_object_or_404
from .scraping import scrape_and_save_race
from django.db.models import Prefetch
from .models import Race, Entry

class RaceDetailView(APIView):
    """
    race_idをURLパラメータで受け取り、
    DBに無ければスクレイピングで取得→保存し、データを返す
    """

    def get(self, request, race_id):
        print(f"アクセスあり: race_id={race_id}")
        race = Race.objects.filter(race_id=race_id).first()
        if not race:
            # データがなければスクレイピングして登録
            try:
                scrape_and_save_race(race_id)
            except Exception as e:
                return Response(
                    {"error": f"データ取得に失敗しました: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            race = (
                Race.objects.filter(race_id=race_id)
                .prefetch_related(
                    Prefetch(
                        "entries",
                        queryset=Entry.objects.select_related(
                            "jockey", "horse"
                        ).prefetch_related("horse__past_races"),
                    )
                )
                .first()
            )
            if not race:
                return Response(
                    {"error": "データ取得後もレース情報が存在しません"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = RaceSerializer(race)
        return Response(serializer.data)
