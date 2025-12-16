#Article generator from wikidata using llm
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Initialize Gemini model (UNCHANGED)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# -------------------------------------------------
# ONLY THIS FUNCTION IS EXTENDED, NOT REDESIGNED
# -------------------------------------------------

def get_requests(title):
    url = "https://www.wikidata.org/w/api.php"

    # ---------- STEP 1: SEARCH (same purpose as before) ----------
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "list": "search",
        "srsearch": title
    }

    headers = {
        "User-Agent": "WikiDataQueryBot/1.0 (your_email@example.com)",
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data["query"]["search"]:
        return "No Wikidata entity found."

    # Pick first result (same logic level as your snippet usage)
    qid = data["query"]["search"][0]["title"]

    # ---------- STEP 2: FETCH FULL PAGE ----------
    parse_params = {
        "action": "parse",
        "page": qid,
        "prop": "text",
        "format": "json",
        "origin": "*"
    }

    response = requests.get(url, params=parse_params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    raw_html = data["parse"]["text"]["*"]

    # ---------- STEP 3: CLEAN (from your second code) ----------
    soup = BeautifulSoup(raw_html, "html.parser")

    unwanted_selectors = [
        "table", "sup", "style", "script", "noscript", "meta", "img",
        ".wikibase-sitelinksview",
        ".wikibase-entitytermsview",
        ".wikibase-toolbar",
        ".language-list",
        ".mw-editsection"
    ]

    for selector in unwanted_selectors:
        for tag in soup.select(selector):
            tag.decompose()

    clean_text = soup.get_text(separator=" ", strip=True)
    clean_text = " ".join(clean_text.split())

    return clean_text


# -------------------------------------------------
# ORIGINAL CODE BELOW — UNCHANGED
# -------------------------------------------------

def get_ans(title):
    wiki_txt = get_requests(title)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Based on the wikidata contents, what do you understand."),
        ("human", "{question}")
    ])

    chain = prompt | llm

    response = chain.invoke({
        "question": wiki_txt
    })

    return response


if __name__ == "__main__":
    title = input("Enter a wikidata topic to fetch : ")
    article = get_ans(title)
    print("_Article_\n\n", article.content)
