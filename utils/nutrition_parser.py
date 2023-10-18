import re
from fuzzywuzzy import process

def correct_ocr_mistakes(text):
    # 검색 및 수정할 단어 목록
    target_words = ["칼로리", "탄수화물", "단백질", "지방"]

    corrected_text = text
    for word in target_words:
        # 각 단어에 대해 텍스트 내에서 가장 유사한 단어를 찾습니다.
        closest_match, score = process.extractOne(word, text.split())

        # 만약 찾아낸 단어와의 유사도가 60 이상이면(이 값을 조절할 수 있습니다), 텍스트를 수정합니다.
        if score > 60:
            corrected_text = corrected_text.replace(closest_match, word)

    return corrected_text

def parse_nutrients_from_text(text):
    nutrient_pattern = r'(\W?(탄수화물|단백질|(?<![가-힣])지방|내용량)\W?)\s*([\d.]+)\s*([a-zA-Z]+)'
    kcal_pattern = r'(\d+)\s*kcal'

    matches = re.findall(nutrient_pattern, text)
    print(matches)
    nutrient_dict = {match[1]: float(match[2]) for match in matches}

    kcal_matches = re.findall(kcal_pattern, text)
    if not kcal_matches:
        nutrient_dict['칼로리'] = -1
    else:
        nutrient_dict['칼로리'] = float(kcal_matches[0])

    return nutrient_dict
