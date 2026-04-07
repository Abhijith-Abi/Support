import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LOOP_DELAY = 0.0
GROUP_NAME = "Support Shift"
TARGET_KEYWORDS = [
    # Core shift words
    "shift", "cover", "swap", "duty", "replace", "rotation",
    # Who
    "anyone", "someone", "somebody", "anybody", "volunteers", "volunteer",
    # Ask/request words
    "can", "could", "would", "will", "please", "need", "want",
    "willing", "able", "available", "free", "open",
    # Action words
    "take", "step", "pick", "fill", "help", "join", "do",
    "handle", "manage", "sub", "substitute",
    # Context
    "me", "my", "over", "up", "for", "today",
    "tonight", "tomorrow", "morning", "evening", "night",
    "urgent", "asap", "immediately", "emergency",
]  
REPLY_TEXT = "Ok"
SECOND_GROUP_NAME = "TCyS - Support Engineers"  # TODO: Replace with actual group name
# SECOND_GROUP_NAME = "Me"
NOTIFY_MESSAGE = "Abhijith P A in"

options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=chrome-data")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://web.whatsapp.com")
print("Scan QR Code and press ENTER...")
input()

wait = WebDriverWait(driver, 30)

search_box = wait.until(
    EC.presence_of_element_located((By.XPATH, '//div[@id="side"]//input[@data-tab="3"]'))
)
search_box.click()
search_box.send_keys(GROUP_NAME)
time.sleep(1)
search_box.send_keys(Keys.ENTER)

def get_latest_message_info():
    try:
        return driver.execute_script('''
            var msgs = document.querySelectorAll('div.message-in');
            if (msgs.length === 0) return {id: "", text: ""};
            var lastMsg = msgs[msgs.length - 1];
            
            var idAttr = lastMsg.getAttribute('data-id');
            var p = lastMsg.parentElement;
            while(!idAttr && p && p !== document.body) {
                idAttr = p.getAttribute('data-id');
                p = p.parentElement;
            }
            if (!idAttr) idAttr = "msg_" + msgs.length;
            
            var textSpan = lastMsg.querySelector('span.selectable-text[dir="ltr"]') || lastMsg.querySelector('span[dir="ltr"]');
            var text = textSpan ? textSpan.innerText.trim() : "";
            
            return {id: idAttr + "_" + text, text: text};
        ''')
    except Exception:
        return None

def is_target_chat_active():
    try:
        return driver.execute_script('''
            var main = document.querySelector('#main');
            if (!main) return false;
            var header = main.querySelector('header');
            if (header && header.innerText.includes(arguments[0])) return true;
            return false;
        ''', GROUP_NAME)
    except Exception:
        return False

def check_sidebar_for_message(target_group):
    try:
        return driver.execute_script('''
            var groupName = arguments[0];
            var keywords = arguments[1];
            var spans = document.querySelectorAll('span[title="' + groupName + '"]');
            for(var i=0; i<spans.length; i++) {
                var row = spans[i].closest('div[role="listitem"]');
                if(!row) continue;
                
                var hasUnread = row.querySelector('[aria-label*="unread"]') != null;
                var rowText = row.innerText.toLowerCase();
                
                // For sidebar checking, we might just want to open if it's the target group 
                // and has unread, keywords are optional here or used in the main loop
                if(hasUnread) {
                    spans[i].dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true, view: window}));
                    spans[i].click();
                    return true;
                }
            }
            return false;
        ''', target_group, TARGET_KEYWORDS)
    except Exception:
        return False

def switch_to_group(group_name):
    print(f"Switching to group: {group_name}")
    try:
        search_box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="side"]//input[@data-tab="3"]'))
        )
        search_box.click()
        # Select all and delete to clear
        search_box.send_keys(Keys.COMMAND + "a")
        search_box.send_keys(Keys.BACKSPACE)
        search_box.send_keys(group_name)
        time.sleep(1)
        search_box.send_keys(Keys.ENTER)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Error switching to group {group_name}: {e}")
        return False

def send_message_js(message):
    script = """
    var reply = arguments[0];
    var box = document.querySelector('div[contenteditable="true"][data-tab="10"]') || document.querySelector('div[title="Type a message"]');
    if(box) {
        box.focus();
        document.execCommand('insertText', false, reply);
        box.dispatchEvent(new Event('input', {bubbles: true}));
        setTimeout(function() {
            var icon = document.querySelector('span[data-icon="send"]');
            if(icon) {
                var btn = icon.closest('button') || icon.closest('div[role="button"]') || icon.parentNode;
                if(btn) btn.click();
            } else {
                box.dispatchEvent(new KeyboardEvent('keydown', {bubbles: true, cancelable: true, keyCode: 13, key: 'Enter'}));
            }
        }, 10);
        return true;
    }
    return false;
    """
    return driver.execute_script(script, message)

