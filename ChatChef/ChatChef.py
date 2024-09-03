import pandas as pd
from flask import Flask, request, jsonify
import re
from datetime import datetime, timedelta

app = Flask(__name__)

# 엑셀 파일 로드 및 열 이름 정제
df = pd.read_excel('d:/menu/chatchef/chatchef/대전_0902.xlsx')
df.columns = df.columns.str.strip()  # 열 이름의 공백 제거

# 식사 종류 매핑
meal_mapping = {
    "아침": "조식",
    "점심": "중식",
    "저녁": "석식",
    "조식": "조식",
    "중식": "중식",
    "석식": "석식"
}

# 날짜 처리를 위한 함수
def process_date(input_date):
    if input_date == "오늘":
        return datetime.now().strftime('%Y-%m-%d')
    elif input_date == "내일":
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        return input_date  # 기본적으로 YYYY-MM-DD 형식의 날짜를 반환

# 특정 날짜와 식사 종류에 해당하는 메뉴를 추출하는 함수
def get_menu(date, meal_type):
    try:
        # 날짜와 식사 종류로 필터링하여 메뉴 추출
        filtered_df = df[(df['날짜'] == date) & (df['구분'] == meal_type)]
        if not filtered_df.empty:
            menu_items = filtered_df.iloc[0]['메뉴']
            # 메뉴를 쉼표(,)로 분리한 후 줄 바꿈(\n)으로 연결
            return menu_items.replace(',', '\n')  
        else:
            return "해당 날짜나 식사 종류의 메뉴를 찾을 수 없습니다."
    except KeyError:
        return "데이터를 찾을 수 없습니다. 날짜나 식사 종류의 형식을 확인하세요."
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 날짜와 식사 종류를 파싱하는 함수
def parse_input(utterance):
    # 정규 표현식을 사용하여 날짜와 식사 종류를 추출
    match = re.match(r'(\S+)\s*(\S+)', utterance)
    if match:
        input_date = match.group(1)
        meal_input = match.group(2)
        date = process_date(input_date)  # 날짜를 오늘, 내일로 처리
        meal_type = meal_mapping.get(meal_input)  # 매핑된 식사 종류 가져오기
        return date, meal_type
    else:
        return None, None

@app.route('/get_menu', methods=['POST'])
def handle_request():
    data = request.get_json()
    
    # 사용자가 보낸 발화 내용에서 날짜와 식사 종류 추출 (예: "오늘 아침")
    utterance = data['userRequest']['utterance']
    
    # 날짜와 식사 종류 파싱
    date, meal_type = parse_input(utterance)

    if not date or not meal_type:
        response_message = "날짜와 식사 종류를 정확히 입력해 주세요. 예: '오늘 아침' 또는 '2024-09-02 조식'"
    else:
        # 메뉴 정보 가져오기
        menu_text = get_menu(date, meal_type)
        response_message = f"{date}의 {meal_type} 메뉴:\n{menu_text}"

    # JSON 응답 생성 (퀵 리플라이 없이)
    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_message
                    }
                }
            ]
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)