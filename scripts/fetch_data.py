#!/usr/bin/env python3
"""URL 딕셔너리에서 CSV데이터를 가져오고 JSON으로 저장하는 스크립트"""

import csv
import io
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# URL 설정
DATA_URLS = {
    "news": "https://docs.google.com/spreadsheets/d/e/2PACX-1vREc_BHd3Mwee4ot1oZMedVj9a0fAlb2wX--HNKcrFJyMBkOfoZKxIeVqys6lncvohjwaXsadh6x8Co/pub?gid=0&single=true&output=csv",
    "events": "https://docs.google.com/spreadsheets/d/e/2PACX-1vREc_BHd3Mwee4ot1oZMedVj9a0fAlb2wX--HNKcrFJyMBkOfoZKxIeVqys6lncvohjwaXsadh6x8Co/pub?gid=1567101976&single=true&output=csv",
}

# 공통 세션 생성
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; DataFetcher/1.0)"})

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

def fetch_url(filename_url_pair, timeout=30, retries=2):
    """URL에서 CSV 데이터를 가져와서 JSON으로 변환합니다."""
    filename, url = filename_url_pair
    
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            
            # BOM 제거 후 CSV 파싱
            content = response.text.lstrip("\ufeff")
            
            # 빈 행 필터링하여 CSV 파싱
            csv_reader = csv.DictReader(io.StringIO(content))
            csv_data = [row for row in csv_reader if any(row.values())]
            
            return filename, {
                "success": True,
                "status_code": response.status_code,
                "data": csv_data,
                "records_count": len(csv_data),
                "headers": list(csv_data[0].keys()) if csv_data else [],
                "size": len(response.content),
                "filename": filename,
                "url": url,
                "processed_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST"),
            }
        except (requests.RequestException, csv.Error) as e:
            if attempt == retries - 1:
                return filename, {
                    "success": False,
                    "error": str(e),
                    "filename": filename,
                    "url": url,
                    "processed_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST"),
                }
    
    return filename, {
        "success": False,
        "error": "Max retries exceeded",
        "filename": filename,
        "url": url,
        "processed_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST"),
    }

def process_urls():
    """URL들을 병렬로 처리하고 결과를 반환합니다."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = dict(executor.map(fetch_url, DATA_URLS.items()))
    return results

def save_data(results, data_dir="data"):
    """결과를 JSON으로 저장합니다."""
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)
    
    for filename, result in results.items():
        json_path = data_path / f"{filename}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    try:
        results = process_urls()
        save_data(results)
        
        successful = sum(1 for r in results.values() if r["success"])
        total = len(results)
        
        if successful == total:
            print(f"All {total} data sources fetched successfully")
        else:
            print(f"{successful}/{total} successful")
            for filename, result in results.items():
                if not result["success"]:
                    print(f"ERROR {filename}: {result['error']}")
    
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())