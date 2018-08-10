from scrapy.cmdline import execute

execute(['scrapy', 'crawl', 'SheegoSpider', '-o', 'sheegoItemFile2.json'])
# execute(['scrapy', 'crawl', 'quotes'])
# execute(['scrapy', 'shell', 'https://www.sheego.de/'])