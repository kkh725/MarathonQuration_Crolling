#!/usr/bin/env python3
"""
마라톤온라인(marathon.pe.kr) 국내 마라톤 대회 크롤링
목록 + 상세페이지 → marathons_korea.json
"""

import requests
import json
import re
import time
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup


BASE_URL = "http://www.roadrun.co.kr/schedule"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def fetch_html(url):
    """EUC-KR 페이지를 UTF-8 문자열로 반환"""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.encoding = "euc-kr"
    return resp.text


def parse_list_page():
    """목록 페이지에서 대회 기본 정보 + ID 추출"""
    html = fetch_html(f"{BASE_URL}/list.php")
    soup = BeautifulSoup(html, "html.parser")

    events = []
    seen_ids = set()

    # view.php?no=XXXXX 링크에서 ID와 대회명 추출
    for a_tag in soup.find_all("a", href=re.compile(r"view\.php\?no=\d+")):
        href = a_tag["href"]
        m = re.search(r"no=(\d+)", href)
        if not m:
            continue
        eid = m.group(1)
        if eid in seen_ids:
            continue
        seen_ids.add(eid)

        title = a_tag.get_text(strip=True)
        if not title:
            continue

        # 종목: 대회명 바로 다음 <font size="2" color="#990000">
        distances = ""
        next_font = a_tag.find_next("font", attrs={"color": "#990000"})
        if next_font:
            distances = next_font.get_text(strip=True)

        # 날짜: 이 행 위쪽의 날짜 셀 (M/D 형식)
        tr = a_tag.find_parent("tr")
        date_str = ""
        day_of_week = ""
        if tr:
            # 같은 tr 내 첫 td에 날짜가 있거나, 이전 tr에 있음
            date_td = tr.find("td", width="18%")
            if date_td:
                date_text = date_td.get_text(strip=True)
                dm = re.search(r"(\d{1,2}/\d{1,2})", date_text)
                if dm:
                    date_str = dm.group(1)
                dw = re.search(r"\((.)\)", date_text)
                if dw:
                    day_of_week = dw.group(1)

        # 장소: width="19%" td
        location = ""
        if tr:
            loc_td = tr.find("td", width="19%")
            if loc_td:
                location = loc_td.get_text(strip=True)

        # 주최 / 전화: width="30%" td
        organizer = ""
        phone = ""
        if tr:
            org_td = tr.find("td", width="30%")
            if org_td:
                org_text = org_td.get_text(" ", strip=True)
                # 전화번호 추출
                pm = re.search(r"☎?([\d\-]+)", org_text)
                if pm:
                    phone = pm.group(1)
                # 주최: 전화 앞 텍스트
                org_parts = org_text.split("☎")[0].strip()
                if org_parts:
                    organizer = org_parts

        # 홈페이지 링크
        website = ""
        if tr:
            home_a = tr.find("a", href=re.compile(r"^http"), target="_new")
            if home_a:
                website = home_a["href"]

        events.append({
            "id": eid,
            "title": title,
            "date": date_str,
            "dayOfWeek": day_of_week,
            "distances": distances,
            "location": location,
            "organizer": organizer,
            "phone": phone,
            "website": website,
        })

    return events


