import csv
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from amazoncaptcha import AmazonCaptcha
from urllib.parse import urljoin


base_url = "https://www.amazon.in"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}

def bypass_captcha(url):
    response = requests.get(url, headers=HEADERS)
    if "captcha" in response.url:
        captcha = AmazonCaptcha.from_page_source(response.content)
        captcha.solve()
        response = captcha.retry_request()
    return response

def scrape_products_page(url,products_list):
    response = bypass_captcha(url)
    product_soup = BeautifulSoup(response.content, "html.parser")

    products = product_soup.find_all("div", {"data-component-type": "s-search-result"})        
    for product in products:
        product_name_element = product.find('span', class_='a-size-medium a-color-base a-text-normal')      
        if product_name_element:
            product_name = product_name_element.get_text(strip=True)
        else:
            product_name = ""
        product_price_element = product.find("span", {"class": "a-price-whole"})
        if product_price_element:
            product_price = product_price_element.get_text(strip=True)
        else:
            product_price = ""
        product_rating_element = product.find("span", {"class": "a-icon-alt"})
        if product_rating_element:
            product_rating = product_rating_element.get_text(strip=True)
        else:
            product_rating = ""
        num_reviews_element = product.find("span", {"class": "a-size-base s-underline-text"})
        if num_reviews_element:
            num_reviews = num_reviews_element.get_text(strip=True)
        else:
            num_reviews = ""
        product_url_element = product.find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})['href']
        if product_url_element:
            product_url = product_url_element
        else:
            product_url = ""
        complete_product_url = urljoin(base_url, product_url)
        product_detail_data = scrape_product_detail_page(complete_product_url)
        # Merge data from both functions into a single dictionary
        product_data = {
            "Product name": product_name,
            "Product price": product_price,
            "Product rating": product_rating,
            "Number of reviews": num_reviews,
            "Product URL": product_detail_data["Product URL"],
            "Product Description": product_detail_data["Product Description"],
            "Manufacturer": product_detail_data["Manufacturer"],
            "Description": product_detail_data["Description"],
            "ASIN": product_detail_data["ASIN"],
        }        
        products_list.append(product_data)
    return products_list



def scrape_product_detail_page(product_url):
    response = bypass_captcha(product_url)
    product_detail_soup = BeautifulSoup(response.content, "html.parser")
    
    manufacturer_name = ""
    asin = ""

    description_element = product_detail_soup.find("div", {"class": "a-section a-spacing-medium a-spacing-top-small"})
    if description_element:
        description = description_element.get_text(strip=True)
    else:
        description = ""
    product_description_element = product_detail_soup.find("div", {"class": "a-section feature detail-bullets-wrapper bucket"})
    if product_description_element:
        product_description = product_description_element.get_text(strip=True)
        product_manufacturer_element = product_description_element.find("span", {"class": "a-text-bold"})
        if product_manufacturer_element and "Manufacturer" in product_manufacturer_element.get_text():
            manufacturer_name = product_manufacturer_element.find_next_sibling("span").get_text(strip=True)
        else:
            manufacturer_name = ""
        asin_element = product_detail_soup.find("span", {"class": "a-text-bold"})
        if asin_element and "ASIN" in asin_element.get_text():
            asin = asin_element.get_text(strip=True)
        else:
            asin = ""
    else:
        product_description = ""

    product_detail_data = {
        "Product URL": product_url,
        "Product Description": product_description,
        "Manufacturer": manufacturer_name,
        "Description": description,
        "ASIN": asin,
    }

    return product_detail_data

def save_to_csv(data):
    fields = list(data[0].keys())
    filename = "amazon_products.csv"

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
