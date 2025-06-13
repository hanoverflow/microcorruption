from playwright.sync_api import sync_playwright
import time

# it looks like a lot of the page gets loaded from javascript
# we have to use a browser, gross

base_url = "https://microcorruption.com"

def handle_dialog(dialog):
    dialog.accept()

def load_page(page, url):
    page.on("dialog", handle_dialog)
    page.goto(url)
    # we should use some wait for selector but it doesn't work and the sleep timer does
    # page.wait_for_selector("#cities")
    time.sleep(0.3)
    return page

def fetch_challenge_list(page):
    page = load_page(page, f"{base_url}/map")
    challenge_elements = page.query_selector_all("#cities > section > ul > li > a")
    challenge_dict = {}
    for element in challenge_elements:
        href = element.get_attribute("href")
        text = element.inner_text()
        challenge_dict[text] = href

    return challenge_dict

def extract_challenge(page, challenge_dict, challenge):
    # TODO: Add better error handling
    if challenge not in challenge_dict:
        print(f"Challenge {challenge} not in {challenge_dict}")
        exit(1)
    load_page(page, f"{base_url}{challenge_dict[challenge]}")
    asm_elems = page.query_selector_all("#asmbox > div")
    asm = []
    for i in asm_elems:
        insn = {
            "id": i.get_attribute("id"),
            "class": i.get_attribute("class"),
            "text": i.inner_text(),
        }
        asm.append(insn)
    return asm

if __name__ == "__main__":
    # TODO: include a CLI that lets you list challenges or select a particular challenge
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        challenge_list = fetch_challenge_list(page)
        challenge_asm = extract_challenge(page, challenge_list, "Churchill")

    for insn in challenge_asm:
        print(insn["text"])
