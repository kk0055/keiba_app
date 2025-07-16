from django.db import models


class Race(models.Model):
    """レース情報モデル"""

    race_id = models.CharField("レースID", max_length=20, primary_key=True)
    race_name = models.CharField("レース名", max_length=100, null=True, blank=True)
    race_date = models.DateField("開催日", null=True, blank=True)
    venue = models.CharField("開催地", max_length=50, null=True, blank=True)
    course_details = models.CharField("コース", max_length=50, null=True, blank=True)
    ground_condition = models.CharField(
        "馬場状態", max_length=20, null=True, blank=True
    )
    created_at = models.DateTimeField("登録日時", auto_now_add=True)

    class Meta:
        verbose_name = "レース"
        verbose_name_plural = "レース"
        ordering = ["-race_date"]  # 日付の降順で並ぶように

    def __str__(self):
        return f"{self.race_date} {self.venue} {self.race_name}"


class Trainer(models.Model):
    """調教師モデル"""

    trainer_id = models.CharField(
        max_length=20, primary_key=True, help_text="netkeibaの調教師ID"
    )
    trainer_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "調教師"
        verbose_name_plural = "調教師"

    def __str__(self):
        return self.trainer_name


class Horse(models.Model):
    """馬情報モデル"""

    horse_id = models.CharField("馬ID", max_length=20, primary_key=True)
    horse_name = models.CharField("馬名", max_length=100)
    birth_date = models.DateField("生年月日", null=True, blank=True)
    sex = models.CharField("性別", max_length=10, null=True, blank=True)
    trainer = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="調教師"
    )

    class Meta:
        verbose_name = "馬"
        verbose_name_plural = "馬"

    def __str__(self):
        return self.horse_name


class Jockey(models.Model):
    """騎手情報モデル"""

    jockey_id = models.CharField("騎手ID", max_length=20, primary_key=True)
    jockey_name = models.CharField("騎手名", max_length=100)

    class Meta:
        verbose_name = "騎手"
        verbose_name_plural = "騎手"

    def __str__(self):
        return self.jockey_name


class Entry(models.Model):
    """対象レース情報モデル"""

    race = models.ForeignKey(
        Race, on_delete=models.CASCADE, related_name="entries", verbose_name="レース"
    )
    horse = models.ForeignKey(
        Horse, on_delete=models.CASCADE, related_name="entries", verbose_name="馬"
    )
    jockey = models.ForeignKey(
        Jockey, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="騎手"
    )

    waku = models.IntegerField("枠番", null=True, blank=True)
    umaban = models.IntegerField("馬番", null=True, blank=True)
    weight_carried = models.FloatField("斤量", null=True, blank=True)

    odds = models.FloatField("オッズ", null=True, blank=True)
    popularity = models.IntegerField("人気", null=True, blank=True)

    horse_weight = models.IntegerField("馬体重", null=True, blank=True)
    horse_weight_diff = models.IntegerField("馬体重増減", null=True, blank=True)

    class Meta:
        verbose_name = "出走情報"
        verbose_name_plural = "出走情報"
        constraints = [
            models.UniqueConstraint(fields=["race", "horse"], name="unique_entry")
        ]
        ordering = ["race__race_date", "umaban"]

    def __str__(self):
        return f"{self.race.race_name} - {self.horse.horse_name}"


class HorsePastRace(models.Model):
    """馬の過去レース成績"""

    horse = models.ForeignKey(
        Horse, on_delete=models.CASCADE, related_name="past_races", verbose_name="馬"
    )
    past_race_id = models.CharField(max_length=20, null=True, blank=True)
    race_date = models.DateField("レース日")
    venue = models.CharField("開催地", max_length=20)
    race_name = models.CharField("レース名", max_length=100)
    weather = models.CharField("天気", max_length=10, null=True, blank=True)
    head_count = models.IntegerField("頭数", null=True, blank=True)
    waku = models.IntegerField("枠番", null=True, blank=True)
    umaban = models.IntegerField("馬番", null=True, blank=True)
    odds = models.FloatField("オッズ", null=True, blank=True)
    popularity = models.IntegerField("人気", null=True, blank=True)
    rank = models.IntegerField("着順", null=True, blank=True)
    jockey_id = models.CharField("騎手ID", max_length=100, null=True, blank=True)
    jockey_name = models.CharField("騎手名", max_length=100, null=True, blank=True)
    weight_carried = models.FloatField("斤量", null=True, blank=True)
    distance = models.CharField("距離(m)", max_length=20, null=True, blank=True)
    ground_condition = models.CharField("馬場", max_length=10, null=True, blank=True)
    time = models.CharField("タイム", max_length=20, null=True, blank=True)
    margin = models.CharField("着差", max_length=20, null=True, blank=True)
    passing = models.CharField("通過順", max_length=20, null=True, blank=True)
    pace = models.CharField("ペース", max_length=20, null=True, blank=True)
    last_3f = models.CharField("上がり3F", max_length=10, null=True, blank=True)
    body_weight = models.CharField("馬体重", max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "過去走成績"
        verbose_name_plural = "過去走成績"
        ordering = ["-race_date"]
        unique_together = ("horse", "past_race_id")

    def __str__(self):
        return f"{self.horse.horse_name} - {self.race_date} {self.race_name}"
