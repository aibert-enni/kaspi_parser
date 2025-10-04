import asyncio
import json
import logging
import random
import pathlib

import httpx
from fake_useragent import UserAgent

from app.schemes.parser import DataFromHtmlS, ReviewsS
from app.schemes.product import ProductBaseS
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)

ua = UserAgent()


class KaspiScraper:
    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": ua.random,
                "Host": "kaspi.kz",
                "X-Ks-City": "750000000",
            }
        )

    @staticmethod
    def get_product_code_from_url(url: str) -> str:
        return url.split("/")[-2].split("-")[-1]

    async def get_product_page_html(self, url: str) -> str:
        resp = await self.client.get(url)

        if resp.status_code != 200:
            raise RuntimeError(f"Error getting product page: {resp.status_code}")

        return resp.text

    def get_product_data_from_html(self, html: str) -> DataFromHtmlS:
        # Находим место, где начинается JSON
        start = html.find("BACKEND.components.item")
        if start == -1:
            raise RuntimeError("Не нашли переменную BACKEND.components.item")

        # Находим первую фигурную скобку после знака '='
        start = html.find("{", start)

        # Ищем конец объекта: считаем баланс скобок
        braces = 0
        end = start
        for i, ch in enumerate(html[start:], start=start):
            if ch == "{":
                braces += 1
            elif ch == "}":
                braces -= 1
                if braces == 0:
                    end = i + 1
                    break

        json_text = html[start:end]

        data = json.loads(json_text)

        title = data["card"]["title"]
        min_price = data["card"]["price"]
        category = data["breadcrumbs"][-1]["title"]
        brand = data["card"]["promoConditions"]["brand"]
        product_codes = data["card"]["promoConditions"]["categoryCodes"]

        details = {}

        for specification in data["specifications"]:
            for feature in specification["features"]:
                values = []

                for value in feature["featureValues"]:
                    values.append(value["value"])

                details[feature["name"]] = values

        image_links = []

        for image in data["galleryImages"]:
            image_links.append(image["large"])

        return DataFromHtmlS(
            title=title,
            min_price=min_price,
            category=category,
            brand=brand,
            product_codes=product_codes,
            details=details,
            image_links=image_links
        )

    async def get_product_reviews(
        self, product_code: str, product_url: str
    ) -> ReviewsS:

        self.client.headers["Referer"] = product_url

        url = f"https://kaspi.kz/yml/review-view/api/v1/reviews/product/{product_code}?baseProductCode&orderCode&filter=COMMENT&sort=POPULARITY&limit=9&merchantCodes&withAgg=true"

        resp = await self.client.get(url)

        data = resp.json()

        rating = data["summary"]["global"]

        comments = data["groupSummary"][1]["total"]

        return ReviewsS(rating=rating, comments=comments)

    async def get_product_offers(
        self, product_code: str, product_url: str, brand: str, product_codes: list[str]
    ) -> list[dict]:
        self.client.headers["Referer"] = product_url

        self.client.headers["Origin"] = "https://kaspi.kz"

        url = f"https://kaspi.kz/yml/offer-view/offers/{product_code}"

        limit = 60

        payload = {
            "cityId": "750000000",
            "id": product_code,
            "merchantUID": [],
            "limit": limit,
            "page": 0,
            "product": {
                "brand": brand,
                "categoryCodes": product_codes,
                "baseProductCodes": [],
                "groups": None,
            },
            "sortOption": "PRICE",
            "highRating": None,
            "searchText": None,
            "isExcellentMerchant": False,
            "zoneId": ["Magnum_ZONE1"],
            "installationId": "-1",
        }

        offers = []

        while True:
            resp = await self.client.post(url=url, json=payload)

            data = resp.json()

            for offer in data["offers"]:
                offers.append(
                    {
                        "name": offer["merchantName"],
                        "price": offer["price"],
                    }
                )

            if data["total"] <= limit * payload["page"]:
                break

            payload["page"] += 1

        self.client.headers.pop("Origin")

        return offers

    async def scrape_product_by_url(self, url: str) -> ProductBaseS:
        html = await self.get_product_page_html(url)

        data = self.get_product_data_from_html(html)

        product_code = self.get_product_code_from_url(url)

        reviews = await self.get_product_reviews(product_code, url)

        offers = await self.get_product_offers(
            product_code, url, data.brand, data.product_codes
        )

        min_price = offers[0]["price"]
        max_price = offers[-1]["price"]

        price_history = ProductService.format_price_history(min_price=min_price, max_price=max_price)
        offers_history = ProductService.format_offers_history(offers)

        return ProductBaseS(
            product_code=product_code,
            name=data.title,
            min_price=min_price,
            max_price=max_price,
            rating=reviews.rating,
            comments_count=reviews.comments,
            details=data.details,
            image_links=data.image_links,
            offers=offers,
            sellers_count=len(offers),
            price_history=[price_history],
            offers_history=[offers_history]
        )


instagram_scraper = KaspiScraper()
