from pydantic import BaseModel


class DataFromHtmlS(BaseModel):
    title: str
    min_price: int
    category: str
    brand: str
    product_codes: list[str]
    details: dict
    image_links: list[str]

class ReviewsS(BaseModel):
    rating: float
    comments: int