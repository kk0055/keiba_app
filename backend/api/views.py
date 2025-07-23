from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RaceSerializer, EntrySerializer
from django.shortcuts import get_object_or_404
from .scraping import scrape_and_save_race
from django.db.models import Prefetch
from .models import Race, Entry
from django.db.models import Count, Q, Sum


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

        race = Race.objects.filter(race_id=race_id).first()
        if not race:
            return Response(
                {"error": "データ取得後もレース情報が存在しません"},
                status=status.HTTP_404_NOT_FOUND,
            )

        #    Qオブジェクトで「rankが1, 2, 3のいずれか」という条件を作成
        win_place_condition = Q(horse__past_races__rank__in=[1, 2, 3])

        sorted_entries = (
            Entry.objects.filter(race=race)
            .select_related("jockey", "horse")
            .prefetch_related(
                # prefetch_relatedは引き続き有効（各馬の全過去レースデータを取得するため）
                "horse__past_races"
            )
            .annotate(
                # 'win_place_count'という新しいフィールドを各Entryに追加
                # filter引数で条件に合うものだけをカウントする
                win_place_count=Count("horse__past_races", filter=win_place_condition),
                sum_grade_score=Sum(
                    "horse__past_races__race_grade_score"
                ), 
            )
            .order_by(
                # win_place_countが多い順（降順）に並べ替え
                "-win_place_count",
                # "-sum_grade_score",
            )
        )

        # 3. データを手動でシリアライズしてレスポンスを構築する
        #    これにより、並べ替えたEntryリストを確実に使用できる
        race_serializer = RaceSerializer(race)
        entry_serializer = EntrySerializer(sorted_entries, many=True)

        # レスポンスデータを構築
        response_data = race_serializer.data
        response_data["entries"] = entry_serializer.data

        return Response(response_data)
