import re
from fuzzywuzzy import process

def correct_ocr_text(text):
    target_words = ["kcal", "탄수화물", "단백질", "지방"]
    corrected_text = text
    for word in target_words:
        extracted_words = process.extractBests(word, text.split(), score_cutoff=50, limit=50)
        for extracted_word, score in extracted_words:
            if abs(len(extracted_word) - len(word)) <= 1:
                corrected_text = corrected_text.replace(extracted_word, word)
                break

    print(f'after correcting: ${corrected_text}')
    return corrected_text

def fix_nine_to_g(text):
    for i in range(len(text)-2):
        if text[i] == '9' and text[i + 1] == ' ': # 9 뒤에 공백일 때
            if text[i-1].isdigit() and text[i + 2] != 'g': # 9가 숫자의 마지막 부분이면서 뒤에 g가 없을 때
                text = text[:i] + 'g' + text[i + 1:] # 9를 g로 바꿔줌
    return text

def parse_nutrients_from_text(text):  # 기존 코드에 존재하던 부분
    nutrient_pattern = r'(물|질|방)\s*(\d+(?:\.\d+)?)\s?g'
    kcal_pattern = r'(\d+)\s*k'

    matches = re.findall(nutrient_pattern, text)
    nutrient_dict = {'탄수화물': 0, '단백질': 0, '지방': 0, '칼로리': 0}
    fats = []  # 지방, 포화지방, 트랜스지방을 담아 가장 큰 값을 지방으로 판단

    for match in matches:
        # print(match[0])
        if match[0] == '물':  # 물로 끝나면 탄수화물이라고 판단
            if match[1].startswith('0') and len(match[1]) > 1 and match[1][1] != '.':
                nutrient_dict['탄수화물'] = float(match[1]) / 10
                continue
            nutrient_dict['탄수화물'] = float(match[1])
        elif match[0] == '질':  # 질로 끝나면 단백질이라고 판단
            if match[1].startswith('0') and len(match[1]) > 1 and match[1][1] != '.':
                nutrient_dict['단백질'] = float(match[1]) / 10
                continue
            nutrient_dict['단백질'] = float(match[1])
        elif match[0] == '방':  # 방으로 끝나면 지방, 포화지방, 트랜스지방 이라고 판단 (합계)
            if match[1].startswith('0') and len(match[1]) > 1 and match[1][1] != '.':
                fats.append(float(match[1]) / 10)
                continue
            fats.append(float(match[1]))

    if len(fats) != 0:
        nutrient_dict['지방'] = max(fats)  # "방"으로 끝나는 것들의 숫자를 파싱한 값 중 가장 큰 값을 지방으로 판단 (포함의 관계이므로)
    kcal_matches = re.findall(kcal_pattern, text)  # 칼로리는 kcal로 끝나는 숫자
    if not kcal_matches:
        nutrient_dict['칼로리'] = -1
    else:
        nutrient_dict['칼로리'] = float(kcal_matches[0])

    return nutrient_dict
