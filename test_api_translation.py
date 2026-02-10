#!/usr/bin/env python3
"""Google Translate API를 사용한 도시명 번역 테스트"""

import sys
sys.path.insert(0, '.')

from crawl_global import MarathonParser

# 테스트 도시들 (매핑 있는 것 + 없는 것)
test_cities = [
    # 매핑 있는 도시 (딕셔너리에서 바로 반환)
    ('Tokyo', '도쿄', True),
    ('Paris', '파리', True),
    ('London', '런던', True),

    # 매핑 없는 도시 (API로 번역)
    ('Mueang Khong', None, False),
    ('Antalya', None, False),
    ('Pokhara', '포카라', True),  # 딕셔너리에 있음
    ('Kathmandu', '카트만두', True),  # 딕셔너리에 있음
    ('Xiamen', None, False),
    ('Göreme', None, False),
    ('Batase', None, False),
    ('Thep Sadet', None, False),
]

print('=' * 80)
print('도시명 번역 테스트 (딕셔너리 + Google Translate API)')
print('=' * 80)

for city, expected, in_dict in test_cities:
    result = MarathonParser.get_city_kr(city)
    source = '📖 딕셔너리' if in_dict else '🌐 API 번역'

    print(f'\n{source} {city:25s} → {result}')
    if expected and result != expected:
        print(f'   ⚠️  예상: {expected}')

print('\n' + '=' * 80)
print('✅ 테스트 완료!')
print(f'번역 캐시 크기: {len(MarathonParser._translation_cache)}개')
