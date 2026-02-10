#!/usr/bin/env python3
"""
World's Marathons API 데이터 수집 및 파싱 스크립트
필드 요약표에 따라 필요한 데이터만 추출
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

class MarathonParser:
    """마라톤 데이터 파싱 클래스"""

    # 번역 캐시 (같은 도시명을 여러 번 번역하지 않도록)
    _translation_cache = {}

    # 대회 타입 한글 변환
    RACE_TYPE_KR = {
        'full_marathon': '풀코스',
        'half_marathon': '하프',
        'ultra_marathon': '울트라',
        'ten_km': '10km',
        'five_km': '5km',
        'custom': '기타',
    }

    # 노면 타입 한글 변환
    SURFACE_KR = {
    'Asphalt': '매끄러운 도로',
    'Road': '일반 도로',
    'Trail': '산길',
    'Terrain': '흙길',
    'Mixed': '섞여 있음',
    'Track': '우레탄 트랙',
    'Urban trail': '공원 산책로',
    'Sand': '모래길',
    'Snow': '눈길',
    'Indoor': '실내',
    'Grass': '잔디',
    'Gravel': '자갈길',
    'Other': '기타',
}

    # 코스 난이도 한글 변환
    DIFFICULTY_KR = {
        'flat': '평평해요',
        'rolling': '조금 출렁여요',
        'undulating': '오르내림이 반복돼요',
        'hilly': '언덕이 많아요',
        'mountain': '험난한 산길',
        'extreme': '한계에 가까워요',
    }

    # 국가명 한글 변환
    COUNTRY_KR = {
        'Afghanistan': '아프가니스탄',
        'Albania': '알바니아',
        'Algeria': '알제리',
        'Andorra': '안도라',
        'Angola': '앙골라',
        'Antarctica': '남극',
        'Antigua and Barbuda': '앤티가 바부다',
        'Argentina': '아르헨티나',
        'Armenia': '아르메니아',
        'Aruba': '아루바',
        'Australia': '호주',
        'Austria': '오스트리아',
        'Azerbaijan': '아제르바이잔',
        'Bahamas': '바하마',
        'Bahrain': '바레인',
        'Bangladesh': '방글라데시',
        'Barbados': '바베이도스',
        'Belarus': '벨라루스',
        'Belgium': '벨기에',
        'Belize': '벨리즈',
        'Bermuda': '버뮤다',
        'Bhutan': '부탄',
        'Bolivia': '볼리비아',
        'Bosnia and Herzegovina': '보스니아 헤르체고비나',
        'Botswana': '보츠와나',
        'Brazil': '브라질',
        'Brunei': '브루나이',
        'Bulgaria': '불가리아',
        'Cabo Verde': '카보베르데',
        'Cambodia': '캄보디아',
        'Canada': '캐나다',
        'Cayman Islands': '케이맨 제도',
        'Chile': '칠레',
        'China': '중국',
        'Colombia': '콜롬비아',
        'Congo (Democratic Republic of the)': '콩고민주공화국',
        'Cook Islands': '쿡 제도',
        'Costa Rica': '코스타리카',
        'Croatia': '크로아티아',
        'Cuba': '쿠바',
        'Curaçao': '퀴라소',
        'Cyprus': '키프로스',
        'Czech Republic': '체코',
        "Côte d'Ivoire": '코트디부아르',
        'Denmark': '덴마크',
        'Dominican Republic': '도미니카 공화국',
        'Ecuador': '에콰도르',
        'Egypt': '이집트',
        'Estonia': '에스토니아',
        'Ethiopia': '에티오피아',
        'Falkland Islands (Malvinas)': '포클랜드 제도',
        'Faroe Islands': '페로 제도',
        'Fiji': '피지',
        'Finland': '핀란드',
        'France': '프랑스',
        'French Polynesia': '프랑스령 폴리네시아',
        'Gabon': '가봉',
        'Gambia': '감비아',
        'Georgia': '조지아',
        'Germany': '독일',
        'Ghana': '가나',
        'Gibraltar': '지브롤터',
        'Greece': '그리스',
        'Greenland': '그린란드',
        'Guam': '괌',
        'Guatemala': '과테말라',
        'Holy See': '바티칸',
        'Hong Kong': '홍콩',
        'Hungary': '헝가리',
        'Iceland': '아이슬란드',
        'India': '인도',
        'Indonesia': '인도네시아',
        'Iran': '이란',
        'Ireland': '아일랜드',
        'Isle of Man': '맨섬',
        'Israel': '이스라엘',
        'Italy': '이탈리아',
        'Jamaica': '자메이카',
        'Japan': '일본',
        'Jersey': '저지',
        'Jordan': '요르단',
        'Kazakhstan': '카자흐스탄',
        'Kenya': '케냐',
        'Kuwait': '쿠웨이트',
        'Kyrgyzstan': '키르기스스탄',
        "Lao People's Democratic Republic": '라오스',
        'Latvia': '라트비아',
        'Lebanon': '레바논',
        'Liberia': '라이베리아',
        'Liechtenstein': '리히텐슈타인',
        'Lithuania': '리투아니아',
        'Luxembourg': '룩셈부르크',
        'Macao': '마카오',
        'Madagascar': '마다가스카르',
        'Malawi': '말라위',
        'Malaysia': '말레이시아',
        'Maldives': '몰디브',
        'Malta': '몰타',
        'Martinique': '마르티니크',
        'Mauritius': '모리셔스',
        'Mexico': '멕시코',
        'Moldova (Republic of)': '몰도바',
        'Mongolia': '몽골',
        'Montenegro': '몬테네그로',
        'Morocco': '모로코',
        'Mozambique': '모잠비크',
        'Myanmar': '미얀마',
        'Namibia': '나미비아',
        'Nepal': '네팔',
        'Netherlands': '네덜란드',
        'New Zealand': '뉴질랜드',
        'Niger': '니제르',
        'Nigeria': '나이지리아',
        'North Korea': '북한',
        'North Macedonia': '북마케도니아',
        'Northern Mariana Islands': '북마리아나 제도',
        'Norway': '노르웨이',
        'Oman': '오만',
        'Pakistan': '파키스탄',
        'Panama': '파나마',
        'Paraguay': '파라과이',
        'Peru': '페루',
        'Philippines': '필리핀',
        'Poland': '폴란드',
        'Portugal': '포르투갈',
        'Puerto Rico': '푸에르토리코',
        'Qatar': '카타르',
        'Romania': '루마니아',
        'Russia': '러시아',
        'Rwanda': '르완다',
        'Réunion': '레위니옹',
        'Samoa': '사모아',
        'Sao Tome and Principe': '상투메 프린시페',
        'Saudi Arabia': '사우디아라비아',
        'Senegal': '세네갈',
        'Serbia': '세르비아',
        'Seychelles': '세이셸',
        'Sierra Leone': '시에라리온',
        'Singapore': '싱가포르',
        'Slovakia': '슬로바키아',
        'Slovenia': '슬로베니아',
        'Somalia': '소말리아',
        'South Africa': '남아프리카공화국',
        'South Korea': '대한민국',
        'Spain': '스페인',
        'Sri Lanka': '스리랑카',
        'Sweden': '스웨덴',
        'Switzerland': '스위스',
        'Syrian Arab Republic': '시리아',
        'Taiwan': '대만',
        'Tajikistan': '타지키스탄',
        'Tanzania': '탄자니아',
        'Thailand': '태국',
        'Togo': '토고',
        'Trinidad and Tobago': '트리니다드 토바고',
        'Tunisia': '튀니지',
        'Turkey': '튀르키예',
        'Turks and Caicos Islands': '터크스 케이커스 제도',
        'Uganda': '우간다',
        'Ukraine': '우크라이나',
        'United Arab Emirates': '아랍에미리트',
        'United Kingdom': '영국',
        'United States of America': '미국',
        'Uruguay': '우루과이',
        'Uzbekistan': '우즈베키스탄',
        'Vanuatu': '바누아투',
        'Vietnam': '베트남',
        'Virgin Islands (British)': '영국령 버진아일랜드',
        'Virgin Islands (U.S.)': '미국령 버진아일랜드',
        'Zambia': '잠비아',
        'Zimbabwe': '짐바브웨',
        'Åland Islands': '올란드 제도',
    }

    # 도시명 한글 변환 (세계 주요 마라톤 도시)
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
        'Quebec': '퀘벡', 'Winnipeg': '위니펙', 'Hamilton': '해밀턴',
        'Victoria': '빅토리아', 'Halifax': '핼리팩스',

        # 영국 주요 도시
        'London': '런던', 'Manchester': '맨체스터', 'Birmingham': '버밍엄',
        'Leeds': '리즈', 'Glasgow': '글래스고', 'Edinburgh': '에딘버러',
        'Liverpool': '리버풀', 'Bristol': '브리스톨', 'Sheffield': '셰필드',
        'Newcastle': '뉴캐슬', 'Belfast': '벨파스트', 'Cardiff': '카디프',
        'Leicester': '레스터', 'Nottingham': '노팅엄', 'Southampton': '사우샘프턴',
        'Brighton': '브라이튼', 'Oxford': '옥스퍼드', 'Cambridge': '케임브리지',
        'York': '요크', 'Bath': '바스', 'Bradford': '브래드퍼드',
        'Coventry': '코번트리', 'Hull': '헐', 'Plymouth': '플리머스',
        'Reading': '레딩', 'Canterbury': '캔터베리', 'Winchester': '윈체스터',
        'Chester': '체스터', 'Derby': '더비', 'Exeter': '엑서터',
        'Portsmouth': '포츠머스', 'Norwich': '노리치', 'Durham': '더럼',
        'Windsor': '윈저', 'Eastbourne': '이스트본', 'Bournemouth': '본머스',
        'Worthing': '워딩', 'Northampton': '노샘프턴',

        # 프랑스 주요 도시
        'Paris': '파리', 'Marseille': '마르세유', 'Lyon': '리옹',
        'Toulouse': '툴루즈', 'Nice': '니스', 'Nantes': '낭트',
        'Strasbourg': '스트라스부르', 'Montpellier': '몽펠리에', 'Bordeaux': '보르도',
        'Lille': '릴', 'Rennes': '렌', 'Reims': '랭스',
        'Le Havre': '르아브르', 'Saint-Étienne': '생테티엔', 'Toulon': '툴롱',
        'Grenoble': '그르노블', 'Dijon': '디종', 'Angers': '앙제',
        'Nîmes': '님', 'Aix-en-Provence': '엑상프로방스', 'Cannes': '칸',
        'Brest': '브레스트', 'Tours': '투르', 'Amiens': '아미앵',

        # 독일 주요 도시
        'Berlin': '베를린', 'Hamburg': '함부르크', 'Munich': '뮌헨',
        'Cologne': '쾰른', 'Frankfurt': '프랑크푸르트', 'Stuttgart': '슈투트가르트',
        'Düsseldorf': '뒤셀도르프', 'Dortmund': '도르트문트', 'Essen': '에센',
        'Leipzig': '라이프치히', 'Bremen': '브레멘', 'Dresden': '드레스덴',
        'Hanover': '하노버', 'Nuremberg': '뉘른베르크', 'Duisburg': '뒤스부르크',
        'Bochum': '보훔', 'Wuppertal': '부퍼탈', 'Bonn': '본',
        'Bielefeld': '빌레펠트', 'Mannheim': '만하임', 'Karlsruhe': '카를스루에',
        'Münster': '뮌스터', 'Augsburg': '아우크스부르크',

        # 스페인 주요 도시
        'Madrid': '마드리드', 'Barcelona': '바르셀로나', 'Valencia': '발렌시아',
        'Seville': '세비야', 'Zaragoza': '사라고사', 'Málaga': '말라가',
        'Murcia': '무르시아', 'Palma': '팔마', 'Las Palmas': '라스팔마스',
        'Bilbao': '빌바오', 'Alicante': '알리칸테', 'Córdoba': '코르도바',
        'Valladolid': '바야돌리드', 'Vigo': '비고', 'Gijón': '히혼',
        'Granada': '그라나다', 'San Sebastián': '산세바스티안',

        # 이탈리아 주요 도시
        'Rome': '로마', 'Milan': '밀라노', 'Naples': '나폴리',
        'Turin': '토리노', 'Palermo': '팔레르모', 'Genoa': '제노바',
        'Bologna': '볼로냐', 'Florence': '피렌체', 'Bari': '바리',
        'Catania': '카타니아', 'Venice': '베네치아', 'Verona': '베로나',
        'Messina': '메시나', 'Padua': '파도바', 'Trieste': '트리에스테',
        'Brescia': '브레시아', 'Parma': '파르마', 'Pisa': '피사',
        'Modena': '모데나', 'Rimini': '리미니', 'Ravenna': '라벤나',

        # 네덜란드 주요 도시
        'Amsterdam': '암스테르담', 'Rotterdam': '로테르담', 'The Hague': '헤이그',
        'Utrecht': '위트레흐트', 'Eindhoven': '에인트호번', 'Tilburg': '틸뷔르흐',
        'Groningen': '흐로닝언', 'Almere': '알메르', 'Breda': '브레다',
        'Nijmegen': '네이메헌', 'Maastricht': '마스트리흐트',

        # 벨기에 주요 도시
        'Brussels': '브뤼셀', 'Antwerp': '앤트워프', 'Ghent': '겐트',
        'Charleroi': '샤를루아', 'Liège': '리에주', 'Bruges': '브뤼헤',
        'Namur': '나뮈르', 'Leuven': '뢰번',

        # 스위스 주요 도시
        'Zurich': '취리히', 'Geneva': '제네바', 'Basel': '바젤',
        'Bern': '베른', 'Lausanne': '로잔', 'Lucerne': '루체른',
        'Interlaken': '인터라켄', 'St. Moritz': '생모리츠',

        # 오스트리아 주요 도시
        'Vienna': '빈', 'Graz': '그라츠', 'Linz': '린츠',
        'Salzburg': '잘츠부르크', 'Innsbruck': '인스브루크',

        # 북유럽 주요 도시
        'Stockholm': '스톡홀름', 'Gothenburg': '예테보리', 'Malmö': '말뫼',
        'Copenhagen': '코펜하겐', 'Oslo': '오슬로', 'Bergen': '베르겐',
        'Helsinki': '헬싱키', 'Tampere': '탐페레', 'Turku': '투르쿠',
        'Tallinn': '탈린', 'Reykjavik': '레이캬비크',

        # 동유럽 주요 도시
        'Warsaw': '바르샤바', 'Kraków': '크라쿠프', 'Prague': '프라하',
        'Budapest': '부다페스트', 'Bucharest': '부쿠레슈티', 'Sofia': '소피아',
        'Belgrade': '베오그라드', 'Zagreb': '자그레브', 'Bratislava': '브라티슬라바',
        'Ljubljana': '류블랴나', 'Vilnius': '빌뉴스', 'Riga': '리가',
        'Kiev': '키예프', 'Moscow': '모스크바', 'St. Petersburg': '상트페테르부르크',

        # 그리스/터키 주요 도시
        'Athens': '아테네', 'Thessaloniki': '테살로니키', 'Istanbul': '이스탄불',
        'İstanbul': '이스탄불', 'Ankara': '앙카라', 'Izmir': '이즈미르',

        # 아시아 주요 도시
        'Tokyo': '도쿄', 'Osaka': '오사카', 'Kyoto': '교토',
        'Yokohama': '요코하마', 'Nagoya': '나고야', 'Sapporo': '삿포로',
        'Fukuoka': '후쿠오카', 'Kobe': '고베', 'Hiroshima': '히로시마',
        'Sendai': '센다이', 'Nara': '나라', 'Okinawa': '오키나와',
        'Seoul': '서울', 'Busan': '부산', 'Incheon': '인천',
        'Daegu': '대구', 'Daejeon': '대전', 'Gwangju': '광주',
        'Beijing': '베이징', 'Shanghai': '상하이', 'Guangzhou': '광저우',
        'Shenzhen': '선전', 'Chengdu': '청두', 'Hong Kong': '홍콩',
        'Taipei': '타이베이', 'Singapore': '싱가포르', 'Bangkok': '방콕',
        'Kuala Lumpur': '쿠알라룸푸르', 'Manila': '마닐라', 'Jakarta': '자카르타',
        'Hanoi': '하노이', 'Ho Chi Minh': '호치민', 'Phnom Penh': '프놈펜',
        'New Delhi': '뉴델리', 'Mumbai': '뭄바이', 'Bangalore': '방갈로르',
        'Kolkata': '콜카타', 'Chennai': '첸나이', 'Hyderabad': '하이데라바드',
        'Kathmandu': '카트만두', 'Pokhara': '포카라', 'Colombo': '콜롬보',
        'Dhaka': '다카', 'Karachi': '카라치', 'Islamabad': '이슬라마바드',

        # 중동 주요 도시
        'Dubai': '두바이', 'Abu Dhabi': '아부다비', 'Doha': '도하',
        'Riyadh': '리야드', 'Jeddah': '제다', 'Amman': '암만',
        'Beirut': '베이루트', 'Jerusalem': '예루살렘', 'Tel Aviv': '텔아비브',

        # 오세아니아 주요 도시
        'Sydney': '시드니', 'Melbourne': '멜버른', 'Brisbane': '브리즈번',
        'Perth': '퍼스', 'Adelaide': '애들레이드', 'Canberra': '캔버라',
        'Gold Coast': '골드코스트', 'Auckland': '오클랜드', 'Wellington': '웰링턴',
        'Christchurch': '크라이스트처치', 'Queenstown': '퀸스타운',

        # 남미 주요 도시
        'Buenos Aires': '부에노스아이레스', 'São Paulo': '상파울루', 'Rio de Janeiro': '리우데자네이루',
        'Brasília': '브라질리아', 'Lima': '리마', 'Bogotá': '보고타',
        'Santiago': '산티아고', 'Caracas': '카라카스', 'Quito': '키토',
        'Montevideo': '몬테비데오', 'Asunción': '아순시온', 'La Paz': '라파스',

        # 아프리카 주요 도시
        'Cairo': '카이로', 'Cape Town': '케이프타운', 'Johannesburg': '요하네스버그',
        'Nairobi': '나이로비', 'Lagos': '라고스', 'Kinshasa': '킨샤사',
        'Casablanca': '카사블랑카', 'Marrakech': '마라케시', 'Tunis': '튀니스',
        'Addis Ababa': '아디스아바바', 'Dar es Salaam': '다르에스살람',

        # 멕시코 주요 도시
        'Mexico City': '멕시코시티', 'Guadalajara': '과달라하라', 'Monterrey': '몬테레이',
        'Cancún': '칸쿤', 'Tijuana': '티후아나', 'Puebla': '푸에블라',
    }

    # 국가 → 대륙(한글) 매핑
    COUNTRY_CONTINENT_KR = {
        # 아시아
        'Afghanistan': '아시아', 'Azerbaijan': '아시아', 'Bahrain': '아시아',
        'Bangladesh': '아시아', 'Bhutan': '아시아', 'Brunei': '아시아',
        'Cambodia': '아시아', 'China': '아시아', 'Georgia': '아시아',
        'Hong Kong': '아시아', 'India': '아시아', 'Indonesia': '아시아',
        'Iran': '아시아', 'Israel': '아시아', 'Japan': '아시아',
        'Jordan': '아시아', 'Kazakhstan': '아시아', 'Kuwait': '아시아',
        'Kyrgyzstan': '아시아', "Lao People's Democratic Republic": '아시아',
        'Lebanon': '아시아', 'Macao': '아시아', 'Malaysia': '아시아',
        'Maldives': '아시아', 'Mongolia': '아시아', 'Myanmar': '아시아',
        'Nepal': '아시아', 'North Korea': '아시아', 'Oman': '아시아',
        'Pakistan': '아시아', 'Philippines': '아시아', 'Qatar': '아시아',
        'Saudi Arabia': '아시아', 'Singapore': '아시아', 'South Korea': '아시아',
        'Sri Lanka': '아시아', 'Syrian Arab Republic': '아시아',
        'Taiwan': '아시아', 'Tajikistan': '아시아', 'Thailand': '아시아',
        'Turkey': '아시아', 'United Arab Emirates': '아시아',
        'Uzbekistan': '아시아', 'Vietnam': '아시아',
        # 유럽
        'Albania': '유럽', 'Andorra': '유럽', 'Armenia': '유럽',
        'Austria': '유럽', 'Belarus': '유럽', 'Belgium': '유럽',
        'Bosnia and Herzegovina': '유럽', 'Bulgaria': '유럽',
        'Croatia': '유럽', 'Cyprus': '유럽', 'Czech Republic': '유럽',
        'Denmark': '유럽', 'Estonia': '유럽', 'Faroe Islands': '유럽',
        'Finland': '유럽', 'France': '유럽', 'Germany': '유럽',
        'Gibraltar': '유럽', 'Greece': '유럽', 'Holy See': '유럽',
        'Hungary': '유럽', 'Iceland': '유럽', 'Ireland': '유럽',
        'Isle of Man': '유럽', 'Italy': '유럽', 'Jersey': '유럽',
        'Latvia': '유럽', 'Liechtenstein': '유럽', 'Lithuania': '유럽',
        'Luxembourg': '유럽', 'Malta': '유럽', 'Moldova (Republic of)': '유럽',
        'Montenegro': '유럽', 'Netherlands': '유럽', 'North Macedonia': '유럽',
        'Norway': '유럽', 'Poland': '유럽', 'Portugal': '유럽',
        'Romania': '유럽', 'Russia': '유럽', 'Serbia': '유럽',
        'Slovakia': '유럽', 'Slovenia': '유럽', 'Spain': '유럽',
        'Sweden': '유럽', 'Switzerland': '유럽', 'Ukraine': '유럽',
        'United Kingdom': '유럽', 'Åland Islands': '유럽',
        # 북미
        'Aruba': '북미', 'Bahamas': '북미', 'Barbados': '북미',
        'Belize': '북미', 'Bermuda': '북미', 'Canada': '북미',
        'Cayman Islands': '북미', 'Costa Rica': '북미', 'Cuba': '북미',
        'Curaçao': '북미', 'Dominican Republic': '북미',
        'Guatemala': '북미', 'Jamaica': '북미', 'Martinique': '북미',
        'Mexico': '북미', 'Panama': '북미', 'Puerto Rico': '북미',
        'Trinidad and Tobago': '북미', 'Turks and Caicos Islands': '북미',
        'United States of America': '북미', 'Virgin Islands (British)': '북미',
        'Virgin Islands (U.S.)': '북미',
        'Antigua and Barbuda': '북미', 'Greenland': '북미',
        'Guam': '북미', 'Northern Mariana Islands': '북미',
        # 남미
        'Argentina': '남미', 'Bolivia': '남미', 'Brazil': '남미',
        'Chile': '남미', 'Colombia': '남미', 'Ecuador': '남미',
        'Paraguay': '남미', 'Peru': '남미', 'Uruguay': '남미',
        # 아프리카
        'Algeria': '아프리카', 'Angola': '아프리카', 'Botswana': '아프리카',
        'Cabo Verde': '아프리카', "Côte d'Ivoire": '아프리카',
        'Egypt': '아프리카', 'Ethiopia': '아프리카', 'Gabon': '아프리카',
        'Gambia': '아프리카', 'Ghana': '아프리카', 'Kenya': '아프리카',
        'Liberia': '아프리카', 'Madagascar': '아프리카', 'Malawi': '아프리카',
        'Mauritius': '아프리카', 'Morocco': '아프리카', 'Mozambique': '아프리카',
        'Namibia': '아프리카', 'Niger': '아프리카', 'Nigeria': '아프리카',
        'Rwanda': '아프리카', 'Réunion': '아프리카',
        'Sao Tome and Principe': '아프리카', 'Senegal': '아프리카',
        'Seychelles': '아프리카', 'Sierra Leone': '아프리카',
        'Somalia': '아프리카', 'South Africa': '아프리카',
        'Tanzania': '아프리카', 'Togo': '아프리카', 'Tunisia': '아프리카',
        'Uganda': '아프리카', 'Zambia': '아프리카', 'Zimbabwe': '아프리카',
        'Congo (Democratic Republic of the)': '아프리카',
        # 오세아니아
        'Australia': '오세아니아', 'Cook Islands': '오세아니아',
        'Fiji': '오세아니아', 'French Polynesia': '오세아니아',
        'New Zealand': '오세아니아', 'Samoa': '오세아니아',
        'Vanuatu': '오세아니아',
        # 남극
        'Antarctica': '남극',
        # 기타
        'Falkland Islands (Malvinas)': '남미',
    }

    @staticmethod
    def get_continent_kr(country: str) -> str:
        """국가명으로 한글 대륙명 반환"""
        return MarathonParser.COUNTRY_CONTINENT_KR.get(country, '')

    @staticmethod
    def translate_with_api(text: str) -> str:
        """
        MyMemory Translation API를 사용한 영어 → 한국어 번역
        무료, 빠르고 안정적
        """
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': 'en|ko'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                translated = data.get('responseData', {}).get('translatedText', text)

                # 번역 결과가 원본과 같거나 비어있으면 원본 유지
                if translated and translated != text:
                    return translated

            return text

        except Exception as e:
            # API 오류시 원본 유지
            return text

    @staticmethod
    def get_city_kr(city: str) -> str:
        """
        도시명을 한글로 변환
        1. CITY_KR 딕셔너리에서 매핑 확인
        2. 매핑 없으면 MyMemory Translation API로 번역
        3. API 실패시 원본 유지
        """
        if not city or not city.strip():
            return city

        # 1. 딕셔너리에서 매핑 확인
        if city in MarathonParser.CITY_KR:
            return MarathonParser.CITY_KR[city]

        # 2. 캐시에서 확인
        if city in MarathonParser._translation_cache:
            return MarathonParser._translation_cache[city]

        # 3. MyMemory Translation API로 번역
        translated = MarathonParser.translate_with_api(city)

        # 캐시에 저장
        MarathonParser._translation_cache[city] = translated

        # API 호출 간격 (너무 빠르게 호출하면 차단될 수 있음)
        time.sleep(0.1)

        return translated

    # 태그 한글 변환 (자연스러운 것만)
    TAG_KR = {
        # 참가자 수
        '0-99-participants': '100명 미만',
        '100-999-participants': '100~999명',
        '1000-4999-participants': '1,000~4,999명',
        '5000-9999-participants': '5,000~9,999명',
        '10000-24999-participants': '1만~2만5천명',
        '25000-499999-participants': '2만5천명 이상',
        '50000-∞-participants': '5만명 이상',
        # 지형/환경
        'city': '도시',
        'coastal': '해안',
        'countryside': '시골',
        'desert': '사막',
        'forest': '숲',
        'mountain': '산',
        'mountain-range': '산맥',
        'nature': '자연',
        'island': '섬',
        'jungle': '정글',
        'lake': '호수',
        'lakeside': '호숫가',
        'river': '강변',
        'valley': '계곡',
        'beach': '해변',
        'bay': '만',
        'sea': '바다',
        'ocean-view': '오션뷰',
        'park': '공원',
        'national-park': '국립공원',
        'state-park': '주립공원',
        'regional-park': '지역공원',
        'glacier': '빙하',
        'volcano': '화산',
        'canyon': '협곡',
        'cave': '동굴',
        'falls': '폭포',
        'waterfalls': '폭포',
        'pond': '연못',
        'bridge': '다리',
        'tunnel': '터널',
        'canal': '운하',
        'vineyards': '포도밭',
        'farms': '농장',
        'prairie': '초원',
        'savannah': '사바나',
        'rocks': '바위',
        'ice': '빙판',
        'snow': '눈',
        'sand': '모래',
        'grass': '잔디',
        'gravel': '자갈',
        'mud': '진흙',
        'polar': '극지',
        'lappland': '라플란드',
        # 코스 특성
        'flat': '평탄',
        'hilly': '언덕',
        'downhill': '내리막',
        'scenic': '경치가 좋아요',
        'picturesque': '풍경이 그림이에요',
        'historic': '역사적',
        'historical': '역사적',
        'ancient': '고대',
        'castle': '성',
        'architecture': '건축',
        'urban': '도심',
        'rural': '시골',
        'residential': '주택가',
        'sub-urban': '교외',
        'road': '도로',
        'trail': '트레일',
        'urban-trail': '도심 트레일',
        'single-track': '싱글트랙',
        'asphalt': '아스팔트',
        'track': '트랙',
        'indoor': '실내',
        'closed-road': '폐쇄도로',
        'out-and-back': '왕복 코스',
        'point-to-point': '편도 코스',
        'single-loop': '단일 루프',
        'mulitple-loops': '복수 루프',
        'road_ahoutu': '도로로 달려요',
        # 대회 특성
        'beginner-friendly' : '초보자 편해요',
        'family-friendly': '가족같아요',
        'fast': '기록용',
        'night': '야간',
        'winter': '겨울',
        'spring': '봄',
        'new-year': '새해',
        'new-years': '새해',
        'sunset': '일몰',
        'charity': '자선',
        'fund-raising': '모금',
        'nonprofit': '비영리',
        'fun': '펀런',
        'adventure': '어드벤처',
        'extreme': '극한',
        'challenge': '챌린지',
        'relay': '릴레이',
        'virtual-run': '버추얼 런',
        'walk': '워킹',
        'obstacle': '장애물',
        'colour-run': '컬러런',
        'halloween': '할로윈',
        'beer': '맥주',
        'wine': '와인',
        'music': '음악',
        'entertainment': '엔터테인먼트',
        'amusement': '놀이',
        'amusement-park': '놀이공원',
        'zoo': '동물원',
        'sport': '스포츠',
        'kids': '어린이',
        'kids-run': '어린이 달리기',
        'youth-run': '청소년 달리기',
        'women-only': '여성 전용',
        'men-only': '남성 전용',
        'wheelchair-friendly': '휠체어도 가능해요',
        'eco-friendly': '친환경',
        'certified': '공인',
        'invitation-only': '초청 전용',
        'package-tour': '패키지 투어',
        'team': '팀',
        'teams': '팀',
        'military': '군사',
        'green': '친환경',
        'natural': '자연',
        'wild-life': '야생동물',
        'wildlife': '야생동물',
        'capital': '수도',
        'resort': '리조트',
        'airport': '공항',
        'stadium': '경기장',
        'motor-speedway': '서킷',
        'school': '학교',
        'sport-club': '스포츠클럽',
        'skating': '스케이팅',
        'skydiving': '스카이다이빙',
        'triathlon': '트라이애슬론',
        'marathon': '마라톤',
        'half-marathon': '하프마라톤',
        'ultra': '울트라',
        'run': '달리기',
        'trailrun': '트레일러닝',
        'road-running': '로드러닝',
        # 인증/라벨 (자연스러운 것만)
        'boston-marathon-qualifier': '보스턴 마라톤 예선',
        'boston-qualifier': '보스턴 예선',
        'world-majors': '월드 메이저',
        'unesco': '유네스코',
        'unesco-world-heritage-site': '유네스코 세계유산',
        'aims-certified': 'AIMS 공인',
        'aims-member': 'AIMS 회원',
        'utmb-qualifier': 'UTMB 예선',
        'world-athletics-label': '세계육상연맹 라벨',
        'world-athletics-gold-label': '세계육상연맹 골드라벨',
        'world-athletics-platinum-label': '세계육상연맹 플래티넘라벨',
        'world-athletics-elite-Label': '세계육상연맹 엘리트라벨',
        'olympic-games-qualifier': '올림픽 예선',
        'commonwealth-games-qualifier': '커먼웰스 게임 예선',
    }

    @staticmethod
    def get_type_label(race_type: str) -> str:
        """대회 타입을 한글 라벨로 변환"""
        return MarathonParser.RACE_TYPE_KR.get(race_type, '기타')

    @staticmethod
    def get_country_kr(country: str) -> str:
        """국가명을 한글로 변환"""
        return MarathonParser.COUNTRY_KR.get(country, country)

    @staticmethod
    def get_surface_kr(surface: str) -> str:
        """노면 타입을 한글로 변환"""
        return MarathonParser.SURFACE_KR.get(surface, surface)

    @staticmethod
    def get_difficulty_kr(difficulty: str) -> str:
        """코스 난이도를 한글로 변환"""
        return MarathonParser.DIFFICULTY_KR.get(difficulty, difficulty)

    @staticmethod
    def get_tag_kr(tag: str) -> str:
        """태그를 한글로 변환 (매핑 없으면 원본 유지)"""
        return MarathonParser.TAG_KR.get(tag, tag)

    @staticmethod
    def estimate_participants(tags: List[Dict]) -> Optional[str]:
        """태그에서 참가자 수 추정"""
        for tag in tags:
            label = tag.get('label', '')
            if 'participants' in label:
                if '0-99' in label:
                    return '100명 미만'
                elif '100-999' in label:
                    return '100~999명'
                elif '1000-4999' in label:
                    return '1,000~4,999명'
                elif '5000-9999' in label:
                    return '5,000~9,999명'
                elif '10000-24999' in label:
                    return '1만~2만5천명'
                elif '25000' in label:
                    return '2만5천명 이상'
                elif '50000' in label:
                    return '5만명 이상'
        return None
    
    @staticmethod
    def parse_marathon(raw: Dict) -> Dict:
        """
        원본 API 데이터를 앱용 포맷으로 파싱
        필드 요약표 기준
        """
        
        # 오늘 이전 대회 필터링
        date_next_race = raw.get('dateNextRace', '')
        if date_next_race:
            try:
                race_date = datetime.fromisoformat(date_next_race)
                if race_date.date() < datetime.now().date():
                    return None
            except (ValueError, TypeError):
                pass

        # 필수 필드 (식별)
        marathon_id = raw.get('id', '')
        title = raw.get('title', '')

        # 필수 필드 (날짜)
        str_date_next_race = raw.get('strDateNextRace', '')
        str_date_weekday = raw.get('strDateRangeNextRaceWeekDay', '')
        
        # 필수 필드 (위치)
        city = raw.get('city', '')
        country = raw.get('country', '')
        country_code = raw.get('countryCode', '')
        start_point = raw.get('startPoint', [0, 0])
        
        # 필수 필드 (거리)
        race_type = raw.get('raceType', 'custom')
        distance = raw.get('distance', '')
        unique_distances = raw.get('uniqueDistances', [])
        
        # 필수 필드 (이미지)
        image = raw.get('image', '')
        image_small = raw.get('imageSmall', '')
        image_extra_small = raw.get('imageExtraSmall', '')
        
        # 필수 필드 (가격)
        min_price = raw.get('minPrice', 0)
        min_price_formatted = raw.get('minPriceFormatted', '')
        
        # 선택 필드 (코스)
        surface = raw.get('surface', '')
        course_difficulty = raw.get('courseDifficulty', '')
        
        # 필수 필드 (태그)
        tags = raw.get('tags', [])
        tag_labels = [tag.get('label', '') for tag in tags]
        
        # 필수 필드 (평점)
        rating = raw.get('rating', 0.0)
        reviews_count = raw.get('reviewsCount', 0)
        
        # 필수 필드 (링크)
        self_link = raw.get('selfLink', '')
        website = raw.get('website', '')
        
        # 필수 필드 (등록)
        register_possible = raw.get('registerPossible', False)
        is_sold_out = raw.get('isSoldOut', False)
        is_race_day_passed = raw.get('isRaceDayPassed', False)
        
        # 선택 필드 (날짜)
        first_race_date = raw.get('firstRaceDate', '')
        last_race_date = raw.get('lastRaceDate', '')
        
        # 선택 필드 (거리 상세)
        race_distances = raw.get('raceDistances', [])
        
        # 선택 필드 (가격)
        early_bird_days_left = raw.get('earlyBirdDaysLeft')
        
        # 파싱된 데이터 구성
        parsed = {
            # 식별 정보
            'id': marathon_id,
            'title': title,
            
            # 날짜 정보
            'dateNextRace': date_next_race,
            'strDateNextRace': str_date_next_race,
            'strDateRangeNextRaceWeekDay': str_date_weekday,
            'firstRaceDate': first_race_date,
            'lastRaceDate': last_race_date,
            
            # 위치 정보
            'city': MarathonParser.get_city_kr(city),
            'country': MarathonParser.get_country_kr(country),
            'countryCode': country_code,
            'location': f"{MarathonParser.get_city_kr(city)}, {MarathonParser.get_country_kr(country)}" if city and country else MarathonParser.get_city_kr(city) or MarathonParser.get_country_kr(country),
            'continent': MarathonParser.get_continent_kr(country),
            'startPoint': start_point,
            'coordinates': {
                'latitude': start_point[1] if len(start_point) > 1 else 0,
                'longitude': start_point[0] if len(start_point) > 0 else 0
            },
            
            # 거리 정보
            'raceType': race_type,
            'raceTypeLabel': MarathonParser.get_type_label(race_type),
            'distance': distance,
            'uniqueDistances': unique_distances,
            'raceDistances': race_distances,
            'mainDistance': unique_distances[0] if unique_distances else distance,
            
            # 이미지
            'image': image,
            'imageSmall': image_small,
            'imageExtraSmall': image_extra_small,
            'thumbnail': image_small or image_extra_small or image,
            
            # 가격
            'minPrice': round(int(min_price * 1450), -2) if min_price else 0,
            'minPriceFormatted': f"약 {round(int(min_price * 1450), -2):,}원" if min_price else '',
            'earlyBirdDaysLeft': early_bird_days_left,
            'hasEarlyBird': early_bird_days_left is not None and early_bird_days_left > 0,
            
            # 코스
            'surface': MarathonParser.get_surface_kr(surface),
            'courseDifficulty': MarathonParser.get_difficulty_kr(course_difficulty),

            # 태그
            'tags': [MarathonParser.get_tag_kr(t) for t in tag_labels],
            'participantsEstimate': MarathonParser.estimate_participants(tags),
            
            # 평점
            'rating': rating,
            'reviewsCount': reviews_count,
            'hasReviews': reviews_count > 0,
            
            # 링크
            'selfLink': self_link,
            'website': website,
            
            # 등록 상태
            'registerPossible': register_possible,
            'isSoldOut': is_sold_out,
            'isRaceDayPassed': is_race_day_passed,
            'isAvailable': register_possible and not is_sold_out and not is_race_day_passed,
            
            # 추가 편의 필드
            'isPremium': 'premium' in tag_labels or 'boston-marathon-qualifier' in tag_labels,
            'isBeginnerFriendly': 'beginner-friendly' in tag_labels,
            'isScenic': 'scenic' in tag_labels or 'nature' in tag_labels,
        }
        
        return parsed


def fetch_marathon_data():
    """마라톤 데이터 가져오기 및 파싱 (API 1000개 제한 우회)"""

    url = "https://worldsmarathons.com/api/search"
    base_params = {
        "sport": "running",
        "all": "true",
        "currency": "EUR"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://worldsmarathons.com/",
        "Accept": "application/json"
    }

    all_raw = {}  # id -> raw data (중복 제거용)

    def fetch_and_add(extra_params, label):
        """API 요청 후 결과를 all_raw에 추가, 중복 제거"""
        params = {**base_params, **extra_params}
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"  ⚠️  {label}: HTTP {resp.status_code}")
            return []
        data = resp.json()
        results = data.get('results', [])
        api_count = data.get('count', 0)
        new = 0
        for r in results:
            rid = r.get('id', '')
            if rid and rid not in all_raw:
                all_raw[rid] = r
                new += 1
        print(f"  {label}: 총{api_count}개 중 {len(results)}개 수신, 신규 {new}개 (누적 {len(all_raw)}개)")
        time.sleep(0.3)
        return results

    print("=" * 70)
    print("🏃 World's Marathons 전체 데이터 수집 시작")
    print("=" * 70)

    try:
        # Phase 1: 소규모 대륙 (각 1000개 이하 → 전체 수신 가능)
        print("\n📡 Phase 1: 소규모 대륙")
        for cont in ['asia', 'africa', 'South America', 'australia', 'Antarctica']:
            fetch_and_add({'continent': cont}, cont)

        # Phase 2: 유럽 - raceType별 분할 (half_marathon만 1211개로 초과)
        print("\n📡 Phase 2: 유럽 (raceType별)")
        eu_countries = set()
        for rt in ['full_marathon', 'ultra_marathon', 'custom']:
            results = fetch_and_add({'continent': 'europe', 'raceType': rt}, f'europe/{rt}')
            for r in results:
                c = r.get('country', '')
                if c:
                    eu_countries.add(c)

        # 유럽 half_marathon: 1211개 > 1000 제한 → 국가별 분할
        print("\n📡 Phase 3: 유럽 half_marathon (국가별)")
        seed = fetch_and_add({'continent': 'europe', 'raceType': 'half_marathon'}, 'europe/half(seed)')
        for r in seed:
            c = r.get('country', '')
            if c:
                eu_countries.add(c)
        for country in sorted(eu_countries):
            fetch_and_add({'country': country, 'raceType': 'half_marathon'}, f'  {country}/half')

        # Phase 4: 북미 - raceType별 분할 (각각 1000 이하)
        print("\n📡 Phase 4: 북미 (raceType별)")
        na_countries = set()
        for rt in ['full_marathon', 'half_marathon', 'ultra_marathon', 'custom']:
            results = fetch_and_add({'continent': 'North America', 'raceType': rt}, f'NA/{rt}')
            for r in results:
                c = r.get('country', '')
                if c:
                    na_countries.add(c)

        # Phase 5: 북미 국가별 개별 쿼리 (누락분 보충)
        print("\n📡 Phase 5: 북미 국가별")
        for country in sorted(na_countries):
            fetch_and_add({'country': country}, f'  {country}')

        # Phase 6: 유럽 국가별 전체 쿼리 (raceType 없이, 누락분 보충)
        print("\n📡 Phase 6: 유럽 국가별 (전체)")
        for country in sorted(eu_countries):
            fetch_and_add({'country': country}, f'  {country}')

        # Phase 7: 기본 쿼리로 누락분 보충
        print("\n📡 Phase 7: 기본 쿼리 (누락분 보충)")
        fetch_and_add({}, 'catch-all')
        # 누락된 대륙/지역 추가 시도
        for cont in ['Oceania', 'Central America', 'Middle East']:
            fetch_and_add({'continent': cont}, f'  {cont}')

        all_results = list(all_raw.values())
        print(f"\n📊 최종 수집: {len(all_results)}개 (중복 제거 완료)")

        if not all_results:
            print("⚠️  결과 데이터가 비어있습니다.")
            return []

        # 원본 데이터 저장
        print("\n💾 원본 데이터 저장 중...")
        import os
        os.makedirs('data', exist_ok=True)
        raw_output = {'count': len(all_results), 'results': all_results}
        with open("data/marathons_global_raw.json", "w", encoding="utf-8") as f:
            json.dump(raw_output, f, ensure_ascii=False, indent=2)
        print(f"✅ data/marathons_global_raw.json 저장 완료 ({len(all_results)}개)")

        # 파싱
        print("\n🔄 데이터 파싱 중...")
        parsed_marathons = []
        for i, raw_marathon in enumerate(all_results, 1):
            try:
                parsed = MarathonParser.parse_marathon(raw_marathon)
                if parsed is None:
                    continue
                parsed_marathons.append(parsed)
                if i % 500 == 0:
                    print(f"   처리 중... {i}/{len(all_results)}")
            except Exception as e:
                print(f"   ⚠️  {i}번째 마라톤 파싱 실패: {e}")
                continue
        print(f"✅ 파싱 완료: {len(parsed_marathons)}개")

        # 파싱된 데이터 저장
        print("\n💾 파싱된 데이터 저장 중...")
        output = {
            'metadata': {
                'total_count': len(parsed_marathons),
                'parsed_count': len(parsed_marathons),
                'fetched_at': datetime.now().isoformat(),
                'api_url': url,
                'currency': base_params.get('currency', 'EUR')
            },
            'marathons': parsed_marathons
        }
        with open("data/marathons_global.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"✅ data/marathons_global.json 저장 완료")

        # 통계 출력
        print_statistics(parsed_marathons)

        # 샘플 데이터 출력
        print_samples(parsed_marathons)

        return parsed_marathons

    except requests.exceptions.Timeout:
        print("❌ 요청 타임아웃")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return []
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return []


def print_statistics(marathons: List[Dict]):
    """데이터 통계 출력"""
    print("\n" + "=" * 70)
    print("📈 데이터 통계")
    print("=" * 70)
    
    # 타입별 개수
    type_counts = {}
    for m in marathons:
        type_label = m.get('raceTypeLabel', '기타')
        type_counts[type_label] = type_counts.get(type_label, 0) + 1
    
    print("\n🏃 대회 타입별:")
    for type_label, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {type_label}: {count}개")
    
    # 국가별 개수 (상위 10개)
    country_counts = {}
    for m in marathons:
        country = m.get('country', '미상')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    print("\n🌍 국가별 (상위 10개):")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {country}: {count}개")
    
    # 노면 타입별
    surface_counts = {}
    for m in marathons:
        surface = m.get('surface', '미상')
        if surface:
            surface_counts[surface] = surface_counts.get(surface, 0) + 1
    
    print("\n🛣️  노면 타입별:")
    for surface, count in sorted(surface_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {surface}: {count}개")
    
    # 등록 가능 여부
    available = sum(1 for m in marathons if m.get('isAvailable'))
    sold_out = sum(1 for m in marathons if m.get('isSoldOut'))
    passed = sum(1 for m in marathons if m.get('isRaceDayPassed'))
    
    print("\n📝 등록 상태:")
    print(f"  등록 가능: {available}개")
    print(f"  매진: {sold_out}개")
    print(f"  종료: {passed}개")
    
    # 평점
    with_reviews = [m for m in marathons if m.get('hasReviews')]
    if with_reviews:
        avg_rating = sum(m.get('rating', 0) for m in with_reviews) / len(with_reviews)
        print(f"\n⭐ 평점:")
        print(f"  리뷰 있는 대회: {len(with_reviews)}개")
        print(f"  평균 평점: {avg_rating:.2f}/5.0")
    
    # 가격
    with_price = [m for m in marathons if m.get('minPrice', 0) > 0]
    if with_price:
        prices = [m.get('minPrice', 0) for m in with_price]
        print(f"\n💰 가격:")
        print(f"  가격 정보 있음: {len(with_price)}개")
        print(f"  최저가: {min(prices):.2f} EUR")
        print(f"  최고가: {max(prices):.2f} EUR")
        print(f"  평균가: {sum(prices)/len(prices):.2f} EUR")


def print_samples(marathons: List[Dict]):
    """샘플 데이터 출력"""
    print("\n" + "=" * 70)
    print("📋 샘플 데이터 (처음 3개)")
    print("=" * 70)
    
    for i, marathon in enumerate(marathons[:3], 1):
        print(f"\n{i}. {marathon.get('title', 'N/A')}")
        print(f"   ID: {marathon.get('id', 'N/A')}")
        print(f"   위치: {marathon.get('location', 'N/A')}")
        print(f"   날짜: {marathon.get('strDateRangeNextRaceWeekDay', 'N/A')}")
        print(f"   타입: {marathon.get('raceTypeLabel', 'N/A')}")
        print(f"   거리: {marathon.get('mainDistance', 'N/A')}")
        print(f"   가격: {marathon.get('minPriceFormatted', 'N/A')}")
        print(f"   평점: {marathon.get('rating', 0)}/5.0 ({marathon.get('reviewsCount', 0)} 리뷰)")
        print(f"   등록: {'✅ 가능' if marathon.get('isAvailable') else '❌ 불가'}")
        print(f"   태그: {', '.join(marathon.get('tags', [])[:5])}")


if __name__ == "__main__":
    marathons = fetch_marathon_data()

    if marathons:
        print("\n" + "=" * 70)
        print("✅ 크롤링 완료!")
        print("=" * 70)
        print(f"\n저장된 파일:")
        print(f"  1. data/marathons_global_raw.json - 원본 API 응답")
        print(f"  2. data/marathons_global.json - 파싱된 데이터")
        print(f"\n총 {len(marathons)}개의 마라톤 데이터 수집 완료! 🎉")

        # visa 데이터 자동 병합
        print("\n" + "=" * 70)
        print("🌍 비자 데이터 병합 시작")
        print("=" * 70)
        try:
            import subprocess

            # visa 데이터 병합 실행
            print("\n비자 정보 추가 중...")
            result = subprocess.run(
                ['python3', 'merge_visa_data.py', 'marathons_global_raw.json'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"⚠️  비자 데이터 병합 중 오류 발생:\n{result.stderr}")

            result = subprocess.run(
                ['python3', 'merge_visa_data.py', 'marathons_global.json'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"⚠️  비자 데이터 병합 중 오류 발생:\n{result.stderr}")

            print("\n" + "=" * 70)
            print("✅ 모든 작업 완료!")
            print("=" * 70)

        except Exception as e:
            print(f"\n⚠️  비자 데이터 병합 중 오류 발생: {e}")
            print("수동으로 merge_visa_data.py를 실행해주세요.")
    else:
        print("\n❌ 데이터 수집 실패")