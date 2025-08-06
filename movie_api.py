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


def get_movie_info():
    """영화진흥위원회 API를 호출하여 주간 상영영화 정보를 가져옴"""
    response = requests.get(URL)
    if response.status_code != 200:
        print("API 요청 실패:", response.status_code)
        return None

    data = response.json()
    box_office = data["boxOfficeResult"]
    show_range = box_office["showRange"]
    boxoffice_type = box_office["boxofficeType"]
    movies = box_office["weeklyBoxOfficeList"]

    # ✅ 영화 리스트를 딕셔너리로 정리
    movie_list = []
    for movie in movies:
        movie_list.append({
            "rank": movie["rank"],
            "name": movie["movieNm"],
            "open_date": movie["openDt"],
            "audi_acc": f"{int(movie['audiAcc']):,}",
            "sales_share": movie["salesShare"] + "%"
        })

    return {
        "show_range": show_range,
        "boxoffice_type": boxoffice_type,
        "movies": movie_list
    }


def update_readme():
    """README.md 파일을 업데이트"""
    info = get_movie_info()
    if not info:
        return

    show_range = info["show_range"]
    boxoffice_type = info["boxoffice_type"]
    movies = info["movies"]

    # ✅ 표 헤더
    table_header = "| 순위 | 영화명 | 개봉일 | 누적 관객수 | 매출 점유율 |\n|------|--------|--------|-------------|--------------|\n"

    # ✅ 표 데이터
    table_rows = ""
    for movie in movies:
        table_rows += f"| {movie['rank']} | {movie['name']} | {movie['open_date']} | {movie['audi_acc']} | {movie['sales_share']} |\n"

    # ✅ README 콘텐츠
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
    print(readme_content)
    # with open(README_PATH, "w", encoding="utf-8") as file:
    #     file.write(readme_content)


if __name__ == "__main__":
    update_readme()