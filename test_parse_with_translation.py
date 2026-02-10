#!/usr/bin/env python3
"""도시명 번역이 적용된 파싱 테스트"""

import json
import sys
sys.path.insert(0, '.')

from crawl_global import MarathonParser

# 원본 데이터 로드
print("원본 데이터 로드 중...")
with open('data/marathons_global_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

results = raw_data.get('results', [])
print(f"총 {len(results)}개 마라톤 발견\n")

# 샘플 10개만 파싱 테스트
print("=" * 80)
print("샘플 10개 파싱 결과 (도시명 번역 적용):")
print("=" * 80)

for i, raw_marathon in enumerate(results[:10], 1):
    parsed = MarathonParser.parse_marathon(raw_marathon)
    if parsed:
        orig_city = raw_marathon.get('city', '')
        orig_country = raw_marathon.get('country', '')

        print(f"\n{i}. {parsed['title']}")
        print(f"   원본: {orig_city}, {orig_country}")
        print(f"   번역: {parsed['city']}, {parsed['country']}")
        print(f"   Location: {parsed['location']}")

        # 번역 여부 표시
        city_translated = orig_city != parsed['city']
        status = "✅ 도시 번역됨" if city_translated else "⚪ 도시 원본"
        print(f"   상태: {status}")

print("\n" + "=" * 80)
print("✅ 테스트 완료!")
