from django.db import models

class Game(models.Model):
    game_name = models.CharField(max_length=255)
    original_price = models.FloatField()
    discount_price = models.FloatField()
    discount_startdate = models.CharField(max_length=20, null=True, blank=True)
    discount_enddate = models.CharField(max_length=20, null=True, blank=True)
    genre = models.CharField(max_length=255, null=True, blank=True)
    release_date = models.CharField(max_length=20, null=True, blank=True)
    maker = models.CharField(max_length=255, null=True, blank=True)
    player_number = models.CharField(max_length=50, null=True, blank=True)
    product_type = models.CharField(max_length=100)
    game_language = models.TextField(null=True, blank=True)
    game_image_url = models.URLField(null=True, blank=True)
    game_url = models.URLField(null=True, blank=True)

    '''매핑한 변수들
    # 게임 기본 정보
    game_name = models.CharField(max_length=255)  # 게임 이름
    genre = models.CharField(max_length=100)  # 장르 (예: 액션, RPG 등)
    release_date = models.DateField()  # 발매일
    maker = models.CharField(max_length=100)  # 메이커/회사
    product_type = models.CharField(max_length=100)  # 상품 유형 (예: 다운로드 전용, 패키지 등)
    player_number = models.CharField(max_length=50)  # 플레이 인원수 (예: 1~4명)
    game_language = models.CharField(max_length=100)  # 대응 언어 (예: 일본어, 한국어, 영어 등)

    # 가격 및 할인 정보
    original_price = models.DecimalField(max_digits=8, decimal_places=2)  # 정가
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # 할인가
    discount_startdate = models.DateField(null=True, blank=True)  # 할인 시작일
    discount_enddate = models.DateField(null=True, blank=True)  # 할인 종료일

    # 외부 리소스 링크
    game_image_url = models.URLField(max_length=500, null=True, blank=True)  # 게임 이미지 URL
    game_url = models.URLField(max_length=500, null=True, blank=True)  # 닌텐도 구매 페이지 URL
    '''

    '''기존 변수들
    game_name = models.CharField(max_length=255)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_startdate = models.DateField(null=True, blank=True)
    discount_enddate = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=255)
    release_date = models.DateField()
    maker = models.CharField(max_length=255)
    player_number = models.CharField(max_length=50)
    product_type = models.CharField(max_length=100)
    game_language = models.CharField(max_length=255)
    game_image_url = models.URLField()
    game_url = models.URLField()
    '''

    class Meta:
        db_table = 'game'  # 테이블 이름 수동 지정
        managed = False    # Django가 이 테이블을 만들지 않도록 설정

    def __str__(self):
        return self.game_name
    

# 가격 추이를 위한 클래스 선언
class PriceHistory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='price_history')
    date = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.game.game_name} - {self.date} - {self.price}"