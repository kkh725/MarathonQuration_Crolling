import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

URL = "https://aims-worldrunning.org/calendar.html"
HEADERS = {
    "User-Agent": "MarathonCrawler/1.0 (contact@example.com)"
}

DISTANCE_MAP = {
    "M": "FULL",
    "H": "HALF",
    "R": "10K",
    "U": "ULTRA"
}

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

def parse_distances(raw):
    distances = []
    for key in raw.replace(" ", "").split(","):
        if key in DISTANCE_MAP:
            distances.append(DISTANCE_MAP[key])
    return list(set(distances))

def crawl_aims_calendar():
    res = requests.get(URL, headers=HEADERS, timeout=10)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    events = []
    current_month = None
    current_year = None

    elements = soup.select(".calendar-month-header, .calendar-item")

    for el in elements:
        classes = el.get("class", [])

        # 월 헤더 처리: "January 2026" 형태
        if "calendar-month-header" in classes:
            text = el.get_text(strip=True)
            parts = text.split()
            if len(parts) == 2 and parts[0] in MONTH_MAP:
                current_month = MONTH_MAP[parts[0]]
                current_year = int(parts[1])
            continue

        if current_month is None or current_year is None:
            continue

        # 날짜 추출
        date_el = el.select_one(".calendar-date")
        if not date_el:
            continue

        date_text = date_el.get_text(strip=True)

        # tbc 날짜는 스킵
        if date_text.lower() == "tbc":
            start_date = None
            end_date = None
        else:
            # en-dash(U+2013) 또는 하이픈으로 분리된 다일 이벤트 처리
            day_parts = re.split(r"[\u2013\-]", date_text)
            start_day = int(day_parts[0].strip())
            end_day = int(day_parts[-1].strip())
            start_date = f"{current_year}-{current_month:02d}-{start_day:02d}"
            end_date = f"{current_year}-{current_month:02d}-{end_day:02d}"

        # 이벤트명 & URL
        race_link = el.select_one(".calendar-race-name a")
        event_name = race_link.get_text(strip=True) if race_link else None
        aims_url = race_link.get("href") if race_link else None

        # 국가코드
        cc_el = el.select_one(".calendar-country-code")
        country_code = cc_el.get_text(strip=True) if cc_el else None

        # 거리 정보
        supinfo = el.select_one(".calendar-supinfo")
        distances = []
        if supinfo:
            full_text = supinfo.get_text(strip=True)
            cc_text = country_code or ""
            distance_raw = full_text.replace(cc_text, "", 1).strip()
            distances = parse_distances(distance_raw)

        event = {
            "event_name": event_name,
            "start_date": start_date,
            "end_date": end_date,
            "country_code": country_code,
            "city": None,
            "distances": distances,
            "aims_url": aims_url
        }

        events.append(event)

    return {
        "source": "aims-worldrunning.org",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "events": events
    }

if __name__ == "__main__":
    data = crawl_aims_calendar()
    with open("aims_marathons.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
