from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import re

# ------------------------------------------------------------
# 공통 정리 함수: 줄바꿈, 탭, nbsp 제거하고 스페이스로 통일
# ------------------------------------------------------------
def clean(text):
    if not isinstance(text, str):
        return ""
    return " ".join(text.replace("\n", " ").replace("\t", " ").replace("\xa0", " ").split())

# ------------------------------------------------------------
# 상세정보 HTML(dt/dd) 파싱 함수
# ------------------------------------------------------------
def parse_detail_panel(detail_row):
    """
    Selenium element(detail_row)의 innerHTML에서
    <dt>레이블</dt><dd>값</dd> 쌍을 모두 읽어서
    딕셔너리로 반환
    """
    html = detail_row.get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')

    data = {}
    # dt -> 다음 dd 값을 읽어서 key/value 로 저장
    for dt in soup.select('dt'):
        key = dt.get_text(strip=True).rstrip(':')
        dd = dt.find_next_sibling('dd')
        if dd:
            # dd 안의 텍스트(줄바꿈, bullet 포함)를 깨끗이 정리
            data[key] = clean(dd.get_text(separator=' '))
    return data

# ------------------------------------------------------------
# 1) 주택담보대출(보금자리론 등) 스크래핑
# ------------------------------------------------------------
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)
driver.get("https://finlife.fss.or.kr/finlife/ldng/houseMrtg/list.do?menuNo=700007")

# 한 페이지에 50개 보이도록 설정
wait.until(EC.presence_of_element_located((By.ID, "pageUnit")))
Select(driver.find_element(By.ID, "pageUnit")).select_by_visible_text("50")
time.sleep(0.5)
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search.ajaxFormSearch"))).click()
time.sleep(0.5)

results = []
# 총 6페이지(1~6)
for page_num in range(1, 7):
    print(f"📄 [주담대] 페이지 {page_num} 수집 중...")
    if page_num > 1:
        # 페이지 번호 클릭
        links = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li a[data-pageindex]")
        for a in links:
            if a.get_attribute("data-pageindex") == str(page_num):
                driver.execute_script("arguments[0].click();", a)
                time.sleep(0.5)
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr")))
                break

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    for i in range(0, len(rows), 2):
        tds = rows[i].find_elements(By.TAG_NAME, "td")
        if len(tds) < 15:
            continue

        info = {
            "금융회사": clean(tds[1].text),
            "상품명": clean(tds[2].text),
            "주택종류": clean(tds[3].text),
            # select 박스 텍스트 마지막 단어만
            "금리방식": clean(tds[4].text.split()[-1]),
            "상환방식": clean(tds[5].text.split()[-1]),
            "최저금리": clean(tds[6].text),
            "최고금리": clean(tds[7].text),
            "전월평균금리": clean(tds[8].text),
            "문의전화": clean(tds[13].text),
        }

        # 상세보기 클릭
        detail_link = next(a for a in rows[i].find_elements(By.TAG_NAME, "a") if "상세" in a.text)
        driver.execute_script("arguments[0].scrollIntoView(true);", detail_link)
        driver.execute_script("arguments[0].click();", detail_link)
        time.sleep(0.1)

        # 다음 행이 상세정보 패널(tr)
        detail_row = rows[i + 1]
        detail_data = parse_detail_panel(detail_row)
        info.update(detail_data)

        results.append(info)

    print(f"✅ [주담대] 누적 수집: {len(results)}개")

driver.quit()

# ------------------------------------------------------------
# 2) 개인신용대출 (신용대출) 스크래핑
# ------------------------------------------------------------
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)
driver.get("https://finlife.fss.or.kr/finlife/ldng/indvlCrdt/list.do?menuNo=700009")

# 페이지당 50개 설정
wait.until(EC.presence_of_element_located((By.ID, "pageUnit")))
Select(driver.find_element(By.ID, "pageUnit")).select_by_visible_text("50")
time.sleep(0.5)
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search.ajaxFormSearch"))).click()
time.sleep(0.5)

rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
for i in range(0, len(rows), 2):
    tds = rows[i].find_elements(By.TAG_NAME, "td")
    if len(tds) < 14:
        continue

    info = {
        "금융회사": clean(tds[0].text),
        "대출종류": clean(tds[1].text),
        "금리구분": clean(tds[2].text),
        "900점 초과": clean(tds[3].text),
        "801~900점": clean(tds[4].text),
        "701~800점": clean(tds[5].text),
        "601~700점": clean(tds[6].text),
        "501~600점": clean(tds[7].text),
        "401~500점": clean(tds[8].text),
        "301~400점": clean(tds[9].text),
        "300점 이하": clean(tds[10].text),
        "평균금리": clean(tds[11].text),
        "CB회사명": clean(tds[12].text),
        "문의전화": clean(tds[13].text),
    }

    # 상세보기 클릭
    detail_link = next(a for a in rows[i].find_elements(By.TAG_NAME, "a") if "상세" in a.text)
    driver.execute_script("arguments[0].scrollIntoView(true);", detail_link)
    driver.execute_script("arguments[0].click();", detail_link)
    time.sleep(0.1)

    detail_row = rows[i + 1]
    detail_data = parse_detail_panel(detail_row)
    info.update(detail_data)

    results.append(info)

print(f"✅ [신용대출] 누적 수집: {len(results)}개 총합")

driver.quit()

# ------------------------------------------------------------
# 3) JSON 문서화
# ------------------------------------------------------------
documents = []
for idx, item in enumerate(results):
    doc = {
        "id": f"대출_{idx+1:03d}",
        "bank": item.get("금융회사", ""),
        "product_name": item.get("상품명", item.get("대출종류", "")),
        "type": "대출",
        "content": (
            f"{item.get('금융회사','')} / "
            f"{item.get('상품명', item.get('대출종류',''))} / "
            f"금리: {item.get('최저금리','')}"
            f"{'~'+item['최고금리'] if item.get('최고금리') else ''}"
        ),
        "key_summary": (
            f"{item.get('금융회사','')} / "
            f"{item.get('상품명', item.get('대출종류',''))} / "
            f"{item.get('평균금리','')}"
        ),
        "metadata": item
    }
    documents.append(doc)

with open("loan.json", "w", encoding="utf-8") as f:
    json.dump({"documents": documents}, f, ensure_ascii=False, indent=2)

print(f"📁 저장 완료: loan.json (총 {len(documents)}건)")
