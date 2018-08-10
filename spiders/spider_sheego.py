import scrapy
from scrapy.http import HtmlResponse
import request
# from urllib.request import urlopen
# import webbrowser
# from scrapy.utils.response import open_in_browser
# import urllib.request

final_url = ''
variantid = ''
result = 0
to_string = ''
json = ''
count = 0

class sheegoItem(scrapy.Item):
    fields_to_export = ['spiderName', 'category', 'url', 'retailer', 'image_url']
    spiderName = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    retailer = scrapy.Field()
    image_urls = scrapy.Field()
    skus = scrapy.Field()


class skusItem(scrapy.Item):
    size_color = scrapy.Field()
    # available = scrapy.Field()
    # currency = scrapy.Field()
    # colour = scrapy.Field()
    # price = scrapy.Field()
    # size = scrapy.Field()


class SheegoSpider(scrapy.Spider):
    name = "SheegoSpider"
    start_urls = [
        'https://www.sheego.de/neu/alle-damenmode-neuheiten/',
        # 'https://www.sheego.de/damenmode/',
        # 'https://www.sheego.de/damen-waesche/',
        #'https://www.sheego.de/bademode/',
         # 'https://www.sheego.de/damenschuhe/',
        # 'https://www.sheego.de/damenmode-sale/',
    ]

    def parse(self, response):
        for href in response.xpath("//a[contains(@class,'js-product__link')]/@href"):
            global count
            count = count + 1
            print("Count is :: ", count)
            yield response.follow(href, self.go_to_item_page)

        next_page = response.xpath('//span[contains(@class,"paging__btn--next")]/a/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def go_to_item_page(self, response):  # here response will return the page of each item
        item = sheegoItem()
        item['url'] = response.url
        item['spiderName'] = "SheegoSpider"
        cateogry_list = list()
        print("RESPONSE ::", response.url)
        for index in response.xpath("//div[contains(@class,'details__box--main')]/script/text()").extract():
            if "window.oTracking.data.productCategory" in index:
                cat = index.split("=")[1]
                cat = cat.split(";")[0]
                cat = cat.replace("'","")
                for element in cat.split("/"):
                    cateogry_list.append(element)

        item['category'] = cateogry_list
        item['retailer'] = "Sheego"

        # image url scraper
        image_urls = list()
        for image_url in response.xpath("//a[@id='magic']/@href"):
            image_urls.append(image_url.extract().strip())

        item['image_urls'] = image_urls

        list_of_color = list()
        for script in response.xpath("//section[contains(@class,'p-details__variants')]/section"
                                     "/section[contains(@class,' color')]"
                                     "/div[contains(@class,'cj-slider')]/div[contains(@class, 'cj-slider__frame')]"
                                     "/div[contains(@class, 'cj-slider__slides')]"
                                     "/script[contains(@class,'js-ads-script')][1]/text()"):
            data = script.extract()
            data = data.split("=")[1]
            data = data.split(";")[0]
            data = data.replace("[", '')
            data = data.replace("]", '')
            for index in data.split(","):
                index = index.replace("'", "")
                index = index.replace(" ", "")
                list_of_color.append(index)

            # print("List :: ", list_of_color)
            link = response.url.split("?")[0] + "?color="
            urls = list()
           # print("These are the links of the products :: \n")
            for index in list_of_color:
                temp = link + index
                urls.append(temp)  # Is it possible to send list
                #yield scrapy.Request(url=temp, callback=self.parseTheimagelink, meta={'url_list': urls})
                yield response.follow(temp, self.parseTheimagelink, meta={'url_list': urls, 'item': item})

    def parseTheimagelink(self, response):
        url_list = response.meta.get('url_list')
        item = response.meta.get('item')
        dict_list = list()
        for url in url_list:
            r = requests.get(url)
            #print("URL :: ", url)
            response = HtmlResponse(url="url", body=r.content)
            # x = response.xpath('//div[contains(@class,"f-row")]/div[contains(@class,"cj-p-details__variants")]'
            #                    '/div[contains(@class,"at-dv-title-box")]/h1/span[contains(@class,"l-bold")]/text()').extract_first().strip()
            temp_list = list()
            sizes = list()
            current_color = list()
            for size in response.xpath("//div[contains(@class,'c-sizespots')]/div[contains(@class,'at-dv-size-button')]/text()"):
                if size.extract() != "\n":
                    temp_list.append(size.extract())
            for index in temp_list:
                sizes.append(index.strip())

            #print("Sizes available ::  ", sizes)
            temp_list = response.xpath("//section[contains(@class,'p-details__variants')]"
                                           "/section/p[contains(@class,'l-mb-5')]/text()").extract()
            for index in temp_list:
                if index.strip() != '':
                    current_color.append(index.strip())
            price = response.xpath("//section[contains(@class,'p-details__price')]/span[contains(@class,'l-bold')]/text()").extract_first().strip()
            #print("PRICE  ", price)
            #print("COLOR ", current_color)
            #print("Sizes ", sizes)
            color=""
            for index in current_color:
                color = index



            for index in sizes:
                name = index + "_" + color
                #print(name)

                dict = { "available": "true", "currency": "US", "colour": color, "price": price.strip(), "size": index}
                dict_main = {name: dict}
               # print(dict_main)
                # skusItem['avaliable']= "true"
                # skusItem['currency'] = "US"
                # skusItem['color'] = current_color.pop()
                # skusItem['size'] = index
                #print(skusItem)
                dict_list.append(dict_main)
        #print(dict_list)
        item["skus"] = dict_list
        yield item
        print("hi")
