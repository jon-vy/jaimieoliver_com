import re
import time
import requests
from bs4 import BeautifulSoup
import lxml
from user_agent import generate_user_agent
import asyncio
import aiohttp
import json
from random import randint


total_list = []
def get_url():  # Получаю все ссылки
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "User-Agent": generate_user_agent()
    }
    url = "https://www.jamieoliver.com/recipes/category/course/healthy-dinner-ideas/"
    r = requests.get(url=url, headers=headers)
    html_cod = r.text
    soup = BeautifulSoup(html_cod, "lxml")
    urls = soup.find_all("div", class_="recipe-block")
    links_list = []
    for url in urls:
        link = url.contents[1].attrs["href"]
        links_list.append(f"https://www.jamieoliver.com{link}")
    return links_list


async def gahter_date():
    async with aiohttp.ClientSession() as session:
        links_list = get_url()
        tasks = []  # список задач
        for link in links_list:  # [1:3]
            task = asyncio.create_task(pars_date(session, link))  # создал задачу
            tasks.append(task)  # добавил её в список
        await asyncio.gather(*tasks)


async def pars_date(session, url):
    await asyncio.sleep(randint(1, 5))
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "User-Agent": generate_user_agent()
    }
    async with session.get(url=url, headers=headers) as r:
        html_cod = await r.text()
        soup = BeautifulSoup(html_cod, "lxml")
        try:
            name = soup.find("h1", class_="hidden-xs").text
        except:
            name = "no name"

        try:
            description = soup.find("div", class_="recipe-intro").text.strip()  # Удалил пробелы в начале и конце
            description = " ".join(description.split())  # Удалил все переносы строк
        except:
            description = "no description"

        try:
            photo = soup.find("div", class_="hero-wrapper").find("img").get("src")
        except:
            photo = "no photo"

        try:
            video = soup.find("div", class_="hero-wrapper").find("a").get("data-id")
            video = f"https://youtu.be/{video}"
        except:
            video = "no video"

        try:
            cook_time = soup.find("div", class_="recipe-detail time").contents[2].strip()
        except:
            cook_time = "no cook_time"

        try:
            servings = soup.find("div", class_="recipe-detail serves").contents[2].strip()
        except:
            servings = "no servings"

        try:
            level = soup.find("div", class_=re.compile("recipe-detail difficulty")).contents[2].strip()
        except:
            level = "no level"

        ingredients_list = []
        try:
            ingredients = soup.find("ul", class_="ingred-list").find_all("li")
            for i in range(len(ingredients)):
                ingredient = " ".join(ingredients[i].text.split())
                ingredients_list.append(ingredient)
        except:
            ingredients_list.append("no ingredients")

        directions_list = []
        try:
            directions = soup.find("ol", class_="recipeSteps").find_all("li")
            for i in range(len(directions)):
                direction = directions[i].text
                directions_list.append(direction)
        except AttributeError:
            directions = soup.find("div", class_="method-p").find("div").text.split('\n')
            for i in range(len(directions)):
                if directions[i].replace('\r', '') != "" and '\r':
                    directions_list.append(directions[i].strip())
        except:
            directions_list.append("no directions")

        nutrients_dict = {}
        try:
            nutrients = soup.find("div", class_="nutrition-expanded").find_all("div", class_="inner")
            for i in range(len(nutrients)):
                nutrient_title = nutrients[i].find("span", class_="title").text.strip()
                nutrient_top = nutrients[i].find("span", class_="top").text.strip()
                nutrients_dict[nutrient_title] = nutrient_top
        except:
            nutrients = "no informations"
            nutrients_dict[nutrients] = nutrients

        tips_list = []
        try:
            tips = soup.find("div", class_="tip").text.split("\n")
            for i in range(len(tips)):
                if tips[i].replace('\r', '') != "" and '\r':
                    tips_list.append(tips[i].replace('\r', ''))
        except:
            tips = "no tips"
            tips_list.append(tips)

        total_list.append(
            {
                "name": name,
                "description": description,
                "photo": photo,
                "video": video,
                "link": url,
                "cook_time": cook_time,
                "servings": servings,
                "level": level,
                "ingredients": ingredients_list,
                "directions": directions_list,
                "nutrients": nutrients_dict,
                "tips": tips_list,
            }
        )
    print(f"Обработал {url}")

def main():
    asyncio.get_event_loop().run_until_complete(gahter_date())
    with open("jamieoliver.json", "w") as f:
        json.dump(total_list, f)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Время работы {total_time}")

