# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import sqlite3

class ArticlescraperPipeline:
    def process_item(self, item, spider):
        return item


class PriceToFloatPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('price'):
            floatPrice = float(adapter['price'])
            adapter['price'] = floatPrice

            return item
        else:
            raise DropItem(f"Missing price in {item}")


class DuplicatesPipeline:
    
    def __init__(self):
        self.names_seen = set()

    def process_items(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter['name'] in self.names_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.names_seen.add(adapter['name'])
            return item


class SaveToDBPipeline:

    def __init__(self):
         ## Create/Connect to database
        self.con = sqlite3.connect('chocolate.db')

        ## Create cursor, used to execute commands
        self.cur = self.con.cursor()

         ## Create chocolates table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS chocolates(
            name TEXT,
            price REAL,
            url TEXT
        )
        """)

    def process_item(self, item, spider):

    ## Check to see if name is already in database 
        self.cur.execute("SELECT * from chocolates WHERE name = ?", (item['name'],))
        result = self.cur.fetchone()

        ## If it is in DB, send warning
        if result:
            spider.logger.warn("Item already in database: %s" % item['text'])
        
        else:
        ## insert statement
            self.cur.execute("""
            INSERT INTO chocolates (name, price, url) VALUES (?, ?, ?)
        """,
        (
            item['name'],
            item['price'],
            item['url']
        ))
        ## commit data into database
        self.con.commit()

        return item