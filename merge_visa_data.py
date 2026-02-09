#!/usr/bin/env python3
"""
마라톤 데이터에 비자 정보를 추가하는 스크립트
"""
import json
import re
import sys
import time

def parse_visa_period(gnrl_pspt_visa_cn):
    """
    비자 기간 텍스트를 파싱하여 숫자로 변환

    Args:
        gnrl_pspt_visa_cn: 비자 정보 텍스트

    Returns:
        int or None: 비자 없이 체류 가능한 일수, 비자 필요시 None
    """
    if not gnrl_pspt_visa_cn or gnrl_pspt_visa_cn.strip() == "":
        return None

    # "X"인 경우 또는 "X"로 시작하는 경우 비자 필요
    if gnrl_pspt_visa_cn.strip().upper().startswith("X"):
        return None

    text = gnrl_pspt_visa_cn

    # "N일 중 M일" 또는 "N개월중 M일" 패턴 감지 (쉥겐 협정 등)
    # 예: "180일 중 90일" -> 90일, "6개월중 누적 90일" -> 90일
    if ('중' in text or '이내' in text) and '일' in text:
        numbers = re.findall(r'(\d+)일', text)
        if len(numbers) >= 2:
            # 마지막 숫자가 실제 체류 가능 일수
            last_number = re.search(r'(\d+)', numbers[-1])
            if last_number:
                return int(last_number.group(1))
        elif len(numbers) == 1:
            # "6개월중 90일" 같은 패턴
            day_match = re.search(r'(\d+)', numbers[0])
            if day_match:
                return int(day_match.group(1))

    # "N개월" 패턴을 일수로 변환 (단독으로 나올 때만)
    # 예: "6개월" -> 180일
    month_match = re.search(r'(\d+)\s*개월', text)
    if month_match and '일' not in text:
        months = int(month_match.group(1))
        return months * 30  # 1개월 = 30일로 근사

    # 숫자 추출 (일반 케이스)
    numbers = re.findall(r'\d+', text)

    if not numbers:
        return None

    # 숫자를 정수로 변환하고 필터링
    numbers = [int(n) for n in numbers]

    # 너무 작은 숫자(1~5) 제거 (에러 가능성)
    numbers = [n for n in numbers if n > 5]

    if not numbers:
        return None

    # 복수 숫자인 경우
    if len(numbers) >= 2:
        # 일반적으로 30, 60, 90, 180 등이 체류 기간
        # 가장 흔한 체류 기간 숫자 우선 선택
        common_periods = [30, 60, 90, 180]
        for period in common_periods:
            if period in numbers:
                return period

        # 그 외엔 중간값 사용
        numbers.sort()
        return numbers[len(numbers) // 2]

    # 단일 숫자인 경우
    return numbers[0]

def main():
    # 커맨드 라인 인자로 파일 이름 받기
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'marathons_global.json'

    # 파일 경로 설정
    data_dir = 'data'
    input_file = f'{data_dir}/{filename}'
    visa_file = f'{data_dir}/visa.json'
    output_file = f'{data_dir}/{filename}'

    start_time = time.time()

    print(f"마라톤 데이터 로딩 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        marathons_json = json.load(f)

    # 파일 구조에 따라 다르게 처리
    if 'marathons' in marathons_json:
        # marathons_global.json 구조
        marathons_data = marathons_json.get('marathons', [])
        metadata = marathons_json.get('metadata', {})
        structure_type = 'marathons'
    elif 'results' in marathons_json:
        # marathons_global_raw.json 구조
        marathons_data = marathons_json.get('results', [])
        structure_type = 'results'
    else:
        print("오류: 알 수 없는 파일 구조입니다.")
        return

    print(f"총 {len(marathons_data)}개의 마라톤 데이터 로딩됨")

    print("비자 데이터 로딩 중...")
    with open(visa_file, 'r', encoding='utf-8') as f:
        visa_json = json.load(f)

    # visa.json에서 실제 데이터 추출
    visa_data = visa_json.get('response', {}).get('body', {}).get('items', {}).get('item', [])

    # visa.json을 country_iso_alp2를 키로 하는 딕셔너리로 변환
    print("비자 데이터 인덱싱 중...")
    visa_dict = {}
    for entry in visa_data:
        country_code = entry.get('country_iso_alp2')
        if country_code:
            visa_dict[country_code.upper()] = entry

    print(f"총 {len(visa_dict)}개 국가의 비자 정보 로딩됨")

    # 마라톤 데이터 처리
    print("\n마라톤 데이터에 비자 정보 추가 중...")
    matched_count = 0
    unmatched_count = 0
    unmatched_countries = set()

    for marathon in marathons_data:
        country_code = marathon.get('countryCode')

        if not country_code:
            marathon['visa'] = None
            unmatched_count += 1
            continue

        # 국가 코드를 대문자로 변환하여 매칭
        country_code_upper = country_code.upper()

        if country_code_upper in visa_dict:
            visa_info = visa_dict[country_code_upper]
            gnrl_pspt_visa_cn = visa_info.get('gnrl_pspt_visa_cn', '')

            # 비자 기간 파싱
            visa_days = parse_visa_period(gnrl_pspt_visa_cn)
            marathon['visa'] = visa_days

            matched_count += 1
        else:
            marathon['visa'] = None
            unmatched_count += 1
            unmatched_countries.add(country_code)

    print(f"\n매칭 완료: {matched_count}개")
    print(f"매칭 실패: {unmatched_count}개")

    if unmatched_countries:
        print(f"\n매칭되지 않은 국가 코드: {sorted(unmatched_countries)}")

    # 결과 저장 (원래 구조 유지)
    print(f"\n결과를 {output_file}에 저장 중...")
    if structure_type == 'marathons':
        marathons_json['marathons'] = marathons_data
    elif structure_type == 'results':
        marathons_json['results'] = marathons_data

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(marathons_json, f, ensure_ascii=False, indent=2)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"✓ 완료! (소요 시간: {elapsed_time:.2f}초)")

    # 샘플 출력
    print("\n[샘플 데이터 3개]")
    for i, marathon in enumerate(marathons_data[:3]):
        print(f"\n{i+1}. {marathon.get('title', 'N/A')}")
        print(f"   국가: {marathon.get('country', 'N/A')} ({marathon.get('countryCode', 'N/A')})")
        print(f"   비자: {marathon.get('visa')} 일" if marathon.get('visa') else f"   비자: 필요 (또는 정보 없음)")

if __name__ == "__main__":
    main()
