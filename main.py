import os
import traceback

import cv2
import boto3
import configparser

import numpy as np
from starlette.responses import JSONResponse
from utils.image_preprocess import PreProcessor
from fastapi import FastAPI, HTTPException, File, UploadFile
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
async def read_item(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)

    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result = nutrition_run(image)
    if not result:
        raise HTTPException(status_code=422, detail='Text Recognition Fail')
    else:
        return result
