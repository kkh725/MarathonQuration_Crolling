#!/usr/bin/env python3
"""도시명 번역 테스트 스크립트"""

# crawl_global.py에서 CITY_KR 딕셔너리 복사
CITY_KR = {
    # 미국 주요 도시
    'New York': '뉴욕', 'Los Angeles': '로스앤젤레스', 'Chicago': '시카고',
    'Houston': '휴스턴', 'Phoenix': '피닉스', 'Philadelphia': '필라델피아',
    'San Antonio': '샌안토니오', 'San Diego': '샌디에이고', 'Dallas': '댈러스',
    'San Jose': '산호세', 'Austin': '오스틴', 'Jacksonville': '잭슨빌',
    'San Francisco': '샌프란시스코', 'Columbus': '콜럼버스', 'Indianapolis': '인디애나폴리스',
    'Fort Worth': '포트워스', 'Charlotte': '샬럿', 'Seattle': '시애틀',
    'Denver': '덴버', 'Washington': '워싱턴', 'Boston': '보스턴',
    'Nashville': '내슈빌', 'Detroit': '디트로이트', 'Portland': '포틀랜드',
    'Las Vegas': '라스베이거스', 'Memphis': '멤피스', 'Louisville': '루이빌',
    'Baltimore': '볼티모어', 'Milwaukee': '밀워키', 'Albuquerque': '앨버커키',
    'Tucson': '투손', 'Fresno': '프레즈노', 'Sacramento': '새크라멘토',
    'Kansas City': '캔자스시티', 'Atlanta': '애틀랜타', 'Miami': '마이애미',
    'Raleigh': '롤리', 'Minneapolis': '미니애폴리스', 'Omaha': '오마하',
    'Cleveland': '클리블랜드', 'New Orleans': '뉴올리언스', 'Tampa': '탬파',
    'Honolulu': '호놀룰루', 'Pittsburgh': '피츠버그', 'Cincinnati': '신시내티',
    'Orlando': '올랜도', 'St. Louis': '세인트루이스', 'Richmond': '리치먼드',
    'Buffalo': '버펄로', 'Salt Lake City': '솔트레이크시티',

    # 캐나다 주요 도시
    'Toronto': '토론토', 'Montreal': '몬트리올', 'Vancouver': '밴쿠버',
    'Calgary': '캘거리', 'Edmonton': '에드먼턴', 'Ottawa': '오타와',

    # 영국 주요 도시
    'London': '런던', 'Manchester': '맨체스터', 'Birmingham': '버밍엄',
    'Leeds': '리즈', 'Glasgow': '글래스고', 'Edinburgh': '에딘버러',
    'Liverpool': '리버풀', 'Bristol': '브리스톨', 'Sheffield': '셰필드',
    'Newcastle': '뉴캐슬', 'Belfast': '벨파스트', 'Cardiff': '카디프',
    'Windsor': '윈저', 'Richmond': '리치먼드', 'Winchester': '윈체스터',
    'Exeter': '엑서터', 'Bradford': '브래드퍼드', 'Plymouth': '플리머스',

    # 유럽 주요 도시
    'Paris': '파리', 'Berlin': '베를린', 'Rome': '로마', 'Madrid': '마드리드',
    'Barcelona': '바르셀로나', 'Vienna': '빈', 'Amsterdam': '암스테르담',
    'Prague': '프라하', 'Stockholm': '스톡홀름', 'Budapest': '부다페스트',
    'Copenhagen': '코펜하겐', 'Helsinki': '헬싱키', 'Oslo': '오슬로',
    'Istanbul': '이스탄불', 'İstanbul': '이스탄불', 'Tallinn': '탈린',
    'Hamburg': '함부르크', 'Munich': '뮌헨',

    # 아시아 주요 도시
    'Tokyo': '도쿄', 'Seoul': '서울', 'Beijing': '베이징',
    'Shanghai': '상하이', 'Hong Kong': '홍콩', 'Singapore': '싱가포르',
    'Bangkok': '방콕', 'Dubai': '두바이', 'Amman': '암만',

    # 남미 주요 도시
    'Rio de Janeiro': '리우데자네이루', 'Buenos Aires': '부에노스아이레스',

    # 오세아니아 주요 도시
    'Sydney': '시드니', 'Melbourne': '멜버른',

    # 아프리카 주요 도시
    'Kinshasa': '킨샤사', 'Cairo': '카이로',
}

def get_city_kr(city: str) -> str:
    """도시명을 한글로 변환 (매핑 없으면 원본 유지)"""
    return CITY_KR.get(city, city)

# 테스트
test_cities = [
    'Tokyo', 'Paris', 'London', 'New York', 'Seoul',
    'Istanbul', 'İstanbul', 'Berlin', 'Amman', 'Stockholm', 'Budapest',
    'Leeds', 'Unknown City', 'Mueang Khong', 'Rio de Janeiro',
    'Houston', 'Philadelphia', 'San Diego', 'Las Vegas'
]

print('도시명 번역 테스트:')
print('=' * 70)
for city in test_cities:
    kr = get_city_kr(city)
    status = '✅ 번역됨' if kr != city else '⚪ 원본 유지'
    print(f'{status} {city:25s} → {kr}')

print('\n' + '=' * 70)
print(f'✅ 총 {len(CITY_KR)}개 도시 매핑 완료')
