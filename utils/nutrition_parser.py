import re
from fuzzywuzzy import process

def correct_ocr_text(text):
    target_words = ["kcal", "탄수화물", "단백질", "지방"]
    corrected_text = text
    for word in target_words:
        extracted_words = process.extractBests(word, text.split(), score_cutoff=60, limit=10)
        for extracted_word, score in extracted_words:
            if abs(len(extracted_word) - len(word)) <= 1:
                corrected_text = corrected_text.replace(extracted_word, word)
                break

    print(f'after correcting: ${corrected_text}')
    return corrected_text


def parse_nutrients_from_text(text):
    nutrient_pattern = r'(물|질|방|류)\s*(\d+(?:\.\d+)?)(?:\s*g)?' # 영양성분표는 정해진 규격이 있어, 네 영양소를 구분 짓는 글자로 파싱
    # nutrient_pattern = r'(\W?(탄수화물|단백질|(?<![가-힣])지방)\W?)\s*([\d.]+)\s*([a-zA-Z]+)'
    kcal_pattern = r'(\d+)\s*kcal'

    # 69와 같이, g와 9를 구분할 수 없는 경우가 있어서, 9 뒤에 공백이 있으면 9를 g로 교체함
    for i in range(len(text)):
         if text[i] == '9' and text[i+1] != 'g' and text[i+2] != 'g' and text[i+1] != 'k' and text[i+2] != 'k':
             text = list(text)
             text[i] = 'g'
             text = ''.join(text)

    matches = re.findall(nutrient_pattern, text)
    print(matches)
    nutrient_dict = {}
    fats = [] # 지방, 포화지방, 트랜스지방을 담아 가장 큰 값을 지방으로 판단

    for match in matches:
        if match[0] == '물': # 물로 끝나면 탄수화물이라고 판단
            nutrient_dict['carbohydrate'] = float(match[1])
        elif match[0] == '류': # 류로 끝나면 당류라고 판단
            nutrient_dict['당류'] = float(match[1])
        elif match[0] == '질': # 질로 끝나면 단백질이라고 판단
            if match[1].startswith('0') and len(match[1]) > 1: # 0으로 시작하는데 소수점을 잃은 경우(02g 등)에 대한 예외처리
                nutrient_dict['protein'] = float(match[1]) / 10
                continue
            nutrient_dict['protein'] = float(match[1])
        elif match[0] == '방': # 방으로 끝나면 지방, 포화지방, 트랜스지방 이라고 판단 (합계)
            if match[1].startswith('0') and len(match[1]) > 1: # 0으로 시작하는데 소수점을 잃은 경우(02g 등)에 대한 예외처리
                fats.append(float(match[1]) / 10)
                continue
            fats.append(float(match[1]))

    if len(fats) != 0:
        nutrient_dict['fat'] = max(fats) # "방"으로 끝나는 것들의 숫자를 파싱한 값 중 가장 큰 값을 지방으로 판단 (포함의 관계이므로)
    kcal_matches = re.findall(kcal_pattern, text) # 칼로리는 kcal로 끝나는 숫자
    if not kcal_matches:
        nutrient_dict['kcal'] = -1
    else:
        nutrient_dict['kcal'] = float(kcal_matches[0])

    return nutrient_dict
