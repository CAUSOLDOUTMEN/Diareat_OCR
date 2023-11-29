import cv2
import numpy as np
from starlette.responses import JSONResponse
from utils.image_preprocess import PreProcessor
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import logging
import warnings

from utils.nutrition_runner import nutrition_run
from utils.pororo_ocr import PororoOcr
from concurrent.futures import ProcessPoolExecutor
import asyncio


warnings.filterwarnings('ignore')
executor = ProcessPoolExecutor(max_workers=10)



class ImageRequest(BaseModel):
    image_key: str

app = FastAPI()

ocr = PororoOcr()
preprocessor = PreProcessor()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, func, *args)
    return result

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

    result = await run_in_executor(nutrition_run, image)

    if not result:
        raise HTTPException(status_code=422, detail='Text Recognition Fail')
    else:
        return result
