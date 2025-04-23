import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from games.models import Game


class Command(BaseCommand):
    help = "CSV 파일로부터 게임 데이터를 DB에 삽입합니다."

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='CSV 파일 경로를 입력하세요.')

    def handle(self, *args, **kwargs):
        csv_path = kwargs['csv_path']
        inserted_count = 0
        skipped_count = 0

        def safe_decimal(value):
            try:
                clean = value.replace("₩", "").replace(",", "").strip()
                return Decimal(clean)
            except:
                return None

        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                game_name = (row.get('game_name') or '').strip()
                product_type = (row.get('product_type') or '').strip()
                original_price = safe_decimal(row.get('original_price') or '')
                discount_price = safe_decimal(row.get('discount_price') or '') or original_price

                if not game_name or not product_type or original_price is None:
                    self.stdout.write(self.style.WARNING(
                        f"❌ 생략됨: game_name='{game_name}', product_type='{product_type}', original_price='{original_price}'"))
                    skipped_count += 1
                    continue

                game, created = Game.objects.get_or_create(
                    game_name=game_name,
                    product_type=product_type,
                    defaults={
                        'original_price': original_price,
                        'discount_price': discount_price,
                        'discount_startdate': row.get('discount_startdate', ''),
                        'discount_enddate': row.get('discount_enddate', ''),
                        'genre': row.get('genre', ''),
                        'release_date': row.get('release_date', ''),
                        'maker': row.get('maker', ''),
                        'player_number': row.get('player_number', ''),
                        'game_language': row.get('game_language', ''),
                        'game_image_url': row.get('game_image_url', ''),
                        'game_url': row.get('game_url', ''),
                        'collect_date': row.get('collect_date', ''),
                    }
                )

                if created:
                    inserted_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ 총 {inserted_count}개의 게임이 추가되었습니다."))
        self.stdout.write(self.style.WARNING(f"⚠️  {skipped_count}개의 항목은 누락되어 생략되었습니다."))
