import requests
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_books(session, base_url):
    url = base_url + '/catalogue/'
    response = session.get(url + "page-1.html")
    soup = BeautifulSoup(response.text, "lxml")
    links = []

    next_button = soup.find('li', class_='next')
    while next_button:
        for h3 in soup.select('h3 a'):
            links.append(urljoin(url, h3["href"]))
        next_page = urljoin(url, next_button.find('a')['href'])
        response = session.get(next_page)
        soup = BeautifulSoup(response.text, 'lxml')
        next_button = soup.find('li', class_='next')

    for h3 in soup.select('h3 a'):
        links.append(urljoin(url, h3["href"]))

    return links

def get_book_info(session, links):
    books_info = [('Name', 'Price', 'UPC')]
    for link in links:
        response = session.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        name = get_book_name(soup)
        price = get_book_price(soup)
        upc = get_book_upc(soup)
        books_info.append((name, price, upc))
    return books_info

def get_book_name(soup):
    name = soup.find('h1').text
    return name

def get_book_price(soup):
    price = soup.find('p', class_='price_color').text
    return price

def get_book_upc(soup):
    upc = soup.find('th', string='UPC')
    return upc.find_next_sibling('td').text

def write_to_csv(books_info):
    with open('books.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(books_info)


with requests.Session() as session:
    try:
        url = 'https://books.toscrape.com/'
        response = session.get(url, timeout=10)

        if response.status_code == 200:
            start = time.time()

            books = get_books(session, url)
            books_info = get_book_info(session, books)
            write_to_csv(books_info)

            end = time.time()
            elapsed_time = end - start

            print(f"Task took {elapsed_time:.2f}s to complete!")
    except requests.exceptions.RequestException as e:
        print(f"Website request error: {e}")
    except requests.exceptions.Timeout:
        print("Request timed out.")