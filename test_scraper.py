import requests
from bs4 import BeautifulSoup
import re

def scrape():
    with open('hiji.html', 'r', encoding='utf-8') as html_file:
        content = html_file.read()
        output_file = open("hiji.txt", "w", encoding="utf-8")
        output_file.write("Туристическо дружество, град, община, пошенски код, хижи, контакти\n")
        
        soup = BeautifulSoup(content, 'lxml')
        elements = soup.find_all('div', class_='hija')

        for element in elements:
            
            tourist_society = element.find(('font', {'color': '#CC3300'})).text
            output_file.write(tourist_society + ",")

            list_items = element.find_all('li')
            count = 0
            hut_info = ""
            
            name_split = re.split(r'\s', element.find('b').text)
            city = f"{name_split[0]} {name_split[1]}"
           
            municipality = f"{name_split[2]} {name_split[3]}," if len(name_split) >= 4 else "Липсващи данни ,"
            
            output_file.write(city + municipality)

            postal_code = name_split[-1] if any(map(str.isdigit, name_split[-1])) else "Липсващи данни"
            output_file.write(postal_code + ", ")

            for item in list_items:
                if count > 1:
                    hut_info += item.text + ","
                count += 1
            
            if hut_info:
                output_file.write(hut_info)
            else:
                output_file.write("Липсват данни за хижи,")

            contact_info = ""
            for link in element.find_all('a', target="_blank"):
                link_parts = re.split(r'\s', str(link))[1]
                contact_info += f"{link.text}:{link_parts.replace('href=', '').replace('"', '').replace('mailto:', '')},"
            
            output_file.write(contact_info + "\n")

        output_file.close()
