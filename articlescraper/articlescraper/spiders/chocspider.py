import scrapy
from articlescraper.items import ChocolateProduct
from articlescraper.itemloaders import ChocolateProductLoader


class ChocspiderSpider(scrapy.Spider):
    name = 'chocspider'
    allowed_domains = ['www.chocolate.co.uk']
    start_urls = ['https://www.chocolate.co.uk/collections/all']

    def parse(self, response): ##this function will run as soon as the spider loads and visits the start url

        products =  response.css('product-item')
        #loop through all products on the page

        for product in products:
            chocolate = ChocolateProductLoader(item=ChocolateProduct(), selector=product)

            chocolate.add_css('name','a.product-item-meta__title::text'),
            chocolate.add_css('price','span.price', re='<span class="price">\n              <span class="visually-hidden">Sale price</span>(.*)</span>'),
            chocolate.add_css('url', 'div.product-item-meta a::attr(href)')
            yield chocolate.load_item()
            

        next_page = response.css('[rel="next"] ::attr(href)').get()
        if next_page is not None:
            next_page_url = 'https://www.chocolate.co.uk' + next_page
            yield response.follow(next_page_url, callback=self.parse) #follow the nextpage url and carry out the parse method again

#scrapy crawl chocspider -O mydata.csv/json - to save as csv or json file
# -o instead of -O appends the scraped data, -O will overwrite
