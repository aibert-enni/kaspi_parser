import asyncio
from datetime import datetime, timedelta, timezone
import json
import logging
from pathlib import Path
import traceback

from app.core.settings import settings
from app.core.dependencies import get_product_service
from app.services.parser_service import instagram_scraper
from app.utils.json_formatter import JsonFormatter

# Установливаем JsonFormatter для глобального логгера
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

root_logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
root_logger.addHandler(handler)

logger = logging.getLogger(__name__)

# Путь где хранить результаты
EXPORT_DIR = Path("export")

async def process_url(url: str, semaphore: asyncio.Semaphore, products_info: dict, products_offers_info: dict, skipped_urls: list):
    """Обрабатывает один продукт по ссылке с ограничением параллельных запросов."""
    async with semaphore:
        logger.info("Processing URL...", extra={"url": url})

        offers_info = {"offers": [], "offers_history": []}

        try:
            product_code = instagram_scraper.get_product_code_from_url(url)

            async with get_product_service() as product_service:
                product_db = await product_service.get_by_product_code(product_code)

                # Если продукт недавно обновлялся
                if product_db and datetime.now(timezone.utc) - product_db.updated_at < timedelta(minutes=settings.parser.SLEEP_TIME_MINUTES):
                    logger.info(
                        f"Skipping product (already updated <{settings.parser.SLEEP_TIME_MINUTES} min ago)",
                        extra={"product_code": product_code}
                    )
                    products_info[url] = product_db.model_dump(
                        mode="json",
                        exclude={"id", "created_at", "updated_at", "offers", "offers_history"}
                    )
                    offers_info["offers"].append(product_db.offers)
                    offers_info["offers_history"].append(product_db.offers_history)
                    products_offers_info[url] = offers_info
                    return

                # Парсим данные
                product_new = await instagram_scraper.scrape_product_by_url(url)

                # Обновляем/создаем
                if product_db:
                    product_db = await product_service.update_by_difference(original=product_db, new=product_new)
                    logger.info("Product updated", extra={"product_code": product_code})
                else:
                    product_db = await product_service.create(product_new)
                    logger.info("Product created", extra={"product_code": product_code})

            # Сохраняем офферы
            offers_info["offers"].append(product_db.offers)
            offers_info["offers_history"].append(product_db.offers_history)
            products_offers_info[url] = offers_info
            products_info[url] = product_db.model_dump(
                mode="json",
                exclude={"id", "created_at", "updated_at", "offers", "offers_history"}
            )

        except Exception as e:
            logger.error(
                "Error during product scraping",
                extra={"url": url, "error": str(e), "traceback": traceback.format_exc()}
            )
            skipped_urls.append({"url": url, "error": str(e)})

async def kaspi_products_scrapping():
    with open("seed.json", "r", encoding="utf-8") as f:
        urls = json.load(f)["products_urls"]

    products_info = {}
    products_offers_info = {}
    skipped_urls = []

    semaphore = asyncio.Semaphore(settings.asyncio.MAX_CONCURRENT_TASKS)

    tasks = [process_url(url, semaphore, products_info, products_offers_info, skipped_urls) for url in urls]
    await asyncio.gather(*tasks)

    # Сохраняем результаты
    with (EXPORT_DIR / "seed.json").open("w", encoding="utf-8") as f:
        json.dump({"products_info": products_info}, f, indent=4, ensure_ascii=False)

    with (EXPORT_DIR / "offers.json").open("w", encoding="utf-8") as f:
        json.dump(products_offers_info, f, indent=4, ensure_ascii=False)

    with (EXPORT_DIR / "skipped_urls.json").open("w", encoding="utf-8") as f:
        json.dump(skipped_urls, f, indent=4, ensure_ascii=False)

async def main():
    while True:
        logger.info("Starting scrapping...")
        await kaspi_products_scrapping()
        logger.info(f"Sleeping for {settings.parser.SLEEP_TIME_MINUTES} minutes...")
        await asyncio.sleep(settings.parser.SLEEP_TIME_MINUTES * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting...")