def parse_detail_page(eid):
    """상세 페이지에서 추가 정보 추출"""
    html = fetch_html(f"{BASE_URL}/view.php?no={eid}")
    soup = BeautifulSoup(html, "html.parser")

    detail = {}
    field_map = {
        "대회명": "title",
        "대표자명": "representative",
        "E-mail": "email",
        "대회일시": "datetime",
        "전화번호": "phone",
        "대회종목": "distances",
        "대회지역": "region",
        "대회장소": "venue",
        "주최단체": "organizer",
        "접수기간": "registrationPeriod",
        "홈페이지": "website",
        "기타소개": "description",
    }

    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        label = cells[0].get_text(strip=True)
        if label in field_map:
            key = field_map[label]
            if key == "description":
                # HTML 줄바꿈 보존
                value = cells[1].decode_contents()
                value = re.sub(r"<br\s*/?>", "\n", value)
                value = re.sub(r"<[^>]+>", "", value)
                value = re.sub(r"&nbsp;", " ", value)
                value = value.strip()
            elif key == "website":
                a = cells[1].find("a", href=True)
                value = a["href"] if a else cells[1].get_text(strip=True)
            elif key == "email":
                a = cells[1].find("a", href=True)
                if a:
                    em = re.search(r"mail_url=([^'\"&]+)", a.get("href", ""))
                    value = em.group(1) if em else cells[1].get_text(strip=True)
                else:
                    value = cells[1].get_text(strip=True)
            else:
                value = cells[1].get_text(strip=True)
            detail[key] = value

    # 기타소개에서 가격 추출
    desc = detail.get("description", "")
    if desc:
        # "참가비" 주변 금액 우선 탐색
        price_section = re.search(r"참가비[^\d]{0,30}([\d,]+)\s*원", desc)
        if price_section:
            detail["price"] = price_section.group(1).replace(",", "") + "원"
        else:
            # 그 외 "XX,XXX원" 패턴 중 첫 번째
            price_match = re.search(r"([\d,]+)\s*원", desc)
            if price_match:
                raw_price = price_match.group(1).replace(",", "")
                # 너무 큰 수(날짜 등 오탐)나 너무 작은 수 제외
                if raw_price.isdigit() and 1000 <= int(raw_price) <= 1000000:
                    detail["price"] = raw_price + "원"

    return detail


def is_image_url(url):
    """URL이 이미지 파일 확장자인지 확인"""
    return bool(re.search(r"\.(jpg|jpeg|png|webp|gif|bmp|svg)(\?|$|#)", url, re.I))


def fetch_hero_image(website_url):
    """대회 홈페이지에서 대표 이미지 URL 추출 (이미지 파일만, main 우선)"""
    if not website_url:
        return ""
    try:
        resp = requests.get(website_url, headers=HEADERS, timeout=10, allow_redirects=True)
        resp.encoding = resp.apparent_encoding
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # 페이지 내 모든 이미지 URL 수집
        all_images = []

        # og:image
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            all_images.append(urljoin(website_url, og["content"]))

        # twitter:image
        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            all_images.append(urljoin(website_url, tw["content"]))

        # CSS background-image
        for tag in soup.find_all(style=re.compile(r"background(-image)?\s*:")):
            style = tag.get("style", "")
            bg = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", style)
            if bg:
                all_images.append(urljoin(website_url, bg.group(1)))

        # <img> 태그
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if re.search(r"(icon|btn|button|arrow|sprite|pixel|spacer|1x1|blank)", src, re.I):
                continue
            all_images.append(urljoin(website_url, src))

        # 이미지 확장자 필터
        all_images = [url for url in all_images if is_image_url(url)]
        if not all_images:
            return ""

        # "main"이 포함된 이미지 우선
        banners = [url for url in all_images if re.search(r"banner", url, re.I)]
        mains = [url for url in all_images if re.search(r"main", url, re.I)]
        logos = [url for url in all_images if re.search(r"logo", url, re.I)]

        main_images = banners + mains + logos

        if main_images:
            return main_images[0]

        # 그 외 첫 번째 이미지
        return all_images[0]

    except Exception:
        return ""


ALLOWED_DISTANCES = {"풀", "하프", "10km", "5km"}


def filter_distances(distances_str):
    """허용된 종목(풀, 하프, 10km, 5km)만 남기고 나머지 제거"""
    if not distances_str:
        return ""
    parts = [d.strip() for d in distances_str.split(",")]
    filtered = [d for d in parts if d in ALLOWED_DISTANCES]
    return ",".join(filtered)


