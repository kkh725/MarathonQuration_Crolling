# Marathon Crawler

해외/국내 마라톤 대회 정보를 크롤링하여 JSON으로 저장하는 스크립트 모음입니다.

## 구조

| 파일 | 설명 | 출력 |
|------|------|------|
| `crawl_global.py` | World's Marathons API 해외 대회 수집 | `marathons_global_raw.json`, `marathons_global_parsed.json` |
| `crawl_korea.py` | 마라톤온라인(roadrun.co.kr) 국내 대회 크롤링 | `marathons_korea.json` |

## crawl_global.py (해외)

- World's Marathons API에서 전 세계 마라톤 데이터 수집 (약 5,000개)
- API 1,000개 제한을 대륙/국가/종목별 분할 쿼리로 우회
- 국가명, 노면, 난이도, 태그 등 한글 변환
- EUR → KRW 환율 적용 (1,450원, 백원 단위 반올림)
- 오늘 이전 대회 자동 필터링
- 대륙 정보 자동 매핑

## crawl_korea.py (국내)

- 마라톤온라인 목록 + 상세페이지 파싱
- 대회 홈페이지에서 대표 이미지 자동 추출
- 참가비 자동 추출 (상세페이지 기타소개에서)
- 접수기간 시작/종료일 분리 (registrationStartDate, registrationEndDate)
- 종목 필터링 (풀, 하프, 10km, 5km만 유지)
- 오늘 이전 대회 자동 필터링

## 요구사항

- Python 3.9+
- requests
- beautifulsoup4

## 설치

```bash
python -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4
```

## 실행

```bash
# 해외 대회
python crawl_global.py

# 국내 대회
python crawl_korea.py
```
