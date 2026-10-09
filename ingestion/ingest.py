import requests
from bs4 import BeautifulSoup
import json
from sentence_transformers import SentenceTransformer
from database_connection import get_connection

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
#                   Store extracted content in sections
# ----------------------------------------------------------------------------
headings = article.find_all(["h2","h3"])
sections = []
unhandled_tags = set()
count = 1
# print(headings)
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

        # print("ALL TAG : " , heading_description.name)
        print()
        image = heading_description.find("img")
        if image:
            print("image src: " , image.get("src"))
            print("image alt: ", image.get("alt"))
            print()
            section["Content"].append(image.get("src"))
        elif heading_description.name == "p":
            print("Paragraph : ")
            print(heading_description.getText(" ", strip=True))
            print()
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
            # print("Unhadled HTML Tag : ")
            if heading_description.name == "div":
                print("\nUNHANDLE DIV:")
                print(heading_description.prettify())
            else:
                unhandled_tags.add(heading_description.name)
            

    sections.append(section)

    count += 1

    print("-----------------------------")

print(sections)
print(json.dumps(sections, indent=4, ensure_ascii=False))
print("--------------------------------")
print("Unhandle TAGS : " , unhandled_tags)

#------------------------------------------------------------------------------------
#                       Conbine the content of each section
#------------------------------------------------------------------------------------
print()
for section in sections:
    heading = section["Heading"]
    print("Heading : " , heading)
    full_contents = "\n".join(section["Content"])
    print("Full Contents : " , full_contents)
    print("---------------------------------------")

#------------------------------------------------------------------------------------
#               Split long sections into smaller chunks
#      Example:
#      heading 1 - Chunk 1 (100 words), Chunk 2 (100 words), Chank 3 (50 words)
#      heading 2 - Chunk 1(100 words), Chunk 2 (20 words)
#------------------------------------------------------------------------------------

def create_chunks(text, max_words = 100):
    words = text.split()
    chunk = []

    for i in range(0,len(words), max_words):
        chunk_words = words[i:i + max_words]
        chunk_text = " ".join(chunk_words)
        chunk.append(chunk_text)

    return chunk

all_chunks = []
for section in sections:
    heading = section["Heading"]
    full_contents = "\n".join(section["Content"])

    chunks = create_chunks(full_contents,100)

    for index, chunks_text in enumerate(chunks):
        chunk_data = {
            "section_heading" : heading,
            "chunk_index" : len(all_chunks),
            "content" : chunks_text
        }
        all_chunks.append(chunk_data)

for chunk in all_chunks:
    print("Section : " , chunk["section_heading"])
    print("Chunk Index : " , chunk["chunk_index"])
    print("Content : " , chunk["content"])
    print("------------------------------------")

#------------------------------------------------------------------------------------
#           Generate Embeddings for all the documation chunks
#------------------------------------------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")
for chunk in all_chunks:
    heading = chunk["section_heading"]
    content = chunk["content"]

    # Combine heading and content before embedding
    text_to_embed = heading + "\n" + content

    embedding = model.encode(text_to_embed)
    chunk["embedding"] = embedding.tolist()
    print(chunk["embedding"])

print("Total chunks:" , len(all_chunks))
print("First Embedding Dimentions: ", len(all_chunks[0]["embedding"]))

#------------------------------------------------------------------------------------
#       Save the Chunk into PostgreSQL
#------------------------------------------------------------------------------------
document_id = 1
with get_connection() as conn:
    with conn.cursor() as cursor:
        for chunk in all_chunks:
            cursor.execute(
                """
                INSERT INTO document_chunks
                    (document_id, section_heading, chunk_index, content, embedding)
                VALUES(%s, %s, %s, %s, %s)
                ON CONFLICT(document_id, chunk_index)
                DO UPDATE SET
                    section_heading = EXCLUDED.section_heading,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding
                """,
                (
                    document_id,
                    chunk["section_heading"],
                    chunk["chunk_index"],
                    chunk["content"],
                    chunk["embedding"]
                )
            )
print("Successfully saved : ", len(all_chunks), " chunks")
