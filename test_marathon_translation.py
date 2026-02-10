#!/usr/bin/env python3
"""실제 마라톤 데이터로 번역 테스트"""

import json
import sys
sys.path.insert(0, '.')

from crawl_global import MarathonParser

# 원본 데이터 로드
print("원본 데이터 로드 중...\n")
with open('data/marathons_global_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

results = raw_data.get('results', [])[:20]  # 처음 20개만

print("=" * 85)
print("샘플 20개 번역 결과 (딕셔너리 + API):")
print("=" * 85)

dict_translated = 0
api_translated = 0
kept_original = 0

for i, raw_marathon in enumerate(results, 1):
    orig_city = raw_marathon.get('city', '')
    orig_country = raw_marathon.get('country', '')
    title = raw_marathon.get('title', '')

    # 번역
    translated_city = MarathonParser.get_city_kr(orig_city)
    translated_country = MarathonParser.get_country_kr(orig_country)

    # 통계
    if translated_city != orig_city:
        if orig_city in MarathonParser.CITY_KR:
            dict_translated += 1
            source = "📖"
        else:
            api_translated += 1
            source = "🌐"
    else:
        kept_original += 1
        source = "⚪"

    print(f"\n{i:2d}. {source} {title[:60]}")
    print(f"     원본: {orig_city}, {orig_country}")
    print(f"     번역: {translated_city}, {translated_country}")

print("\n" + "=" * 85)
print("통계:")
print(f"  📖 딕셔너리 번역: {dict_translated}개")
print(f"  🌐 API 번역: {api_translated}개")
print(f"  ⚪ 원본 유지: {kept_original}개")
print(f"  번역 캐시: {len(MarathonParser._translation_cache)}개")
print("=" * 85)
