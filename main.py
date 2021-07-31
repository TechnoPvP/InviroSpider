import scrape
import math
import writer

# TODO Minus 26% from total price - Tax incen

def run_scraper():
    spider = scrape.Screenshot()
    spider.run()

# 50 Leads Run Time - 1m : 51s


# try:
# run_scraper()
# except:
    # writer.Writer().save()

if __name__ == '__main__':
    run_scraper()