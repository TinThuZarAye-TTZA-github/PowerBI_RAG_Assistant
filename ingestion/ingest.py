import requests
from bs4 import BeautifulSoup

url = "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema"

# download the Webpage
response = requests.get(url)

print("Status Code : ", response.status_code)

# Parse the HTML
parse_html = BeautifulSoup(response.text, "html.parser")

# print(parse_html.prettify())

# find the main h1 title
title = parse_html.find("h1")
print("Title : ", title.text)

# find main in html
main = parse_html.find("main")


# if main:
#     # main_text = main.get_text(separator="\n", strip=True)
#     print("\n ----------- Main Text ------------")
#     print(main.prettify())
# else:
#     print("Main tag not found in the HTML.")

#find artical tag
# article = parse_html.find("article")
# if article:
#     article_text = article.get_text(separator="\n", strip=True)
#     print("\n ----------- Article Text ------------")
#     print(article_text)
# else:
#     print("Article tag not found in the HTML.")

# find the div with class "content"
# we want all the div from html with class "content"

content_div = parse_html.find_all("div", class_="content")
count = 0;
if content_div:
    for i, content in enumerate(content_div):
        # print("\n ----------- Content Div ------------")
        # print(content.prettify())
        # count += 1
        # print("COUNT ", count )
        content_text = content.get_text(separator="\n", strip=True)
        print("\n ----------- Content Text ------------")
        print(content_text)
# Find all div with class="content"
content_div = parse_html.find_all("div", class_="content")
#we already verified the second one is the article
article = content_div[1]


headings = article.find_all(["h1","h2","h3"])

for heading in headings:
   
    print("heading name : " + heading.name + " -----> " )
    print("Heading Text : " + heading.get_text(strip=True)) 

   
# ----------------------------------------------------------------------------
## one heading first rather than trying to build the whole chunking system at once

# fact_table_heading = article.find("h3", string="Fact tables")
# print("Fact Table : " , fact_table_heading.get_text(strip=True)) 

# count = 1
# for i in fact_table_heading.find_next_siblings():
#     if i.name in ["h2","h3"]:
#         break

#     image = i.find("img")
#     if image:
#         print("Fact Table Descrption #" , count , " : IMAGE ")
#         print("image src : " , image.get("src"))
#         print("image alt : " , image.get("alt"))

#     elif i.name == "p":
    
#         text = i.get_text(" ",strip=True)
#         print("Fact Table Description #  " ,  count , ": " , text)

#     count += 1

# ----------------------------------------------------------------------------
headings = article.find_all(["h2","h3"])
sections = []
count = 1
print(headings)
for heading in headings:
    # print("Heading #", count, " : " , heading.get_text(strip=True))
    # print()

    section  = {
        "Heading" : heading.getText(strip=True),
        "Content" : []
    }


    
    for heading_description in heading.find_next_siblings():
        if heading_description.name in ["h2", "h3"]:
            break

        print("ALL TAG : " , heading_description.name)
        print()
        image = heading_description.find("img")
        if image:
            # print("image src: " , image.get("src"))
            # print("image alt: ", image.get("alt"))
            # print()
            section["Content"].append(image.get("src"))
        elif heading_description.name == "p":
            # print("Paragraph : ")
            # print(heading_description.getText(" ", strip=True))
            # print()
            section["Content"].append(heading_description.getText(" ", strip=True))
        elif heading_description.name == "ul":
            print("Bulletpoint : ")
            bullet_text = ""
            for li in heading_description.find_all("li"):
                print(li.getText(" ", strip=True))
                text = li.getText(" ", strip=True)
                if text:
                    bullet_text += ". " + text + "\n"
                
            print()
            section["Content"].append(bullet_text)
        else: 
            print("Unhadled HTML Tag : ")
            print(heading_description.name)

    sections.append(section)
        

    count += 1

    print("-----------------------------")

    print(sections)
        # print("Heading description : " , heading_description.get_text(strip=True))