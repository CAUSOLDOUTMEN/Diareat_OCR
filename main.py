import os
import re
import traceback

import cv2
import boto3
import configparser

from pororo import Pororo
from pororo.pororo import SUPPORTED_TASKS
from utils.image_preprocess import PreProcessor
from utils.image_util import plt_imshow, put_text
from utils.nutrition_parser import parse_nutrients_from_text
from fastapi import FastAPI, HTTPException, Form
from botocore.exceptions import ClientError
from typing import Optional
import uuid
import logging
import warnings

warnings.filterwarnings('ignore')


class PororoOcr:
    def __init__(self, model: str = "brainocr", lang: str = "ko", **kwargs):
        self.model = model
        self.lang = lang
        self._ocr = Pororo(task="ocr", lang=lang, model=model, **kwargs)
        self.img_path = None
        self.ocr_result = {}

    def run_ocr(self, img_path: str, debug: bool = False):
        self.img_path = img_path
        self.ocr_result = self._ocr(img_path, detail=True)

        if self.ocr_result['description']:
            ocr_text = self.ocr_result["description"]
        else:
            ocr_text = "No text detected."

        if debug:
            self.show_img_with_ocr()

        return ocr_text

    @staticmethod
    def get_available_langs():
        return SUPPORTED_TASKS["ocr"].get_available_langs()

    @staticmethod
    def get_available_models():
        return SUPPORTED_TASKS["ocr"].get_available_models()

    def get_ocr_result(self):
        return self.ocr_result

    def get_img_path(self):
        return self.img_path

    def show_img(self):
        plt_imshow(img=self.img_path)

    def show_img_with_ocr(self):
        img = cv2.imread(self.img_path)
        roi_img = img.copy()

        for text_result in self.ocr_result['bounding_poly']:
            text = text_result['description']
            tlX = text_result['vertices'][0]['x']
            tlY = text_result['vertices'][0]['y']
            trX = text_result['vertices'][1]['x']
            trY = text_result['vertices'][1]['y']
            brX = text_result['vertices'][2]['x']
            brY = text_result['vertices'][2]['y']
            blX = text_result['vertices'][3]['x']
            blY = text_result['vertices'][3]['y']

            pts = ((tlX, tlY), (trX, trY), (brX, brY), (blX, blY))

            topLeft = pts[0]
            topRight = pts[1]
            bottomRight = pts[2]
            bottomLeft = pts[3]

            cv2.line(roi_img, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(roi_img, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(roi_img, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(roi_img, bottomLeft, topLeft, (0, 255, 0), 2)
            roi_img = put_text(roi_img, text, topLeft[0], topLeft[1] - 20, font_size=15)

            # print(text)

        plt_imshow(["Original", "ROI"], [img, roi_img], figsize=(16, 10))


app = FastAPI()

ocr = PororoOcr()
preprocessor = PreProcessor()


parser = configparser.ConfigParser()
parser.read("./boto.conf")
aws_s3_access_key = parser.get("aws_boto_credentials",
              "AWS_ACCESS_KEY")
aws_s3_secret_access_key = parser.get("aws_boto_credentials", "AWS_SECRET_ACCESS_KEY")
s3_region_name = parser.get("aws_boto_credentials", "REGION_NAME")
s3_bucket_name = parser.get("aws_boto_credentials",
              "BUCKET_NAME")


s3_client = boto3.client('s3',
                         aws_access_key_id=aws_s3_access_key,
                         aws_secret_access_key=aws_s3_secret_access_key,
                         region_name=s3_region_name)

BUCKET_NAME = s3_bucket_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def health_check():
    return {"ping":"pong"}

@app.post("/parse_nutrients/")
async def read_item(image_key: str = Form(...)):
    try:
        file_name = f"cache/temp_{image_key}"
        if not os.path.exists(file_name):
            s3_client.download_file(BUCKET_NAME, image_key, file_name)
        image = cv2.imread(file_name, cv2.IMREAD_COLOR)

        screen_cnt = preprocessor.detectContour(image)
        warped = preprocessor.four_point_transform(image, screen_cnt.reshape(4, 2))

        image_path = "test_image/output/cropped_table_enhanced.jpg"
        cv2.imwrite(image_path, warped)
        text = ocr.run_ocr(image_path, debug=True)

        realdata = ""
        for d in text:
            if '탄' in d:
                realdata = d
                break

        final_key = {'내용량', '칼로리', '탄수화물', '단백질', '지방'}
        final_dict = {key: -1 for key in final_key}

        if not realdata:
            raise HTTPException(status_code=404, detail='Text Recognition Fail')
        else:
            nutrient_dict = parse_nutrients_from_text(realdata)
            for key in final_key:
                final_dict[key] = nutrient_dict.get(key, -1)

        return final_dict
    except ClientError:
        raise HTTPException(status_code=404, detail="Image not found in S3")

    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")




