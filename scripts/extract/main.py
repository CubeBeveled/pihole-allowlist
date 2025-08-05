from bs4 import BeautifulSoup
import requests
import re

discourse_url = "https://discourse.pi-hole.net/t/commonly-whitelisted-domains/212.json"


def extract_parentheses(text):
    match = re.search(r"\(([^)]+)\)", text)
    extracted = match.group(1) if match else None

    cleaned = re.sub(r"\s*\([^)]*\)", "", text)

    return cleaned.strip(), extracted


def extract_code_blocks(cooked_html):
    soup = BeautifulSoup(cooked_html, "html.parser")
    code_blocks = soup.find_all("code")
    labeled_blocks = []

    for code in code_blocks:
        section_title = ""
        for prev in code.previous_elements:
            if prev.name == "h2":
                section_title = prev.get_text(strip=True)
                break

        labeled_blocks.append((section_title, code.get_text(strip=True)))

    return labeled_blocks


if __name__ == "__main__":
    response = requests.get(discourse_url)
    response.raise_for_status()

    data = response.json()
    post = data["post_stream"]["posts"][0]

    # all_code = []
    # for post in posts:
    #     code_blocks = extract_code_blocks(post["cooked"])
    #     if code_blocks:
    #         all_code.extend(code_blocks)

    code = extract_code_blocks(post["cooked"])

    for title, block in code:
        block = block.replace("pihole allow ", "").replace(" ", "\n")
        extra = ""

        if ("(") in title and (")") in title:
            title, extra = extract_parentheses(title)
            extra += "\n"

        with open(
            f"adblock/{title.lower().replace("/", "_")}.txt", "wt", encoding="utf-8"
        ) as f:
            f.write(block + extra)
