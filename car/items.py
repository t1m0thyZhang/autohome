# -*- coding: utf-8 -*-

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class CarItem(Item):
    # string 车名 "奔驰S600"
    website_name = Field()
    # string 款式 "2013款"
    website_type = Field()
    # string 全网用户评分
    website_score = Field()
    # string 全网用户印象标签
    website_feeling = Field()
    # string 全网平均购车价
    website_price = Field()
    # string 全网评价油耗
    website_oil = Field()

    # string url
    url = Field()
    # string 评论标题
    comment_title = Field()
    # string 评论时间
    comment_date = Field()
    # string 评论内容
    comment_content = Field()

    # string 用户购买车名
    user_name = Field()
    # string 用户购买款式
    user_type = Field()
    # string 用户购买价格
    user_price = Field()
    # string 用户购买地址
    user_address = Field()
    # string 用户购买时间
    user_date = Field()
    # string 用户购买目的
    user_intent = Field()
    # string 用户油耗
    user_oil = Field()
    # string 用户行驶公里
    user_miles = Field()
    # list 用户评分
    user_score = Field()


class ProductLoader(ItemLoader):
    default_item_class = CarItem
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    description_out = Join()
