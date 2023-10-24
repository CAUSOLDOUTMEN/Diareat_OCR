import re

def parse_nutrients_from_text(text):
    nutrient_pattern = r'(물|질|방|류)\s*(\d+(?:\.\d+)?)(?:\s*g)?'
    # nutrient_pattern = r'(\W?(탄수화물|단백질|(?<![가-힣])지방)\W?)\s*([\d.]+)\s*([a-zA-Z]+)'
    kcal_pattern = r'(\d+)\s*kcal'

    matches = re.findall(nutrient_pattern, text)
    print(matches)
    nutrient_dict = {}
    nutrient_dict['탄수화물'] = -1
    nutrient_dict['당류'] = -1
    nutrient_dict['단백질'] = -1
    nutrient_dict['지방'] = -1

    for match in matches:
        if match[0] == '물': # 물로 끝나면 탄수화물이라고 판단
            nutrient_dict['탄수화물'] = float(match[1])
        elif match[0] == '류': # 류로 끝나면 당류라고 판단
            nutrient_dict['당류'] = float(match[1])
        elif match[0] == '질': # 질로 끝나면 단백질이라고 판단
            if match[1].startswith('0') and len(match[1]) > 1: # 0으로 시작하는데 소수점을 잃은 경우(02g 등)에 대한 예외처리
                nutrient_dict['단백질'] += float(match[1]) / 10
                continue
            nutrient_dict['단백질'] = float(match[1])
        elif match[0] == '방': # 방으로 끝나면 지방, 포화지방, 트랜스지방 이라고 판단 (합계)
            if match[1].startswith('0') and len(match[1]) > 1: # 0으로 시작하는데 소수점을 잃은 경우(02g 등)에 대한 예외처리
                nutrient_dict['지방'] += float(match[1]) / 10
                continue
            nutrient_dict['지방'] += float(match[1])
    if nutrient_dict['지방'] != -1:
        nutrient_dict['지방'] += 1 # 지방은 합계로 나오기 때문에 최초의 -1을 감안하여 1을 더해줌

    kcal_matches = re.findall(kcal_pattern, text) # 칼로리는 kcal로 끝나는 숫자
    if not kcal_matches:
        nutrient_dict['칼로리'] = -1
    else:
        nutrient_dict['칼로리'] = float(kcal_matches[0])

    return nutrient_dict
