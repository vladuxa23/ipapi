import os
import random
import logging
import string
import time

import maxminddb
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.staticfiles import StaticFiles

from utils.logger import logger

app = FastAPI()

asn = maxminddb.open_database(os.path.join("maxmind", "GeoLite2-ASN.mmdb"))
country = maxminddb.open_database(os.path.join("maxmind", "GeoLite2-Country.mmdb"))
city = maxminddb.open_database(os.path.join("maxmind", "GeoLite2-City.mmdb"))

app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def log_requests(request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")

    return response


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.handlers.RotatingFileHandler(
        os.path.join('logs', 'api.log'), mode="a", maxBytes=100 * 1024, backupCount=3
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.on_event("shutdown")
def shutdown():
    asn.close()
    country.close()
    city.close()


@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css"
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/asn")
async def asn_by_ip(ip: str) -> dict:
    return asn.get(ip)


@app.get("/country")
async def country_by_ip(ip: str) -> dict:
    return country.get(ip)


@app.get("/city")
async def get_city_by_ip(ip: str) -> dict:
    return  city.get(ip)


if __name__ == "__main__":
    uvicorn.run("manage:app", host="0.0.0.0", port=3030, reload=False)