def has_reaction_on_last_out():
    try:
        return driver.execute_script('''
            var msgs = document.querySelectorAll('div.message-out');
            if (msgs.length === 0) return false;
            var lastOut = msgs[msgs.length - 1];
            // Refined reaction selectors including button and aria-labels
            var reaction = lastOut.querySelector('button[aria-label*="reaction"], [aria-label*="reaction"], [data-testid="reactions-row"], span[data-testid="reaction-count"]');
            return !!reaction;
        ''')
    except Exception:
        return False

print("Waiting for chat history to load...")
last_message_id = ""
attempts = 0
while not last_message_id and attempts < 30:
    info = get_latest_message_info()
    if info and info.get("id"):
        last_message_id = info.get("id")
        print(f"Baseline message loaded: '{info.get('text')[:20]}...'")
    else:
        time.sleep(1)
        attempts += 1

print("Monitoring instantly for NEW messages...")

while True:
    try:
        # Optimized monitoring script: combines active chat check and message detection
        script = """
        var groupName = arguments[0];
        var keywords = arguments[1].map(function(k){ return k.toLowerCase(); });
        var reply = arguments[2];
        var lastMsgId = arguments[3];
        
        // 1. Check if the correct chat is active
        var main = document.querySelector('#main');
        if (!main) return {id: lastMsgId, replied: false, active: false};
        var header = main.querySelector('header');
        if (!header || !header.innerText.includes(groupName)) return {id: lastMsgId, replied: false, active: false};
        
        // 2. High-speed message detection: only look at the VERY last row
        var rows = document.querySelectorAll('div[role="row"]');
        if(rows.length === 0) return {id: lastMsgId, replied: false, active: true};
        var lastRow = rows[rows.length - 1];
        
        // Skip messages sent BY US (outbound)
        if(lastRow.querySelector('.message-out')) return {id: lastMsgId, replied: false, active: true};
        
        // 3. Extract and compare ID/Text
        var idAttr = lastRow.getAttribute('data-id');
        var textEl = lastRow.querySelector('.copyable-text') || lastRow.querySelector('span.selectable-text');
        var text = textEl ? textEl.innerText.trim() : "";
        var finalId = (idAttr || "row_" + rows.length) + "_" + text;
        
        if(finalId === lastMsgId) return {id: finalId, replied: false, active: true};
        
        // 4. New incoming message detected!
        var msgText = text.toLowerCase();
        if(keywords.some(function(k){ return msgText.includes(k); })) {
            var box = document.querySelector('#main div[role="textbox"]');
            if(box) {
                box.focus();
                document.execCommand('insertText', false, reply);
                box.dispatchEvent(new Event('input', {bubbles: true}));
                
                // Advanced Retry-and-Send logic to handle React lag
                var send = function() {
                    var btn = document.querySelector('button[aria-label="Send"]') || 
                              document.querySelector('span[data-icon="send"]')?.closest('button');
                    if(btn) {
                        btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                        btn.click();
                    } else {
                        // Retry for up to 500ms (10 attempts)
                        if (!window.__sendRetry) window.__sendRetry = 0;
                        if (window.__sendRetry < 10) {
                            window.__sendRetry++;
                            setTimeout(send, 50);
                        } else {
                            window.__sendRetry = 0;
                        }
                    }
                };
                send();
                return {id: finalId, replied: true, active: true};
            }
        }
        return {id: finalId, replied: false, active: true};
        """
        
        result = driver.execute_script(script, GROUP_NAME, TARGET_KEYWORDS, REPLY_TEXT, last_message_id)
        
        if result and result.get("active"):
            if result.get("id") != last_message_id:
                last_message_id = result.get("id")
                if result.get("replied"):
                    print(f"Replied instantly to target message.")
                    print(f"Waiting for reaction (like/reaction)...")
                    
                    reaction_detected = False
                    start_wait = time.time()
                    while time.time() - start_wait < 300: 
                        if has_reaction_on_last_out():
                            print("Reaction detected! Proceeding to notify second group.")
                            reaction_detected = True
                            break
                        if not is_target_chat_active():
                            print("Left target group while waiting. Aborting notification.")
                            break
                        time.sleep(1)
                    
                    if reaction_detected:
                        if SECOND_GROUP_NAME and SECOND_GROUP_NAME != "NAME_OF_SECOND_GROUP":
                            time.sleep(0.5)
                            if switch_to_group(SECOND_GROUP_NAME):
                                time.sleep(1)
                                if send_message_js(NOTIFY_MESSAGE):
                                    print(f"Sent notification to {SECOND_GROUP_NAME}")
                                    time.sleep(1)
                                switch_to_group(GROUP_NAME)
                                time.sleep(1)
                                info = get_latest_message_info()
                                if info and info.get("id"):
                                    last_message_id = info.get("id")
                    else:
                        print("Waiting timed out or group switched. No notification sent.")
        else:
            if check_sidebar_for_message(GROUP_NAME):
                time.sleep(0.5)

    except Exception as e:
        print(f"Error checking/sending: {e}")

    time.sleep(LOOP_DELAY)
