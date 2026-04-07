import time
from playwright.sync_api import sync_playwright

# ================= CONFIG =================
GROUP_NAME = "Support Shift"
SECOND_GROUP_NAME = "TCyS - Support Engineers"

TARGET_KEYWORDS = [
    "shift","cover","swap","duty","replace","rotation",
    "anyone","someone","anybody","volunteer",
    "can","could","please","need","available","free",
    "take","help","join","handle","sub",
    "today","tomorrow","urgent","asap"
]

REPLY_TEXT = "Ok"
NOTIFY_MESSAGE = "Abhijith P A in"

USER_DATA_DIR = "/home/ubuntu/pw-user-data"  # AWS path
LOOP_DELAY = 1
# ==========================================


def contains_keywords(text):
    text = text.lower()
    return any(k in text for k in TARGET_KEYWORDS)


def open_chat(page, name):
    search = page.locator("div[contenteditable='true']").first
    search.click()
    search.fill("")
    search.type(name)
    time.sleep(1)
    page.keyboard.press("Enter")


def send_message(page, text):
    box = page.locator("div[contenteditable='true'][data-tab='10']")
    box.click()
    box.type(text)
    page.keyboard.press("Enter")


def get_last_incoming_message(page):
    msgs = page.locator("div.message-in span.selectable-text")
    count = msgs.count()
    if count == 0:
        return None
    return msgs.nth(count - 1).inner_text()


def has_reaction(page):
    reactions = page.locator("div.message-out [data-testid='reactions-row']")
    return reactions.count() > 0


# ================= MAIN =================
with sync_playwright() as p:

    browser = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=True,   # 🔥 set False first time to scan QR
        args=["--no-sandbox"]
    )

    page = browser.new_page()
    page.goto("https://web.whatsapp.com")

    print("🔐 Waiting for WhatsApp login...")
    page.wait_for_selector("div[contenteditable='true']", timeout=0)

    print(f"✅ Opening group: {GROUP_NAME}")
    open_chat(page, GROUP_NAME)

    last_message = ""

    print("🚀 Monitoring messages...")

    while True:
        try:
            msg = get_last_incoming_message(page)

            if msg and msg != last_message:
                print("📩 New message:", msg)
                last_message = msg

                if contains_keywords(msg):
                    print("⚡ Keyword matched → replying")

                    send_message(page, REPLY_TEXT)

                    # ⏳ wait for reaction (max 5 min)
                    print("⏳ Waiting for reaction...")
                    reaction_detected = False
                    start = time.time()

                    while time.time() - start < 300:
                        if has_reaction(page):
                            print("🔥 Reaction detected!")
                            reaction_detected = True
                            break
                        time.sleep(2)

                    if reaction_detected:
                        print(f"📢 Switching to {SECOND_GROUP_NAME}")
                        open_chat(page, SECOND_GROUP_NAME)
                        time.sleep(1)

                        send_message(page, NOTIFY_MESSAGE)
                        print("✅ Notification sent")

                        # 🔁 go back
                        open_chat(page, GROUP_NAME)

                    else:
                        print("⚠️ No reaction received")

        except Exception as e:
            print("❌ Error:", e)

        time.sleep(LOOP_DELAY)
