from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RaceSerializer, EntrySerializer,AIPredictionReadSerializer, AIPredictionWriteSerializer
from django.shortcuts import get_object_or_404
from .call_command_utils import scrape_and_export_csv, export_race_csv
from .models import Race, Entry, AIPrediction
from django.db.models import Count, Q, Sum
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

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
                scrape_and_export_csv(race_id)
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
                "horse__past_races"
            )
            .annotate(
                # 'win_place_count'という新しいフィールドを各Entryに追加
                # filter引数で条件に合うものだけをカウントする
                win_place_count=Count("horse__past_races", filter=win_place_condition),
                sum_grade_score=Sum("horse__past_races__race_grade_score"),
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
        export_race_csv(race_id)
        return Response(response_data)


class AIPredictionViewSet(viewsets.ModelViewSet):
    """
    AI予想のCRUD操作を行うAPIビュー
    """

    queryset = AIPrediction.objects.select_related(
        "race",
        # "predicted_first__horse",
        # "predicted_first__jockey",
        # "predicted_second__horse",
        # "predicted_second__jockey",
        # "predicted_third__horse",
        # "predicted_third__jockey",
    ).all()

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["race"]

    def get_serializer_class(self):
        """アクションに応じてシリアライザを切り替える"""
        if self.action in ["create", "update", "partial_update"]:
            return AIPredictionWriteSerializer
        return AIPredictionReadSerializer
