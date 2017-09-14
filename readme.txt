===============================
Project Based on Scrapy Redis
===============================


This directory contains an example Scrapy project integrated with scrapy-redis.
By default, all items are sent to redis (key ``<spider>:items``). All spiders
schedule requests through redis, so you can start additional spiders to speed
up the crawling.




requirements
------------
scrapy
scrapy-redis




Spiders
-------

* **myspider_redis**

  This spider uses redis as a shared requests queue and uses
  ``myspider:start_urls`` as start URLs seed. For each URL, the spider outputs
  one item.


.. note::

    All requests are persisted by default. You can clear the queue by using the
    ``SCHEDULER_FLUSH_ON_START`` setting. For example: ``scrapy crawl dmoz -s
    SCHEDULER_FLUSH_ON_START=1``.




Processing items
----------------
解析完详情页数据后，直接将解析结果写缓存，因此本框架不需要自定义的pipelines处理，直接走默认的piplines即可
然后由 download_items_from_redis.py 异步download items结果数据

The ``download_items_from_redis.py`` provides an example of consuming the items queue::

    python download_items_from_redis.py --help


--------------
