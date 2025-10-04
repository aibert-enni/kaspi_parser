import asyncio
from datetime import datetime, timedelta, timezone
import json
import logging
import os

from app.core.dependencies import get_product_service
from app.services.parser_service import instagram_scraper
from app.utils.json_formatter import JsonFormatter

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

root_logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
root_logger.addHandler(handler)

logger = logging.getLogger(__name__)

async def kaspi_products_scrapping():
    with open("seed.json", "r") as f:
        urls = json.load(f)["products_urls"]

    products_info = []

    offers_info = {
        "offers": [],
        "offers_history": []
    }

    for url in urls:
        try:
            product_code = instagram_scraper.get_product_code_from_url(url)
            async with get_product_service() as product_service:
                product_db = await product_service.get_by_product_code(product_code)

                if product_db:
                    if datetime.now(timezone.utc) - product_db.updated_at <  timedelta(minutes=15):
                        logger.info(f"Product with code {product_code} already exists and was updated less than 15 minutes ago. Skipping...")
                        products_info.append(product_db.model_dump(mode="json", exclude={"id", "created_at", "updated_at", "offers", "offers_history"}))
                        offers_info["offers"].append(product_db.offers)
                        offers_info["offers_history"].append(product_db.offers_history)
                        continue
                    
                product_new = await instagram_scraper.scrape_product_by_url(url)

                if product_db:
                    product_db = await product_service.update_by_difference(original=product_db, new=product_new)
                    logger.info(f"Product with code {product_code} has been updated")
                else:
                    product_db = await product_service.create(product_new)

            offers_info["offers"].append(product_db.offers)
            offers_info["offers_history"].append(product_db.offers_history)
            products_info.append(product_db.model_dump(mode="json", exclude={"id", "created_at", "updated_at", "offers", "offers_history"}))
        except Exception as e:
            logger.error(f"Error with url - {url}, error: {e}")

    os.makedirs("export", exist_ok=True)

    export_data = {
        "products_info": products_info
    }

    with open("export/seed.json", "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=4, ensure_ascii=False)

    with open("export/offers.json", "w", encoding="utf-8") as f:
        json.dump(offers_info, f, indent=4, ensure_ascii=False)

async def main():
    sleep_time = 60 * 15
    while True:
        logger.info("Starting scrapping...")
        await kaspi_products_scrapping()
        logger.info("Sleeping for 15 minutes...")
        await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(main())