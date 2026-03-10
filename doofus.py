from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pynput import keyboard
import threading
import re

driver = webdriver.Chrome()

listener = None
typed_chars = []

def on_press(key):
    global typed_chars
    try:
        ch = key.char
        if ch is not None:
            typed_chars.append(ch)
    except AttributeError:
        if key == keyboard.Key.space:
            typed_chars.append(' ')
        elif key == keyboard.Key.backspace:
            if typed_chars:
                typed_chars.pop()
        else:
            pass

def start_listener():
    global listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def predict_email_from_typed(text: str) -> str | None:
    lowered = text.lower()

    m = re.search(r'(\d{7})@?student\.isf\.edu\.hk', lowered)
    if m:
        sid = m.group(1)
        return f"{sid}@student.isf.edu.hk"

    m2 = re.findall(r'\d{7}', lowered)
    if m2:
        sid = m2[-1]
        return f"{sid}@student.isf.edu.hk"

    return None

try:
    k = threading.Thread(target=start_listener, daemon=True)
    k.start()

    driver.get("https://powerschool.isf.edu.hk/")
    print("sign in normally")

    WebDriverWait(driver, 300).until(
        EC.url_contains("https://powerschool.isf.edu.hk/guardian/home.html")
    )

    if listener is not None:
        listener.stop()

    full_typed = ''.join(typed_chars)

    driver.get("https://powerschool.isf.edu.hk/guardian/housetickets.html")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "resultTable"))
    )

    tbody = driver.find_element(By.CSS_SELECTOR, "#resultTable tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    driver.quit()

    predicted_email = predict_email_from_typed(full_typed)
    if predicted_email:
        print("is this your email? (yes/no)", predicted_email)
        i = input("> ")
        if i == "yes":
            print()
        else:
            print("please try again")
            exit()
    else:
        print("we could not predict your email.")
        exit()

    tickets = len(rows)
    doofus = round(tickets * 0.01, 2)
    print("doofus dollars: $" + str(doofus))

except:
    print("error")
