import re

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
