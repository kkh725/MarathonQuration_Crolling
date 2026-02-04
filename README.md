# AIMS Marathon Calendar Crawler

[AIMS World Running](https://aims-worldrunning.org/calendar.html) 캘린더 페이지에서 국제 마라톤 대회 일정을 크롤링하여 JSON 파일로 저장하는 Python 스크립트입니다.

## 수집 항목

| 필드 | 설명 |
|------|------|
| `event_name` | 대회명 |
| `start_date` | 시작일 (YYYY-MM-DD) |
| `end_date` | 종료일 (YYYY-MM-DD) |
| `country_code` | 국가 코드 |
| `city` | 도시 (현재 미지원) |
| `distances` | 거리 종류 (FULL, HALF, 10K, ULTRA) |
| `aims_url` | AIMS 상세 페이지 URL |

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
python main.py
```

실행 후 `aims_marathons.json` 파일이 생성됩니다.

## 출력 예시

```json
{
  "source": "aims-worldrunning.org",
  "updated_at": "2026-02-04T05:29:00.000000Z",
  "events": [
    {
      "event_name": "Example Marathon",
      "start_date": "2026-03-15",
      "end_date": "2026-03-15",
      "country_code": "KOR",
      "city": null,
      "distances": ["FULL", "HALF"],
      "aims_url": "https://aims-worldrunning.org/..."
    }
  ]
}
```
