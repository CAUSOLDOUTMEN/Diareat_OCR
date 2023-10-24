import cv2

from hanspell import spell_checker
from utils.image_preprocess import PreProcessor
from utils.nutrition_parser import parse_nutrients_from_text
from utils.pororo_ocr import PororoOcr
from fastapi import HTTPException


def nutrition_run(image):
    preprocessor = PreProcessor()
    ocr = PororoOcr()


    warped = preprocessor.preprocess_image(image)

    image_path = "./test_image/output/cropped_table_enhanced.jpg"
    cv2.imwrite(image_path, warped)
    text = ocr.run_ocr(image_path, debug=True)

    realdata = ""
    for d in text:
        if '탄' or '백' or '방' or '칼' or '열' in d:
            realdata = d
            break
    print('target string for parsing: ', realdata)

    final_key = {'칼로리', '탄수화물', '단백질', '지방'}
    final_dict = {key: -1 for key in final_key}

    if not realdata:
        return False
    else:
        nutrient_dict = parse_nutrients_from_text(realdata)
        for key in final_key:
            final_dict[key] = nutrient_dict.get(key, -1)

    return final_dict