import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pyppeteer import launch
import io
import logging

app = FastAPI()


async def generate_pdf(url: str) -> bytes:
    print("generate_pdf", url)
    browser = None
    try:
        # browser = await launch(headless=True, args=[
        #     '--no-sandbox',
        #     '--disable-setuid-sandbox',
        #     '--disable-dev-shm-usage',
        #     '--disable-gpu',
        #     '--disable-software-rasterizer'
        # ])
        browser = await launch(executablePath='/usr/local/bin/headless-chromium', args=[
            '--headless',
            '--no-sandbox',
            '--single-process',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-software-rasterizer'
        ])
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 60000})  # 페이지가 완전히 로드될 때까지 대기
        print("url loaded")
        # await asyncio.sleep(3)  # 3초 대기
        # pdf = await page.pdf({
        #     'format': 'A4',
        #     'printBackground': False,
        # })
        # return pdf
    except Exception as e:
        print("Error generating PDF")
        logging.error(e)
    finally:
        if browser:
            await browser.close()


@app.get("/")
def main():
    return {"code": 1}


@app.get("/generate-pdf")
async def generate_pdf_route(url: str = Query(..., description="The URL of the website to convert to PDF")):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        pdf = await generate_pdf(url)
        return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=output.pdf"
        })
    except Exception as e:
        print("Error generating PDF")
        logging.error(e)
        raise HTTPException(status_code=500, detail="An error occurred while generating the PDF")

# sudo uvicorn main:app --host 0.0.0.0 --port 9001
