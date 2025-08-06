import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
README_PATH = "README.md"

# 오늘 기준 1주일 전 날짜
today = datetime.now()
one_week_ago = today - timedelta(days=7)
TARGET_DATE = one_week_ago.strftime("%Y%m%d")

# KOBIS API URL
URL = f"http://kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json?key={API_KEY}&targetDt={TARGET_DATE}&weekGb=0"


def format_rank_change(rank_inten, rank_old_and_new):
    """순위 변화 표시: 증가 ▲, 감소 ▼, 신규 NEW"""
    if rank_old_and_new == "NEW":
        return "🆕 NEW"
    try:
        inten = int(rank_inten)
    except:
        return ""
    if inten > 0:
        return f"▲{inten}"
    elif inten < 0:
        return f"▼{abs(inten)}"
    else:
        return "-"

def get_movie_info():
    response = requests.get(URL)
    if response.status_code != 200:
        print("API 요청 실패:", response.status_code)
        return None

    data = response.json()
    box_office = data["boxOfficeResult"]
    show_range = box_office["showRange"]
    boxoffice_type = box_office["boxofficeType"]
    movies = box_office["weeklyBoxOfficeList"]

    movie_list = []
    for m in movies:
        movie_list.append({
            "rank": m["rank"],
            "rank_change": format_rank_change(m["rankInten"], m["rankOldAndNew"]),
            "name": m["movieNm"],
            "open_date": m["openDt"],
            "audi_acc": f"{int(m['audiAcc']):,}",
            "sales_share": m["salesShare"] + "%",
        })

    return {
        "show_range": show_range,
        "boxoffice_type": boxoffice_type,
        "movies": movie_list
    }

def update_readme():
    info = get_movie_info()
    if not info:
        return

    show_range = info["show_range"]
    boxoffice_type = info["boxoffice_type"]
    movies = info["movies"]

    table_header = (
        "| 순위 | 변동 | 영화명 | 개봉일 | 누적 관객수 | 매출 점유율 |\n"
        "|------|-------|--------|--------|-------------|--------------|\n"
    )

    table_rows = ""
    for movie in movies:
        table_rows += (
            f"| {movie['rank']} | {movie['rank_change']} | {movie['name']} | "
            f"{movie['open_date']} | {movie['audi_acc']} | {movie['sales_share']} |\n"
        )

    readme_content = f"""
# 🎬 {boxoffice_type} ({show_range})

KOBIS API 기반으로 자동 업데이트된 **주간 박스오피스 TOP 10**입니다.  
(기준: {show_range})

---

## 📊 박스오피스 순위

{table_header}{table_rows}

---

✅ 데이터 출처: [KOBIS 영화관입장권통합전산망](https://www.kobis.or.kr)
"""

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(readme_content)


if __name__ == "__main__":
    update_readme()