import os
import traceback

import cv2
import boto3
import configparser

from starlette.responses import JSONResponse
from utils.image_preprocess import PreProcessor
from fastapi import FastAPI, HTTPException, Form
from botocore.exceptions import ClientError
from pydantic import BaseModel
import logging
import warnings

from utils.nutrition_runner import nutrition_run
from utils.pororo_ocr import PororoOcr

warnings.filterwarnings('ignore')



class ImageRequest(BaseModel):
    image_key: str

app = FastAPI()

ocr = PororoOcr()
preprocessor = PreProcessor()

aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
bucket_name = os.environ.get('BUCKET_NAME')
region_name = os.environ.get('REGION_NAME')


s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def health_check():
    return {"ping":"pong"}

@app.exception_handler(Exception)
def handle_unexpected_error(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {exc}"},
    )

@app.post("/parse_nutrients", status_code=201)
async def read_item(request: ImageRequest):
    logger.info(request)
    logger.info(request.image_key)
    image_name = request.image_key
    file_name = f"./cache/temp_{image_name}"
    if not os.path.exists(file_name):
        logger.info("Download image from s3")
        try:
            s3_client.download_file(bucket_name, image_name, file_name)
        except ClientError:
            raise HTTPException(status_code=404, detail='Image not found in S3')
    image = cv2.imread(file_name, cv2.IMREAD_COLOR)

    result = nutrition_run(image)
    if not result:
        raise HTTPException(status_code=422, detail='Text Recognition Fail')
    else:
        return result