def normalize_date(date_str, year=2026):
    """'2/8' 또는 '2026년2월8일' → '2026-02-08'"""
    # 목록 페이지 형식: M/D
    m = re.match(r"(\d{1,2})/(\d{1,2})", date_str)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        return f"{year}-{month:02d}-{day:02d}"

    # 상세 페이지 형식: YYYY년M월D일
    m = re.match(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", date_str)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    return date_str


def parse_registration_dates(period_str):
    """'2025년10월28일~2026년2월1일' → ('2025-10-28', '2026-02-01')"""
    if not period_str:
        return ("", "")
    parts = period_str.split("~")
    if len(parts) != 2:
        return (period_str, "")
    start = normalize_date(parts[0].strip())
    end = normalize_date(parts[1].strip())
    return (start, end)


def main():
    print("=" * 60)
    print("🏃 마라톤온라인 국내 대회 크롤링 시작")
    print("=" * 60)

    # 1) 목록 파싱
    print("\n📡 목록 페이지 파싱 중...")
    events = parse_list_page()
    print(f"   {len(events)}개 대회 발견")

    # 2) 오늘 이전 대회 제외
    today = datetime.now().strftime("%Y-%m-%d")
    filtered = []
    for ev in events:
        d = normalize_date(ev["date"])
        if d >= today:
            ev["dateFormatted"] = d
            filtered.append(ev)
    print(f"   오늘({today}) 이후 대회: {len(filtered)}개")

    # 3) 상세 페이지 크롤링
    print(f"\n📡 상세 페이지 크롤링 중... (총 {len(filtered)}개)")
    results = []
    for i, ev in enumerate(filtered, 1):
        try:
            detail = parse_detail_page(ev["id"])
            time.sleep(0.3)

            # 상세에서 날짜 정규화
            dt_raw = detail.get("datetime", "")
            start_time = ""
            tm = re.search(r"출발시간:\s*(\d{1,2}:\d{2})", dt_raw)
            if tm:
                start_time = tm.group(1)

            # 홈페이지에서 대표 이미지 추출
            site_url = detail.get("website", ev["website"])
            image = ""
            if site_url:
                image = fetch_hero_image(site_url)
                time.sleep(0.3)

            merged = {
                "id": ev["id"],
                "title": detail.get("title", ev["title"]),
                "date": ev.get("dateFormatted", ev["date"]),
                "dayOfWeek": ev["dayOfWeek"],
                "startTime": start_time,
                "distances": filter_distances(detail.get("distances", ev["distances"])),
                "region": detail.get("region", ""),
                "venue": detail.get("venue", ev["location"]),
                "organizer": detail.get("organizer", ev["organizer"]),
                "representative": detail.get("representative", ""),
                "phone": detail.get("phone", ev["phone"]),
                "email": detail.get("email", ""),
                "website": site_url,
                "registrationStartDate": parse_registration_dates(detail.get("registrationPeriod", ""))[0],
                "registrationEndDate": parse_registration_dates(detail.get("registrationPeriod", ""))[1],
                "price": detail.get("price", ""),
                "description": detail.get("description", ""),
                "image": image,
            }
            results.append(merged)

            if i % 10 == 0:
                print(f"   {i}/{len(filtered)} 완료")

        except Exception as e:
            print(f"   ⚠️ {ev['id']} ({ev['title']}) 실패: {e}")
            continue

    print(f"✅ 크롤링 완료: {len(results)}개")

    # 4) 저장
    output = {
        "metadata": {
            "total_count": len(results),
            "fetched_at": datetime.now().isoformat(),
            "source": "http://www.marathon.pe.kr/index_calendar.html",
        },
        "marathons": results,
    }

    with open("marathons_korea.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 marathons_korea.json 저장 완료 ({len(results)}개)")

    # 샘플 출력
    print("\n📋 샘플 (처음 3개):")
    for i, m in enumerate(results[:3], 1):
        print(f"\n{i}. {m['title']}")
        print(f"   날짜: {m['date']} ({m['dayOfWeek']}) {m['startTime']}")
        print(f"   종목: {m['distances']}")
        print(f"   장소: {m['venue']}")
        print(f"   주최: {m['organizer']}")
        print(f"   홈페이지: {m['website']}")
        print(f"   이미지: {m['image']}")


if __name__ == "__main__":
    main()
