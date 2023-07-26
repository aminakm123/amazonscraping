from django.shortcuts import render
from amazon_scrapper.scraper import scrape_products_page, save_to_csv



def scrape_and_export(request):
    base_url = "https://www.amazon.in"
    search_term = "bags"
    url = f"{base_url}/s?k={search_term}&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{{}}"
    
    all_products = []

    for page in range(1, 21):
        url = url.format(page)
        all_products = scrape_products_page(url,all_products)
    
    save_to_csv(all_products)

    return render(request, "scraping_complete.html")
