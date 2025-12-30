# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import csv
# import time
# from pathlib import Path

# URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

# STATE_NAME = "GUJARAT"
# DISTRICT_NAME = "AHMEDABAD"
# OUT_CSV = "pmsuryaghar_demo_apply.csv"

# HEADLESS = False
# SLOW_MO_MS = 100
# WAIT_MS = 60_000

# # How long to wait for dropdown options to appear after opening
# OPTIONS_WAIT_MS = 20_000

# # How many times to "refresh + retry" if dropdown opens but options are empty
# MAX_REFRESH_RETRIES = 3


# # -------------------------
# # Debug dump
# # -------------------------
# def dump_debug(page, prefix="debug"):
#     ts = int(time.time())
#     out_dir = Path("pw_debug")
#     out_dir.mkdir(exist_ok=True)
#     shot = out_dir / f"{prefix}_{ts}.png"
#     html = out_dir / f"{prefix}_{ts}.html"
#     try:
#         page.screenshot(path=str(shot), full_page=True)
#     except Exception:
#         pass
#     try:
#         html.write_text(page.content(), encoding="utf-8")
#     except Exception:
#         pass
#     print(f"[DEBUG] Saved: {shot} and {html}")


# # -------------------------
# # CSV helper
# # -------------------------
# def write_rows_csv(path, rows, header):
#     if not rows:
#         return
#     file_exists = Path(path).exists()
#     with open(path, "a", newline="", encoding="utf-8-sig") as f:
#         w = csv.DictWriter(f, fieldnames=header)
#         if not file_exists:
#             w.writeheader()
#         for r in rows:
#             w.writerow(r)


# # -------------------------
# # Hard refresh (Ctrl+Shift+R-ish)
# # -------------------------
# def hard_refresh(page, url: str, tries: int = 2) -> bool:
#     for _ in range(tries):
#         # 1) reload
#         try:
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1200)
#             return True
#         except Exception:
#             pass

#         # 2) cache-busting goto
#         try:
#             bust = int(time.time() * 1000)
#             page.goto(f"{url}?cb={bust}", wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)
#             return True
#         except Exception:
#             pass

#         # 3) clear storage + unregister service workers + reload
#         try:
#             page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
#             page.evaluate(
#                 """
#                 async () => {
#                   if (navigator.serviceWorker) {
#                     const regs = await navigator.serviceWorker.getRegistrations();
#                     for (const r of regs) await r.unregister();
#                   }
#                 }
#                 """
#             )
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)
#             return True
#         except Exception:
#             pass

#     return False


# def wait_spa_ready(page):
#     try:
#         page.wait_for_load_state("domcontentloaded", timeout=WAIT_MS)
#     except Exception:
#         pass
#     try:
#         page.wait_for_load_state("networkidle", timeout=20_000)
#     except Exception:
#         pass
#     page.wait_for_timeout(1200)


# # -------------------------
# # Dropdown handling (robust)
# # -------------------------
# OPTION_CONTAINER_SELECTORS = [
#     # ng-select (very common in Angular)
#     "ng-dropdown-panel .ng-option",
#     ".ng-dropdown-panel .ng-option",
#     "ng-dropdown-panel [role='option']",
#     ".ng-dropdown-panel [role='option']",

#     # overlay-based UIs
#     ".cdk-overlay-container [role='option']",
#     ".cdk-overlay-container .ng-option",
#     "[role='listbox'] [role='option']",

#     # generic fallbacks (kept later)
#     ".dropdown-menu.show [role='option']",
#     ".dropdown-menu.show li",
# ]

# SEARCH_INPUT_SELECTORS = [
#     "ng-dropdown-panel input[type='text']",
#     ".ng-dropdown-panel input[type='text']",
#     ".cdk-overlay-container input[type='text']",
#     "input[placeholder*='Search' i]",
#     "input[type='search']",
# ]


# def close_dropdown(page):
#     try:
#         page.keyboard.press("Escape")
#     except Exception:
#         pass
#     page.wait_for_timeout(250)


# def click_placeholder_dropdown(page, placeholder_text: str):
#     """
#     Clicks the placeholder like 'Select State' / 'Select District' as in your screenshot.
#     """
#     loc = page.get_by_text(placeholder_text, exact=False).first
#     loc.wait_for(state="visible", timeout=WAIT_MS)
#     loc.click(force=True)


# def _any_options_count(page) -> int:
#     total = 0
#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             total += page.locator(sel).count()
#         except Exception:
#             pass
#     return total


# def wait_for_any_options(page, timeout_ms: int) -> bool:
#     """
#     Wait until any dropdown options exist (not necessarily your target text).
#     """
#     deadline = time.time() + timeout_ms / 1000
#     last = -1
#     while time.time() < deadline:
#         c = _any_options_count(page)
#         if c > 0:
#             return True
#         if c != last:
#             last = c
#         page.wait_for_timeout(250)
#     return False


# def _type_in_search_if_present(page, text: str):
#     for sel in SEARCH_INPUT_SELECTORS:
#         inp = page.locator(sel).first
#         try:
#             if inp.count() > 0 and inp.is_visible():
#                 inp.click()
#                 inp.fill("")  # clear
#                 inp.type(text, delay=40)
#                 page.wait_for_timeout(300)
#                 return
#         except Exception:
#             continue


# def click_option_by_text_strict(page, option_text: str) -> bool:
#     """
#     Clicks option text ONLY inside likely dropdown option containers (not whole page).
#     Returns True if clicked.
#     """
#     # Try ARIA options first
#     try:
#         opt = page.get_by_role("option", name=option_text).first
#         if opt.count() > 0 and opt.is_visible():
#             opt.click(force=True)
#             return True
#     except Exception:
#         pass

#     # Then try known option containers
#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             opt = page.locator(sel).filter(has_text=option_text).first
#             if opt.count() > 0:
#                 opt.scroll_into_view_if_needed()
#                 opt.wait_for(state="visible", timeout=3000)
#                 opt.click(force=True)
#                 return True
#         except Exception:
#             continue

#     return False


# def open_dropdown_and_select_with_refresh(page, placeholder: str, value_text: str):
#     """
#     Fix for your exact issue:
#     - Dropdown opens but options empty
#     - Refresh needed, then options appear
#     We handle it with retries + hard refresh.
#     """
#     for attempt in range(1, MAX_REFRESH_RETRIES + 1):
#         # open dropdown
#         click_placeholder_dropdown(page, placeholder)

#         # wait for options to load
#         ok = wait_for_any_options(page, OPTIONS_WAIT_MS)

#         if not ok:
#             # sometimes typing triggers fetching/filtering
#             _type_in_search_if_present(page, value_text)
#             ok = wait_for_any_options(page, 6_000)

#         # try click the option
#         if ok and click_option_by_text_strict(page, value_text):
#             page.wait_for_timeout(700)
#             return

#         # If reached here, dropdown opened but options didn't load OR target not found.
#         close_dropdown(page)

#         print(f"[WARN] '{placeholder}' options not ready / '{value_text}' not found. Refresh retry {attempt}/{MAX_REFRESH_RETRIES}")
#         if not hard_refresh(page, URL, tries=2):
#             raise RuntimeError("Hard refresh failed while recovering dropdown empty state.")
#         wait_spa_ready(page)

#     raise RuntimeError(f"Could not select '{value_text}' from '{placeholder}' even after refresh retries.")


# def click_apply(page):
#     btn = page.get_by_role("button", name="Apply").first
#     if btn.count() == 0:
#         btn = page.locator("button:has-text('Apply')").first
#     btn.wait_for(state="visible", timeout=WAIT_MS)
#     btn.click(force=True)


# # -------------------------
# # Main
# # -------------------------
# def main():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
#         context = browser.new_context(
#             viewport={"width": 1440, "height": 820},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             wait_spa_ready(page)

#             # Ensure filter panel is visible; else refresh once
#             try:
#                 page.get_by_text("Filters", exact=False).first.wait_for(timeout=12_000)
#             except PWTimeoutError:
#                 print("[WARN] Filters not visible -> hard refresh")
#                 if not hard_refresh(page, URL, tries=2):
#                     raise RuntimeError("Page not loading after hard refresh.")
#                 wait_spa_ready(page)

#             # ---- Select State + District (with refresh-retry logic) ----
#             open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
#             open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)

#             # ---- Click Apply ----
#             click_apply(page)
#             page.wait_for_timeout(2500)

#             # Demo CSV output (just record that apply worked)
#             rows = [{"state": STATE_NAME, "district": DISTRICT_NAME, "status": "applied"}]
#             write_rows_csv(OUT_CSV, rows, header=["state", "district", "status"])

#             print(f"DONE ✅ Applied State={STATE_NAME}, District={DISTRICT_NAME}. Saved -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="pmsuryaghar_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main()



# ---------------------------------------------------------------------------------updated code below---------------------------------------------------------------------------------

# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import csv
# import time
# import re
# from pathlib import Path

# URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

# STATE_NAME = "GUJARAT"
# DISTRICT_NAME = "Ahmedabad"   # case-insensitive matching is used
# OUT_CSV = "pmsuryaghar_guj_ahd_vendors.csv"

# # VIEW
# HEADLESS = False
# SLOW_MO_MS = 80
# WAIT_MS = 60_000

# # Dropdown empty -> refresh retry behavior
# OPTIONS_WAIT_MS = 20_000
# MAX_REFRESH_RETRIES = 4

# # Load more
# LOAD_MORE_WAIT_MS = 25_000
# MAX_LOAD_MORE_CLICKS = 300
# MAX_LOAD_MORE_STUCK = 3

# CSV_HEADER = [
#     "state",
#     "district",
#     "emails",
#     "contact_numbers",
#     "total_installed_capacity_kwp",
#     "no_of_installations",
# ]


# # -------------------------
# # Debug dump
# # -------------------------
# def dump_debug(page, prefix="debug"):
#     ts = int(time.time())
#     out_dir = Path("pw_debug")
#     out_dir.mkdir(exist_ok=True)
#     shot = out_dir / f"{prefix}_{ts}.png"
#     html = out_dir / f"{prefix}_{ts}.html"
#     try:
#         page.screenshot(path=str(shot), full_page=True)
#     except Exception:
#         pass
#     try:
#         html.write_text(page.content(), encoding="utf-8")
#     except Exception:
#         pass
#     print(f"[DEBUG] Saved: {shot} and {html}")


# # -------------------------
# # CSV helpers
# # -------------------------
# def append_rows_csv(path, rows):
#     if not rows:
#         return
#     file_exists = Path(path).exists()
#     with open(path, "a", newline="", encoding="utf-8-sig") as f:
#         w = csv.DictWriter(f, fieldnames=CSV_HEADER)
#         if not file_exists:
#             w.writeheader()
#         for r in rows:
#             w.writerow(r)


# # -------------------------
# # Hard refresh (Ctrl+Shift+R-ish)
# # -------------------------
# def hard_refresh(page, url: str, tries: int = 2) -> bool:
#     for _ in range(tries):
#         try:
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1200)
#             return True
#         except Exception:
#             pass

#         try:
#             bust = int(time.time() * 1000)
#             page.goto(f"{url}?cb={bust}", wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)
#             return True
#         except Exception:
#             pass

#         try:
#             page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
#             page.evaluate(
#                 """
#                 async () => {
#                   if (navigator.serviceWorker) {
#                     const regs = await navigator.serviceWorker.getRegistrations();
#                     for (const r of regs) await r.unregister();
#                   }
#                 }
#                 """
#             )
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)
#             return True
#         except Exception:
#             pass

#     return False


# def wait_spa_ready(page):
#     try:
#         page.wait_for_load_state("domcontentloaded", timeout=WAIT_MS)
#     except Exception:
#         pass
#     try:
#         page.wait_for_load_state("networkidle", timeout=20_000)
#     except Exception:
#         pass
#     page.wait_for_timeout(1000)


# # -------------------------
# # Dropdown handling (Angular overlay)
# # -------------------------
# OPTION_CONTAINER_SELECTORS = [
#     "ng-dropdown-panel .ng-option",
#     ".ng-dropdown-panel .ng-option",
#     "ng-dropdown-panel [role='option']",
#     ".ng-dropdown-panel [role='option']",
#     ".cdk-overlay-container [role='option']",
#     ".cdk-overlay-container .ng-option",
#     "[role='listbox'] [role='option']",
# ]

# SEARCH_INPUT_SELECTORS = [
#     "ng-dropdown-panel input[type='text']",
#     ".ng-dropdown-panel input[type='text']",
#     ".cdk-overlay-container input[type='text']",
#     "input[placeholder*='Search' i]",
#     "input[type='search']",
# ]


# def close_dropdown(page):
#     try:
#         page.keyboard.press("Escape")
#     except Exception:
#         pass
#     page.wait_for_timeout(250)


# def click_placeholder_dropdown(page, placeholder_text: str):
#     loc = page.get_by_text(placeholder_text, exact=False).first
#     loc.wait_for(state="visible", timeout=WAIT_MS)
#     loc.click(force=True)


# def _any_options_count(page) -> int:
#     total = 0
#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             total += page.locator(sel).count()
#         except Exception:
#             pass
#     return total


# def wait_for_any_options(page, timeout_ms: int) -> bool:
#     deadline = time.time() + timeout_ms / 1000
#     while time.time() < deadline:
#         if _any_options_count(page) > 0:
#             return True
#         page.wait_for_timeout(250)
#     return False


# def _type_in_search_if_present(page, text: str):
#     for sel in SEARCH_INPUT_SELECTORS:
#         inp = page.locator(sel).first
#         try:
#             if inp.count() > 0 and inp.is_visible():
#                 inp.click()
#                 inp.fill("")
#                 inp.type(text, delay=35)
#                 page.wait_for_timeout(300)
#                 return
#         except Exception:
#             continue


# def click_option_by_text_case_insensitive(page, option_text: str) -> bool:
#     """
#     Click option where its visible text matches case-insensitively.
#     This avoids 'Ahmedabad' vs 'AHMEDABAD' issues.
#     """
#     wanted = option_text.strip().lower()

#     # First try ARIA option list
#     try:
#         opts = page.get_by_role("option").all()
#         for opt in opts:
#             try:
#                 t = (opt.inner_text() or "").strip()
#                 if t.lower() == wanted and opt.is_visible():
#                     opt.click(force=True)
#                     return True
#             except Exception:
#                 continue
#     except Exception:
#         pass

#     # Then try known option containers
#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             items = page.locator(sel)
#             n = items.count()
#             for i in range(n):
#                 it = items.nth(i)
#                 t = (it.inner_text() or "").strip()
#                 if t.lower() == wanted:
#                     it.scroll_into_view_if_needed()
#                     it.wait_for(state="visible", timeout=4000)
#                     it.click(force=True)
#                     return True
#         except Exception:
#             continue

#     return False


# def open_dropdown_and_select_with_refresh(page, placeholder: str, value_text: str):
#     """
#     Your real behavior: dropdown opens but empty -> refresh -> options appear.
#     """
#     for attempt in range(1, MAX_REFRESH_RETRIES + 1):
#         click_placeholder_dropdown(page, placeholder)

#         ok = wait_for_any_options(page, OPTIONS_WAIT_MS)
#         if not ok:
#             _type_in_search_if_present(page, value_text)
#             ok = wait_for_any_options(page, 6000)

#         if ok and click_option_by_text_case_insensitive(page, value_text):
#             page.wait_for_timeout(600)
#             return

#         close_dropdown(page)
#         print(f"[WARN] '{placeholder}' empty / '{value_text}' not found. Refresh retry {attempt}/{MAX_REFRESH_RETRIES}")
#         if not hard_refresh(page, URL, tries=2):
#             raise RuntimeError("Hard refresh failed while recovering dropdown empty state.")
#         wait_spa_ready(page)

#     raise RuntimeError(f"Could not select '{value_text}' from '{placeholder}' after refresh retries.")


# def click_apply(page):
#     btn = page.get_by_role("button", name="Apply").first
#     if btn.count() == 0:
#         btn = page.locator("button:has-text('Apply')").first
#     btn.wait_for(state="visible", timeout=WAIT_MS)
#     btn.click(force=True)


# # -------------------------
# # Vendor list: PrimeNG Accordion (important fix)
# # -------------------------
# def vendor_header_actions(page):
#     """
#     PrimeNG header action ids look like pn_id_XX_header_action.
#     These are the CLICKABLE toggles. We filter to only vendor rows by 'NO. OF INSTALLATIONS'.
#     """
#     loc = page.locator("[id$='_header_action']").filter(has_text="NO. OF INSTALLATIONS")
#     return loc


# def find_load_more_button(page):
#     return page.locator(":is(button,a,div):has-text('Load More'), :is(button,a,div):has-text('LOAD MORE')").first


# def load_all_vendors(page):
#     """
#     Click Load More until it disappears OR count stops increasing for a few tries.
#     """
#     headers = vendor_header_actions(page)
#     prev_count = headers.count()
#     print(f"[INFO] initial vendor rows (header_action count) = {prev_count}")

#     stuck = 0
#     for _ in range(MAX_LOAD_MORE_CLICKS):
#         btn = find_load_more_button(page)

#         try:
#             if btn.count() == 0 or not btn.is_visible():
#                 print("[INFO] Load More not visible -> done loading")
#                 return
#         except Exception:
#             print("[INFO] Load More not accessible -> done loading")
#             return

#         # bring button into view
#         try:
#             btn.scroll_into_view_if_needed()
#         except Exception:
#             page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
#             page.wait_for_timeout(500)

#         try:
#             btn.click(force=True)
#         except Exception:
#             # last resort
#             page.locator("button:has-text('Load More')").first.click(force=True)

#         # wait for count increase
#         deadline = time.time() + LOAD_MORE_WAIT_MS / 1000
#         grew = False
#         while time.time() < deadline:
#             page.wait_for_timeout(500)
#             headers = vendor_header_actions(page)
#             cur = headers.count()
#             if cur > prev_count:
#                 print(f"[LOAD MORE] {prev_count} -> {cur}")
#                 prev_count = cur
#                 grew = True
#                 stuck = 0
#                 break

#         if not grew:
#             stuck += 1
#             print(f"[WARN] Load More clicked but vendor count did not increase (stuck={stuck}/{MAX_LOAD_MORE_STUCK})")
#             if stuck >= MAX_LOAD_MORE_STUCK:
#                 print("[INFO] stopping load-more due to repeated no-growth")
#                 return


# # -------------------------
# # Extraction: get content by aria-labelledby
# # -------------------------
# def normalize_spaces(s: str) -> str:
#     return re.sub(r"[ \t]+", " ", (s or "").strip())


# def _norm_label(s: str) -> str:
#     return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


# LABEL_EMAILS = ["EMAIL(S)", "EMAILS", "EMAIL"]
# LABEL_PHONES = ["CONTACT NUMBER(S)", "CONTACT NUMBERS", "CONTACT NUMBER"]
# LABEL_CAP = ["TOTAL INSTALLED CAPACITY (KWP)", "TOTAL INSTALLED CAPACITY (kWp)"]
# LABEL_INST = ["NO. OF INSTALLATIONS", "NO OF INSTALLATIONS", "NO. OF INSTALLATION"]

# ALL_LABELS_NORM = set(_norm_label(x) for x in (LABEL_EMAILS + LABEL_PHONES + LABEL_CAP + LABEL_INST))


# def value_after_label(lines, label_variants):
#     label_norms = set(_norm_label(x) for x in label_variants)

#     for i, line in enumerate(lines):
#         if not line:
#             continue
#         n = _norm_label(line)

#         for lv in label_variants:
#             nl = _norm_label(lv)
#             if n == nl or n.startswith(nl):
#                 # same-line remainder
#                 m = re.match(rf"^{re.escape(lv)}\s*[:\-]?\s*(.*)$", line, flags=re.I)
#                 if m:
#                     rem = normalize_spaces(m.group(1))
#                     if rem:
#                         return rem

#                 # next lines until next label
#                 vals = []
#                 j = i + 1
#                 while j < len(lines):
#                     nxt = lines[j].strip()
#                     if not nxt:
#                         j += 1
#                         continue
#                     if _norm_label(nxt) in ALL_LABELS_NORM:
#                         break
#                     if any(_norm_label(nxt).startswith(x) for x in ALL_LABELS_NORM):
#                         break
#                     vals.append(nxt)
#                     if len(vals) >= 6:
#                         break
#                     j += 1

#                 return normalize_spaces("; ".join(vals))

#     return ""


# def pick_number(s: str) -> str:
#     m = re.search(r"(\d[\d,]*)", s or "")
#     return m.group(1).replace(",", "") if m else (s or "")


# def safe_click_header(page, header_loc):
#     """
#     Robust click: center scroll + retry.
#     """
#     # center it
#     try:
#         header_loc.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest'})")
#     except Exception:
#         try:
#             header_loc.scroll_into_view_if_needed()
#         except Exception:
#             pass

#     page.wait_for_timeout(100)

#     # click
#     try:
#         header_loc.click(force=True)
#         return
#     except Exception:
#         # one more attempt after window scroll
#         try:
#             box = header_loc.bounding_box()
#             if box:
#                 page.evaluate("(y)=>window.scrollTo(0,y)", max(0, int(box["y"]) - 200))
#                 page.wait_for_timeout(150)
#         except Exception:
#             pass
#         header_loc.click(force=True)


# def ensure_expanded_by_aria(page, header_action):
#     """
#     PrimeNG header_action usually has aria-expanded=true/false.
#     Expand if needed.
#     """
#     try:
#         aria = header_action.get_attribute("aria-expanded")
#         if aria is not None and aria.strip().lower() == "true":
#             return
#     except Exception:
#         pass

#     safe_click_header(page, header_action)


# def content_region_for_header(page, header_action_id: str):
#     """
#     PrimeNG content region uses aria-labelledby='<header_action_id>'
#     """
#     return page.locator(f"div[role='region'][aria-labelledby='{header_action_id}']").first


# def extract_vendor_fields_from_region_text(region_text: str):
#     lines = [normalize_spaces(x) for x in (region_text or "").splitlines()]
#     lines = [x for x in lines if x]

#     emails = value_after_label(lines, LABEL_EMAILS)
#     phones = value_after_label(lines, LABEL_PHONES)
#     cap = value_after_label(lines, LABEL_CAP)
#     inst = value_after_label(lines, LABEL_INST)

#     return {
#         "emails": emails,
#         "contact_numbers": phones,
#         "total_installed_capacity_kwp": pick_number(cap),
#         "no_of_installations": pick_number(inst),
#     }


# def extract_all_vendors(page):
#     headers = vendor_header_actions(page)
#     n = headers.count()
#     if n == 0:
#         raise RuntimeError("No vendor header_action elements found. (Accordion selector mismatch)")

#     print(f"[INFO] vendor header_action found = {n}")

#     written = 0
#     seen_header_ids = set()

#     for i in range(n):
#         header = headers.nth(i)

#         # header_action id is the stable key
#         hid = ""
#         try:
#             hid = header.get_attribute("id") or ""
#         except Exception:
#             hid = ""

#         if not hid:
#             # If no id, skip (rare)
#             continue

#         if hid in seen_header_ids:
#             continue
#         seen_header_ids.add(hid)

#         # Expand
#         ensure_expanded_by_aria(page, header)

#         # Find matching content region and wait until it's shown/has text
#         region = content_region_for_header(page, hid)

#         # Wait content to become available / not hidden
#         try:
#             region.wait_for(state="attached", timeout=15_000)
#         except Exception:
#             pass

#         # Sometimes aria-hidden flips on region itself
#         # We'll wait for it to contain EMAIL / CONTACT etc.
#         try:
#             region.locator("text=EMAIL").first.wait_for(timeout=10_000)
#         except Exception:
#             page.wait_for_timeout(400)

#         text = ""
#         try:
#             text = region.inner_text()
#         except Exception:
#             text = ""

#         fields = extract_vendor_fields_from_region_text(text)

#         row = {
#             "state": STATE_NAME,
#             "district": DISTRICT_NAME,
#             "emails": fields["emails"],
#             "contact_numbers": fields["contact_numbers"],
#             "total_installed_capacity_kwp": fields["total_installed_capacity_kwp"],
#             "no_of_installations": fields["no_of_installations"],
#         }
#         append_rows_csv(OUT_CSV, [row])
#         written += 1

#         if written % 20 == 0:
#             print(f"  [PROGRESS] written={written}/{n}")

#         page.wait_for_timeout(120)

#     print(f"[DONE] wrote rows={written} -> {OUT_CSV}")


# # -------------------------
# # Main
# # -------------------------
# def main():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
#         context = browser.new_context(
#             viewport={"width": 1440, "height": 820},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             wait_spa_ready(page)

#             # Ensure filter UI exists
#             try:
#                 page.get_by_text("Filters", exact=False).first.wait_for(timeout=12_000)
#             except PWTimeoutError:
#                 print("[WARN] Filters not visible -> hard refresh")
#                 if not hard_refresh(page, URL, tries=2):
#                     raise RuntimeError("Page not loading after hard refresh.")
#                 wait_spa_ready(page)

#             # Select State + District (dropdown-empty-safe)
#             open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
#             open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)

#             # Apply
#             click_apply(page)
#             page.wait_for_timeout(1800)

#             # Wait for at least one vendor header action
#             try:
#                 vendor_header_actions(page).first.wait_for(timeout=15_000)
#             except Exception:
#                 print("[WARN] No vendors after Apply -> hard refresh + re-apply once")
#                 if not hard_refresh(page, URL, tries=2):
#                     raise RuntimeError("Hard refresh failed after empty results.")
#                 wait_spa_ready(page)

#                 open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
#                 open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)
#                 click_apply(page)
#                 page.wait_for_timeout(1800)

#             # Load all vendors (click load more until end)
#             load_all_vendors(page)

#             # Extract
#             extract_all_vendors(page)

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="pmsuryaghar_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main()


# -----------------------------------new updated code starts here--------------------------------------------------------------------------------------------------------

# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import csv
# import time
# import re
# import os
# import hashlib
# from pathlib import Path

# URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

# STATE_NAME = "GUJARAT"
# DISTRICT_NAME = "Ahmedabad"
# OUT_CSV = "pmsuryaghar_guj_ahd_all.csv"
# SEEN_FILE = OUT_CSV + ".seen"

# # VIEW
# HEADLESS = False
# SLOW_MO_MS = 60
# WAIT_MS = 60_000

# # Dropdown empty -> refresh retry
# OPTIONS_WAIT_MS = 20_000
# MAX_REFRESH_RETRIES = 6

# # Load more
# LOAD_MORE_MAX_CLICKS = 600
# LOAD_MORE_STUCK_LIMIT = 6
# LOAD_MORE_POST_CLICK_WAIT_MS = 25_000

# # Extraction
# EXTRACT_WAIT_PER_VENDOR_MS = 12_000
# SCROLL_PAUSE_MS = 120

# # If list is virtualized, do a few passes
# RECHECK_NEW_HEADERS_PASSES = 4

# CSV_HEADER = [
#     "state",
#     "district",
#     "emails",
#     "contact_numbers",
#     "total_installed_capacity_kwp",
#     "no_of_installations",
# ]

# # ✅ YOUR CLASS (brittle, but we try it first)
# # This matches: "p-element ng-tns-c3596192458-15 ng-star-inserted" (as substring)
# PREFERRED_CLASS_SUBSTR = "ng-tns-c3596192458-"
# PREFERRED_NODE_SELECTOR = (
#     f"[class*='p-element'][class*='ng-star-inserted'][class*='{PREFERRED_CLASS_SUBSTR}']"
# )
# # Fallback if that id changes
# FALLBACK_NODE_SELECTOR = "[class*='p-element'][class*='ng-star-inserted'][class*='ng-tns-c']"


# # -------------------------
# # Disk-safe CSV helpers
# # -------------------------
# def _fsync_file(f):
#     f.flush()
#     os.fsync(f.fileno())


# def ensure_csv_header(path: str):
#     p = Path(path)
#     if p.exists() and p.stat().st_size > 0:
#         return
#     with open(p, "w", newline="", encoding="utf-8-sig") as f:
#         w = csv.writer(f)
#         w.writerow(CSV_HEADER)
#         _fsync_file(f)


# def append_row_realtime(path: str, row: dict):
#     ensure_csv_header(path)
#     with open(path, "a", newline="", encoding="utf-8-sig") as f:
#         w = csv.DictWriter(f, fieldnames=CSV_HEADER)
#         w.writerow({k: row.get(k, "") for k in CSV_HEADER})
#         _fsync_file(f)


# def load_seen() -> set:
#     p = Path(SEEN_FILE)
#     if not p.exists() or p.stat().st_size == 0:
#         return set()
#     out = set()
#     for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
#         s = line.strip()
#         if s:
#             out.add(s)
#     return out


# def append_seen_realtime(keys):
#     if not keys:
#         return
#     with open(SEEN_FILE, "a", encoding="utf-8") as f:
#         for k in keys:
#             f.write(k + "\n")
#         _fsync_file(f)


# # -------------------------
# # Debug
# # -------------------------
# def dump_debug(page, prefix="debug"):
#     ts = int(time.time())
#     out_dir = Path("pw_debug")
#     out_dir.mkdir(exist_ok=True)
#     shot = out_dir / f"{prefix}_{ts}.png"
#     html = out_dir / f"{prefix}_{ts}.html"
#     try:
#         page.screenshot(path=str(shot), full_page=True)
#     except Exception:
#         pass
#     try:
#         html.write_text(page.content(), encoding="utf-8")
#     except Exception:
#         pass
#     print(f"[DEBUG] Saved: {shot} and {html}")


# # -------------------------
# # SPA settle / refresh
# # -------------------------
# def wait_spa_ready(page):
#     try:
#         page.wait_for_load_state("domcontentloaded", timeout=WAIT_MS)
#     except Exception:
#         pass
#     try:
#         page.wait_for_load_state("networkidle", timeout=25_000)
#     except Exception:
#         pass
#     page.wait_for_timeout(900)


# def wait_for_settled(page, timeout_ms=25_000):
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     stable = 0
#     while time.time() < deadline:
#         try:
#             stats = page.evaluate(
#                 """
#                 () => {
#                   const headers = document.querySelectorAll("[id$='_header_action']").length;
#                   const tlen = (document.body && document.body.innerText) ? document.body.innerText.length : 0;
#                   return {headers, tlen};
#                 }
#                 """
#             )
#         except Exception:
#             stats = None

#         if stats == last and stats is not None:
#             stable += 1
#             if stable >= 3:
#                 return
#         else:
#             stable = 0
#             last = stats

#         page.wait_for_timeout(250)


# def hard_refresh(page, url: str, tries: int = 2) -> bool:
#     for _ in range(tries):
#         try:
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1200)
#             return True
#         except Exception:
#             pass

#         try:
#             bust = int(time.time() * 1000)
#             page.goto(f"{url}?cb={bust}", wait_until="domcontentloaded")
#             page.wait_for_timeout(1400)
#             return True
#         except Exception:
#             pass

#         try:
#             page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
#             page.evaluate(
#                 """
#                 async () => {
#                   if (navigator.serviceWorker) {
#                     const regs = await navigator.serviceWorker.getRegistrations();
#                     for (const r of regs) await r.unregister();
#                   }
#                 }
#                 """
#             )
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)
#             return True
#         except Exception:
#             pass

#     return False


# # -------------------------
# # Dropdown handling
# # -------------------------
# OPTION_CONTAINER_SELECTORS = [
#     "ng-dropdown-panel .ng-option",
#     ".ng-dropdown-panel .ng-option",
#     "ng-dropdown-panel [role='option']",
#     ".ng-dropdown-panel [role='option']",
#     ".cdk-overlay-container [role='option']",
#     ".cdk-overlay-container .ng-option",
#     "[role='listbox'] [role='option']",
# ]

# SEARCH_INPUT_SELECTORS = [
#     "ng-dropdown-panel input[type='text']",
#     ".ng-dropdown-panel input[type='text']",
#     ".cdk-overlay-container input[type='text']",
#     "input[placeholder*='Search' i]",
#     "input[type='search']",
# ]


# def close_dropdown(page):
#     try:
#         page.keyboard.press("Escape")
#     except Exception:
#         pass
#     page.wait_for_timeout(250)


# def click_placeholder_dropdown(page, placeholder_text: str):
#     loc = page.get_by_text(placeholder_text, exact=False).first
#     loc.wait_for(state="visible", timeout=WAIT_MS)
#     loc.click(force=True)


# def _any_options_count(page) -> int:
#     total = 0
#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             total += page.locator(sel).count()
#         except Exception:
#             pass
#     return total


# def wait_for_any_options(page, timeout_ms: int) -> bool:
#     deadline = time.time() + timeout_ms / 1000
#     while time.time() < deadline:
#         if _any_options_count(page) > 0:
#             return True
#         page.wait_for_timeout(250)
#     return False


# def _type_in_search_if_present(page, text: str):
#     for sel in SEARCH_INPUT_SELECTORS:
#         inp = page.locator(sel).first
#         try:
#             if inp.count() > 0 and inp.is_visible():
#                 inp.click()
#                 inp.fill("")
#                 inp.type(text, delay=35)
#                 page.wait_for_timeout(300)
#                 return
#         except Exception:
#             continue


# def click_option_case_insensitive(page, option_text: str) -> bool:
#     wanted = option_text.strip().lower()

#     try:
#         opts = page.get_by_role("option").all()
#         for opt in opts:
#             try:
#                 t = (opt.inner_text() or "").strip()
#                 if t.lower() == wanted and opt.is_visible():
#                     opt.click(force=True)
#                     return True
#             except Exception:
#                 continue
#     except Exception:
#         pass

#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             items = page.locator(sel)
#             n = items.count()
#             for i in range(n):
#                 it = items.nth(i)
#                 t = (it.inner_text() or "").strip()
#                 if t.lower() == wanted:
#                     it.scroll_into_view_if_needed()
#                     it.wait_for(state="visible", timeout=5000)
#                     it.click(force=True)
#                     return True
#         except Exception:
#             continue

#     return False


# def open_dropdown_and_select_with_refresh(page, placeholder: str, value_text: str):
#     for attempt in range(1, MAX_REFRESH_RETRIES + 1):
#         click_placeholder_dropdown(page, placeholder)

#         ok = wait_for_any_options(page, OPTIONS_WAIT_MS)
#         if not ok:
#             _type_in_search_if_present(page, value_text)
#             ok = wait_for_any_options(page, 7000)

#         if ok and click_option_case_insensitive(page, value_text):
#             page.wait_for_timeout(500)
#             return

#         close_dropdown(page)
#         print(f"[WARN] '{placeholder}' empty / '{value_text}' not found. Refresh retry {attempt}/{MAX_REFRESH_RETRIES}")
#         if not hard_refresh(page, URL, tries=2):
#             raise RuntimeError("Hard refresh failed while recovering dropdown empty state.")
#         wait_spa_ready(page)

#     raise RuntimeError(f"Could not select '{value_text}' from '{placeholder}' after refresh retries.")


# def click_apply(page):
#     btn = page.get_by_role("button", name="Apply").first
#     if btn.count() == 0:
#         btn = page.locator("button:has-text('Apply')").first
#     btn.wait_for(state="visible", timeout=WAIT_MS)
#     btn.click(force=True)


# # -------------------------
# # Vendor list helpers
# # -------------------------
# HEADER_ACTION_SEL = "[id$='_header_action']"
# HEADER_FILTER_RE = re.compile(r"NO\.\s*OF\s*INSTALLATIONS", re.I)


# def count_vendor_headers(page) -> int:
#     return page.locator(HEADER_ACTION_SEL).filter(has_text=HEADER_FILTER_RE).count()


# def find_load_more_button(page):
#     return page.locator("button").filter(has_text=re.compile(r"load\s*more", re.I)).first


# def scroll_to_bottom_everywhere(page):
#     page.evaluate(
#         """
#         () => {
#           window.scrollTo(0, document.body.scrollHeight);
#           const all = Array.from(document.querySelectorAll("*"));
#           const scrollables = all
#             .map(el => {
#               const st = window.getComputedStyle(el);
#               const oy = st.overflowY;
#               const can = (oy === 'auto' || oy === 'scroll') && (el.scrollHeight > el.clientHeight + 50);
#               return can ? el : null;
#             })
#             .filter(Boolean);

#           scrollables.sort((a,b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
#           for (const el of scrollables.slice(0, 6)) el.scrollTop = el.scrollHeight;
#         }
#         """
#     )


# def click_load_more(page) -> bool:
#     btn = find_load_more_button(page)
#     try:
#         if btn.count() == 0:
#             return False
#     except Exception:
#         return False

#     scroll_to_bottom_everywhere(page)
#     page.wait_for_timeout(400)

#     try:
#         btn.scroll_into_view_if_needed()
#     except Exception:
#         pass

#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass

#     try:
#         btn.click(force=True, timeout=5000)
#         return True
#     except Exception:
#         pass

#     try:
#         btn.evaluate("el => { el.scrollIntoView({block:'center'}); el.click(); }")
#         return True
#     except Exception:
#         return False


# def load_all_vendors(page):
#     prev = count_vendor_headers(page)
#     stuck = 0
#     print(f"[INFO] initial vendor headers in DOM = {prev}")

#     for i in range(LOAD_MORE_MAX_CLICKS):
#         btn = find_load_more_button(page)
#         try:
#             if btn.count() == 0 or not btn.is_visible():
#                 print("[INFO] Load More not visible -> done loading")
#                 break
#         except Exception:
#             print("[INFO] Load More not accessible -> done loading")
#             break

#         clicked = click_load_more(page)
#         if not clicked:
#             print("[INFO] Load More not clickable/disabled -> done loading")
#             break

#         wait_for_settled(page, timeout_ms=LOAD_MORE_POST_CLICK_WAIT_MS)

#         cur = count_vendor_headers(page)
#         if cur > prev:
#             print(f"[LOAD MORE] click={i+1} headers {prev} -> {cur}")
#             prev = cur
#             stuck = 0
#         else:
#             stuck += 1
#             print(f"[WARN] Load More clicked but header count not increased (stuck={stuck}/{LOAD_MORE_STUCK_LIMIT})")
#             if stuck >= LOAD_MORE_STUCK_LIMIT:
#                 print("[INFO] stopping load-more due to repeated no-growth (will extract anyway)")
#                 break

#     print(f"[INFO] headers after load more = {count_vendor_headers(page)}")


# # -------------------------
# # Extraction (TRY YOUR CLASS FIRST)
# # -------------------------
# ALL_LABELS = {
#     "EMAIL(S)", "EMAILS", "EMAIL",
#     "CONTACT NUMBER(S)", "CONTACT NUMBERS", "CONTACT NUMBER",
#     "TOTAL INSTALLED CAPACITY (KWP)", "TOTAL INSTALLED CAPACITY (KWP) ", "TOTAL INSTALLED CAPACITY (KWP)",
#     "TOTAL INSTALLED CAPACITY (KWP)", "TOTAL INSTALLED CAPACITY (kWp)", "TOTAL INSTALLED CAPACITY",
#     "NO. OF INSTALLATIONS", "NO OF INSTALLATIONS", "NO. OF INSTALLATION"
# }


# def is_labelish(v: str) -> bool:
#     if not v:
#         return True
#     up = v.strip().upper()
#     return up in ALL_LABELS


# def normalize_phone(s: str) -> str:
#     if not s:
#         return ""
#     m = re.findall(r"\d+", s)
#     return "".join(m) if m else s.strip()


# def pick_first_number(s: str) -> str:
#     if not s:
#         return ""
#     m = re.search(r"(\d[\d,]*)", s)
#     return m.group(1).replace(",", "") if m else s.strip()


# def vendor_items_snapshot(page):
#     return page.evaluate(
#         r"""
#         () => {
#           const re = /NO\.\s*OF\s*INSTALLATIONS/i;
#           const els = Array.from(document.querySelectorAll("[id$='_header_action']"))
#             .filter(el => re.test((el.textContent||"")));
#           return els.map(el => ({id: el.id, text: (el.textContent||"").trim()}));
#         }
#         """
#     )


# def expand_header_by_id(page, header_id: str):
#     return page.evaluate(
#         """
#         (hid) => {
#           const el = document.getElementById(hid);
#           if (!el) return false;
#           const aria = (el.getAttribute('aria-expanded') || '').toLowerCase();
#           el.scrollIntoView({block:'center', inline:'nearest'});
#           if (aria !== 'true') el.click();
#           return true;
#         }
#         """,
#         header_id,
#     )


# def extract_fields_from_header_region(page, header_id: str):
#     """
#     1) Find the region: div[role=region][aria-labelledby=header_id]
#     2) Prefer extracting text INSIDE your class:
#          PREFERRED_NODE_SELECTOR
#        If not found, fallback to:
#          FALLBACK_NODE_SELECTOR
#        Else fallback to region.innerText.
#     3) Parse label -> value (next non-label line)
#     """
#     return page.evaluate(
#         r"""
#         ({hid, preferredSel, fallbackSel}) => {
#           function clean(s){ return (s||"").replace(/\s+/g," ").trim(); }
#           const region = document.querySelector(`div[role='region'][aria-labelledby='${hid}']`);
#           if (!region) return {ok:false, reason:"no-region"};

#           const ALL_LABELS = new Set([
#             "EMAIL(S)","EMAILS","EMAIL",
#             "CONTACT NUMBER(S)","CONTACT NUMBERS","CONTACT NUMBER",
#             "TOTAL INSTALLED CAPACITY (KWP)","TOTAL INSTALLED CAPACITY (KWP) ","TOTAL INSTALLED CAPACITY (KWP)",
#             "TOTAL INSTALLED CAPACITY (kWp)","TOTAL INSTALLED CAPACITY",
#             "NO. OF INSTALLATIONS","NO OF INSTALLATIONS","NO. OF INSTALLATION"
#           ]);

#           const LABELS = {
#             emails: new Set(["EMAIL(S)","EMAILS","EMAIL"]),
#             phones: new Set(["CONTACT NUMBER(S)","CONTACT NUMBERS","CONTACT NUMBER"]),
#             cap: new Set(["TOTAL INSTALLED CAPACITY (KWP)","TOTAL INSTALLED CAPACITY (kWp)","TOTAL INSTALLED CAPACITY"]),
#             inst: new Set(["NO. OF INSTALLATIONS","NO OF INSTALLATIONS","NO. OF INSTALLATION"])
#           };

#           function textFromPreferredArea() {
#             const preferredNodes = Array.from(region.querySelectorAll(preferredSel));
#             if (preferredNodes.length) {
#               return preferredNodes.map(n => clean(n.innerText || n.textContent)).filter(Boolean).join("\n");
#             }
#             const fallbackNodes = Array.from(region.querySelectorAll(fallbackSel));
#             if (fallbackNodes.length) {
#               return fallbackNodes.map(n => clean(n.innerText || n.textContent)).filter(Boolean).join("\n");
#             }
#             return clean(region.innerText || region.textContent || "");
#           }

#           function splitLines(txt){
#             return (txt||"").split("\n").map(x => clean(x)).filter(Boolean);
#           }

#           function firstValueAfterLabel(lines, labelSet){
#             for (let i=0;i<lines.length;i++){
#               const L = lines[i].toUpperCase();
#               if (!labelSet.has(L)) continue;

#               // look ahead for first non-label value
#               for (let j=i+1;j<Math.min(lines.length, i+8);j++){
#                 const v = lines[j];
#                 if (!v) continue;
#                 const Vu = v.toUpperCase();
#                 if (ALL_LABELS.has(Vu)) break;  // next label reached
#                 return v;
#               }
#             }
#             return "";
#           }

#           const txt = textFromPreferredArea();
#           const lines = splitLines(txt);

#           // if your area gives only "EMAIL(S) CONTACT NUMBER(S)" on same line,
#           // split by known labels (soft fix)
#           const expandedLines = [];
#           for (const line of lines){
#             const up = line.toUpperCase();
#             // if a line contains multiple labels, break it into parts
#             if (up.includes("EMAIL(S)") && up.includes("CONTACT NUMBER(S)")) {
#               expandedLines.push("EMAIL(S)");
#               expandedLines.push("CONTACT NUMBER(S)");
#               continue;
#             }
#             expandedLines.push(line);
#           }

#           const emails = firstValueAfterLabel(expandedLines, LABELS.emails);
#           const phones = firstValueAfterLabel(expandedLines, LABELS.phones);
#           const cap = firstValueAfterLabel(expandedLines, LABELS.cap);
#           const inst = firstValueAfterLabel(expandedLines, LABELS.inst);

#           return {
#             ok:true,
#             emails,
#             phones,
#             cap,
#             inst,
#             usedPreferred: region.querySelectorAll(preferredSel).length,
#             usedFallback: region.querySelectorAll(fallbackSel).length,
#             textLen: txt.length
#           };
#         }
#         """,
#         {"hid": header_id, "preferredSel": PREFERRED_NODE_SELECTOR, "fallbackSel": FALLBACK_NODE_SELECTOR},
#     )


# def wait_until_vendor_values(page, header_id: str, header_text: str, timeout_ms: int):
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     while time.time() < deadline:
#         out = extract_fields_from_header_region(page, header_id)
#         last = out

#         if out.get("ok"):
#             emails = (out.get("emails") or "").strip()
#             phones = (out.get("phones") or "").strip()
#             cap = (out.get("cap") or "").strip()
#             inst = (out.get("inst") or "").strip()

#             if not inst:
#                 m = re.search(r"(\d[\d,]*)\s*$", header_text or "")
#                 if m:
#                     inst = m.group(1).replace(",", "")
#                     out["inst"] = inst

#             # accept if we got any real value
#             if (emails and not is_labelish(emails)) or (phones and not is_labelish(phones)) or cap or inst:
#                 return out

#         page.wait_for_timeout(250)

#     return last or {"ok": False, "reason": "timeout"}


# def make_seen_key(header_text: str, emails: str, phones: str, cap: str, inst: str) -> str:
#     base = (header_text or "").strip().lower()
#     ph = (phones or "").strip().lower()
#     em = (emails or "").strip().lower()
#     basis = base
#     if ph:
#         basis += "||" + ph
#     elif em:
#         basis += "||" + em
#     basis += f"||{cap or ''}||{inst or ''}"
#     return hashlib.blake2b(basis.encode("utf-8"), digest_size=16).hexdigest()


# def extract_all_vendors_after_loading(page):
#     ensure_csv_header(OUT_CSV)
#     seen = load_seen()
#     processed_ids = set()

#     page.evaluate("window.scrollTo(0,0)")
#     page.wait_for_timeout(600)

#     total_saved = 0

#     for pass_no in range(RECHECK_NEW_HEADERS_PASSES):
#         snap = vendor_items_snapshot(page)
#         if not snap:
#             raise RuntimeError("No vendor header_action found for extraction.")

#         print(f"[INFO] extraction pass={pass_no+1} headers_in_dom={len(snap)} saved={total_saved}")

#         for item in snap:
#             hid = item.get("id", "")
#             htxt = item.get("text", "") or ""
#             if not hid or hid in processed_ids:
#                 continue
#             processed_ids.add(hid)

#             expand_header_by_id(page, hid)
#             page.wait_for_timeout(120)

#             data = wait_until_vendor_values(page, hid, htxt, timeout_ms=EXTRACT_WAIT_PER_VENDOR_MS)

#             emails = (data.get("emails") or "").strip()
#             phones = (data.get("phones") or "").strip()
#             cap = pick_first_number((data.get("cap") or "").strip())
#             inst = pick_first_number((data.get("inst") or "").strip())

#             phones = normalize_phone(phones)

#             # prevent labels from being saved as values
#             if is_labelish(emails):
#                 emails = ""
#             if is_labelish(phones):
#                 phones = ""

#             if not (emails or phones or cap or inst):
#                 continue

#             key = make_seen_key(htxt, emails, phones, cap, inst)
#             if key in seen:
#                 continue

#             append_row_realtime(
#                 OUT_CSV,
#                 {
#                     "state": STATE_NAME,
#                     "district": DISTRICT_NAME,
#                     "emails": emails,
#                     "contact_numbers": phones,
#                     "total_installed_capacity_kwp": cap,
#                     "no_of_installations": inst,
#                 },
#             )
#             append_seen_realtime([key])
#             seen.add(key)
#             total_saved += 1

#             if total_saved % 25 == 0:
#                 print(f"  [PROGRESS] saved={total_saved}")

#             page.wait_for_timeout(SCROLL_PAUSE_MS)

#         # scroll to force DOM to render more (if virtualized)
#         page.evaluate("window.scrollBy(0, 3500)")
#         page.wait_for_timeout(800)
#         wait_for_settled(page, timeout_ms=12_000)

#     print(f"[DONE] total_saved={total_saved} -> {OUT_CSV}")


# # -------------------------
# # Main
# # -------------------------
# def main():
#     ensure_csv_header(OUT_CSV)

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
#         context = browser.new_context(
#             viewport={"width": 1440, "height": 820},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             wait_spa_ready(page)

#             # Ensure Filters exists
#             try:
#                 page.get_by_text("Filters", exact=False).first.wait_for(timeout=15_000)
#             except PWTimeoutError:
#                 print("[WARN] Filters not visible -> hard refresh")
#                 if not hard_refresh(page, URL, tries=2):
#                     raise RuntimeError("Page not loading after hard refresh.")
#                 wait_spa_ready(page)

#             open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
#             open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)

#             click_apply(page)
#             wait_for_settled(page, timeout_ms=25_000)

#             # Ensure vendor list exists
#             try:
#                 page.locator(HEADER_ACTION_SEL).filter(has_text=HEADER_FILTER_RE).first.wait_for(timeout=25_000)
#             except Exception:
#                 print("[WARN] Vendor list not visible after Apply -> refresh + re-apply once")
#                 if not hard_refresh(page, URL, tries=2):
#                     raise RuntimeError("Hard refresh failed after empty results.")
#                 wait_spa_ready(page)
#                 open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
#                 open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)
#                 click_apply(page)
#                 wait_for_settled(page, timeout_ms=25_000)

#             # 1) Load all pages first
#             load_all_vendors(page)

#             # 2) Scroll to top then extract using your class first
#             extract_all_vendors_after_loading(page)

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="pmsuryaghar_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main()

# ------------------------------------------------new code----------------------------------------------------------------------------------------------------------------


# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import csv
# import time
# import re
# import os
# import hashlib
# from pathlib import Path

# URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

# STATE_NAME = "GUJARAT"
# DISTRICT_NAME = "Arvalli"
# OUT_CSV = "pmsuryaghar_guj_ahd_all.csv"
# SEEN_FILE = OUT_CSV + ".seen"

# # VIEW
# HEADLESS = False
# SLOW_MO_MS = 60
# WAIT_MS = 60_000

# # Dropdown empty -> refresh retry
# OPTIONS_WAIT_MS = 20_000
# MAX_REFRESH_RETRIES = 6

# # Load more
# LOAD_MORE_MAX_CLICKS = 600
# LOAD_MORE_STUCK_LIMIT = 6
# LOAD_MORE_POST_CLICK_WAIT_MS = 25_000

# # Extraction
# EXTRACT_WAIT_PER_VENDOR_MS = 12_000
# SCROLL_PAUSE_MS = 120

# # If list is virtualized, do a few passes
# RECHECK_NEW_HEADERS_PASSES = 4

# CSV_HEADER = [
#     "state",
#     "district",
#     "emails",
#     "contact_numbers",
#     "total_installed_capacity_kwp",
#     "no_of_installations",
# ]

# # -------------------------
# # Disk-safe CSV helpers
# # -------------------------
# def _fsync_file(f):
#     f.flush()
#     os.fsync(f.fileno())


# def ensure_csv_header(path: str):
#     p = Path(path)
#     if p.exists() and p.stat().st_size > 0:
#         return
#     with open(p, "w", newline="", encoding="utf-8-sig") as f:
#         w = csv.writer(f)
#         w.writerow(CSV_HEADER)
#         _fsync_file(f)


# def append_row_realtime(path: str, row: dict):
#     ensure_csv_header(path)
#     with open(path, "a", newline="", encoding="utf-8-sig") as f:
#         w = csv.DictWriter(f, fieldnames=CSV_HEADER)
#         w.writerow({k: row.get(k, "") for k in CSV_HEADER})
#         _fsync_file(f)


# def load_seen() -> set:
#     p = Path(SEEN_FILE)
#     if not p.exists() or p.stat().st_size == 0:
#         return set()
#     out = set()
#     for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
#         s = line.strip()
#         if s:
#             out.add(s)
#     return out


# def append_seen_realtime(keys):
#     if not keys:
#         return
#     with open(SEEN_FILE, "a", encoding="utf-8") as f:
#         for k in keys:
#             f.write(k + "\n")
#         _fsync_file(f)


# # -------------------------
# # Debug
# # -------------------------
# def dump_debug(page, prefix="debug"):
#     ts = int(time.time())
#     out_dir = Path("pw_debug")
#     out_dir.mkdir(exist_ok=True)
#     shot = out_dir / f"{prefix}_{ts}.png"
#     html = out_dir / f"{prefix}_{ts}.html"
#     try:
#         page.screenshot(path=str(shot), full_page=True)
#     except Exception:
#         pass
#     try:
#         html.write_text(page.content(), encoding="utf-8")
#     except Exception:
#         pass
#     print(f"[DEBUG] Saved: {shot} and {html}")


# # -------------------------
# # SPA settle / refresh
# # -------------------------
# def wait_spa_ready(page):
#     try:
#         page.wait_for_load_state("domcontentloaded", timeout=WAIT_MS)
#     except Exception:
#         pass
#     try:
#         page.wait_for_load_state("networkidle", timeout=25_000)
#     except Exception:
#         pass
#     page.wait_for_timeout(900)


# def wait_for_settled(page, timeout_ms=25_000):
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     stable = 0
#     while time.time() < deadline:
#         try:
#             stats = page.evaluate(
#                 """
#                 () => {
#                   const headers = document.querySelectorAll("[id$='_header_action'][aria-controls]").length;
#                   const tlen = (document.body && document.body.innerText) ? document.body.innerText.length : 0;
#                   return {headers, tlen};
#                 }
#                 """
#             )
#         except Exception:
#             stats = None

#         if stats == last and stats is not None:
#             stable += 1
#             if stable >= 3:
#                 return
#         else:
#             stable = 0
#             last = stats

#         page.wait_for_timeout(250)


# def hard_refresh(page, url: str, tries: int = 2) -> bool:
#     for _ in range(tries):
#         try:
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1200)
#             return True
#         except Exception:
#             pass

#         try:
#             bust = int(time.time() * 1000)
#             page.goto(f"{url}?cb={bust}", wait_until="domcontentloaded")
#             page.wait_for_timeout(1400)
#             return True
#         except Exception:
#             pass

#         try:
#             page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
#             page.evaluate(
#                 """
#                 async () => {
#                   if (navigator.serviceWorker) {
#                     const regs = await navigator.serviceWorker.getRegistrations();
#                     for (const r of regs) await r.unregister();
#                   }
#                 }
#                 """
#             )
#             page.reload(wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)
#             return True
#         except Exception:
#             pass

#     return False


# # -------------------------
# # Dropdown handling
# # -------------------------
# OPTION_CONTAINER_SELECTORS = [
#     "ng-dropdown-panel .ng-option",
#     ".ng-dropdown-panel .ng-option",
#     "ng-dropdown-panel [role='option']",
#     ".ng-dropdown-panel [role='option']",
#     ".cdk-overlay-container [role='option']",
#     ".cdk-overlay-container .ng-option",
#     "[role='listbox'] [role='option']",
# ]

# SEARCH_INPUT_SELECTORS = [
#     "ng-dropdown-panel input[type='text']",
#     ".ng-dropdown-panel input[type='text']",
#     ".cdk-overlay-container input[type='text']",
#     "input[placeholder*='Search' i]",
#     "input[type='search']",
# ]


# def close_dropdown(page):
#     try:
#         page.keyboard.press("Escape")
#     except Exception:
#         pass
#     page.wait_for_timeout(250)


# def click_placeholder_dropdown(page, placeholder_text: str):
#     loc = page.get_by_text(placeholder_text, exact=False).first
#     loc.wait_for(state="visible", timeout=WAIT_MS)
#     loc.click(force=True)


# def _any_options_count(page) -> int:
#     total = 0
#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             total += page.locator(sel).count()
#         except Exception:
#             pass
#     return total


# def wait_for_any_options(page, timeout_ms: int) -> bool:
#     deadline = time.time() + timeout_ms / 1000
#     while time.time() < deadline:
#         if _any_options_count(page) > 0:
#             return True
#         page.wait_for_timeout(250)
#     return False


# def _type_in_search_if_present(page, text: str):
#     for sel in SEARCH_INPUT_SELECTORS:
#         inp = page.locator(sel).first
#         try:
#             if inp.count() > 0 and inp.is_visible():
#                 inp.click()
#                 inp.fill("")
#                 inp.type(text, delay=35)
#                 page.wait_for_timeout(300)
#                 return
#         except Exception:
#             continue


# def click_option_case_insensitive(page, option_text: str) -> bool:
#     wanted = option_text.strip().lower()

#     try:
#         opts = page.get_by_role("option").all()
#         for opt in opts:
#             try:
#                 t = (opt.inner_text() or "").strip()
#                 if t.lower() == wanted and opt.is_visible():
#                     opt.click(force=True)
#                     return True
#             except Exception:
#                 continue
#     except Exception:
#         pass

#     for sel in OPTION_CONTAINER_SELECTORS:
#         try:
#             items = page.locator(sel)
#             n = items.count()
#             for i in range(n):
#                 it = items.nth(i)
#                 t = (it.inner_text() or "").strip()
#                 if t.lower() == wanted:
#                     it.scroll_into_view_if_needed()
#                     it.wait_for(state="visible", timeout=5000)
#                     it.click(force=True)
#                     return True
#         except Exception:
#             continue

#     return False


# def open_dropdown_and_select_with_refresh(page, placeholder: str, value_text: str):
#     for attempt in range(1, MAX_REFRESH_RETRIES + 1):
#         click_placeholder_dropdown(page, placeholder)

#         ok = wait_for_any_options(page, OPTIONS_WAIT_MS)
#         if not ok:
#             _type_in_search_if_present(page, value_text)
#             ok = wait_for_any_options(page, 7000)

#         if ok and click_option_case_insensitive(page, value_text):
#             page.wait_for_timeout(500)
#             return

#         close_dropdown(page)
#         print(f"[WARN] '{placeholder}' empty / '{value_text}' not found. Refresh retry {attempt}/{MAX_REFRESH_RETRIES}")
#         if not hard_refresh(page, URL, tries=2):
#             raise RuntimeError("Hard refresh failed while recovering dropdown empty state.")
#         wait_spa_ready(page)

#     raise RuntimeError(f"Could not select '{value_text}' from '{placeholder}' after refresh retries.")


# def click_apply(page):
#     btn = page.get_by_role("button", name="Apply").first
#     if btn.count() == 0:
#         btn = page.locator("button:has-text('Apply')").first
#     btn.wait_for(state="visible", timeout=WAIT_MS)
#     btn.click(force=True)


# # -------------------------
# # Vendor list helpers
# # -------------------------
# HEADER_ACTION_SEL = "[id$='_header_action'][aria-controls]"


# def count_vendor_headers(page) -> int:
#     return page.locator(HEADER_ACTION_SEL).count()


# def find_load_more_button(page):
#     return page.locator("button").filter(has_text=re.compile(r"load\s*more", re.I)).first


# def scroll_to_bottom_everywhere(page):
#     page.evaluate(
#         """
#         () => {
#           window.scrollTo(0, document.body.scrollHeight);
#           const all = Array.from(document.querySelectorAll("*"));
#           const scrollables = all
#             .map(el => {
#               const st = window.getComputedStyle(el);
#               const oy = st.overflowY;
#               const can = (oy === 'auto' || oy === 'scroll') && (el.scrollHeight > el.clientHeight + 50);
#               return can ? el : null;
#             })
#             .filter(Boolean);

#           scrollables.sort((a,b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
#           for (const el of scrollables.slice(0, 6)) el.scrollTop = el.scrollHeight;
#         }
#         """
#     )


# def click_load_more(page) -> bool:
#     btn = find_load_more_button(page)
#     try:
#         if btn.count() == 0:
#             return False
#     except Exception:
#         return False

#     scroll_to_bottom_everywhere(page)
#     page.wait_for_timeout(400)

#     try:
#         btn.scroll_into_view_if_needed()
#     except Exception:
#         pass

#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass

#     try:
#         btn.click(force=True, timeout=5000)
#         return True
#     except Exception:
#         pass

#     try:
#         btn.evaluate("el => { el.scrollIntoView({block:'center'}); el.click(); }")
#         return True
#     except Exception:
#         return False


# def load_all_vendors(page):
#     prev = count_vendor_headers(page)
#     stuck = 0
#     print(f"[INFO] initial vendor headers in DOM = {prev}")

#     for i in range(LOAD_MORE_MAX_CLICKS):
#         btn = find_load_more_button(page)
#         try:
#             if btn.count() == 0 or not btn.is_visible():
#                 print("[INFO] Load More not visible -> done loading")
#                 break
#         except Exception:
#             print("[INFO] Load More not accessible -> done loading")
#             break

#         clicked = click_load_more(page)
#         if not clicked:
#             print("[INFO] Load More not clickable/disabled -> done loading")
#             break

#         wait_for_settled(page, timeout_ms=LOAD_MORE_POST_CLICK_WAIT_MS)

#         cur = count_vendor_headers(page)
#         if cur > prev:
#             print(f"[LOAD MORE] click={i+1} headers {prev} -> {cur}")
#             prev = cur
#             stuck = 0
#         else:
#             stuck += 1
#             print(f"[WARN] Load More clicked but header count not increased (stuck={stuck}/{LOAD_MORE_STUCK_LIMIT})")
#             if stuck >= LOAD_MORE_STUCK_LIMIT:
#                 print("[INFO] stopping load-more due to repeated no-growth (will extract anyway)")
#                 break

#     print(f"[INFO] headers after load more = {count_vendor_headers(page)}")


# # -------------------------
# # Extraction
# # -------------------------
# def normalize_phone_list(s: str) -> str:
#     """
#     Keep multiple numbers separated by '|', do NOT merge them into one big digit blob.
#     """
#     if not s:
#         return ""
#     nums = re.findall(r"\d{8,}", s)
#     out = []
#     for n in nums:
#         if n not in out:
#             out.append(n)
#     return "|".join(out)


# def pick_first_number(s: str) -> str:
#     if not s:
#         return ""
#     m = re.search(r"(\d[\d,]*)", s)
#     return m.group(1).replace(",", "") if m else s.strip()


# def vendor_items_snapshot(page):
#     """
#     Return all accordion header actions + their aria-controls (content id).
#     """
#     return page.evaluate(
#         r"""
#         () => {
#           const els = Array.from(document.querySelectorAll("[id$='_header_action'][aria-controls]"));
#           return els.map(el => ({
#             id: el.id,
#             controls: el.getAttribute("aria-controls") || "",
#             expanded: (el.getAttribute("aria-expanded") || "").toLowerCase(),
#             text: (el.innerText || el.textContent || "").trim()
#           }));
#         }
#         """
#     )


# def expand_header_by_id(page, header_id: str):
#     return page.evaluate(
#         """
#         (hid) => {
#           const el = document.getElementById(hid);
#           if (!el) return false;
#           const aria = (el.getAttribute('aria-expanded') || '').toLowerCase();
#           el.scrollIntoView({block:'center', inline:'nearest'});
#           if (aria !== 'true') el.click();
#           return true;
#         }
#         """,
#         header_id,
#     )


# def extract_fields_from_vendor(page, header_id: str):
#     """
#     Find content using aria-controls (most reliable),
#     then parse EMAIL(S), CONTACT NUMBER(S), TOTAL INSTALLED CAPACITY (kWp), NO. OF INSTALLATIONS.
#     """
#     return page.evaluate(
#         r"""
#         (hid) => {
#           function cleanLine(s){ return (s||"").replace(/\s+/g," ").trim(); }

#           const header = document.getElementById(hid);
#           if (!header) return {ok:false, reason:"no-header"};

#           const controls = header.getAttribute("aria-controls") || "";
#           let region = null;

#           if (controls) region = document.getElementById(controls);

#           // fallback (just in case)
#           if (!region) region = document.querySelector(`div[role='region'][aria-labelledby='${hid}']`);
#           if (!region) {
#             const base = hid.replace(/_header_action$/, "_header");
#             region = document.querySelector(`div[role='region'][aria-labelledby='${base}']`);
#           }

#           if (!region) return {ok:false, reason:"no-region", controls};

#           let txt = (region.innerText || region.textContent || "")
#             .replace(/\u00a0/g, " ")
#             .replace(/\r/g, "\n");

#           // Canonicalize labels with placeholders first
#           txt = txt.replace(/EMAIL\s*\(S\)/gi, "___EMAILS___");
#           txt = txt.replace(/CONTACT\s*NUMBER\s*\(S\)/gi, "___CONTACT_NUMBERS___");
#           txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY\s*\(\s*kwp\s*\)/gi, "___CAPACITY_KWP___");
#           txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY/gi, "___CAPACITY___");
#           txt = txt.replace(/NO\.\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");
#           txt = txt.replace(/NO\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");

#           // Inject newlines around placeholders to stabilize parsing
#           txt = txt.replace(/___EMAILS___/g, "\nEMAIL(S)\n");
#           txt = txt.replace(/___CONTACT_NUMBERS___/g, "\nCONTACT NUMBER(S)\n");
#           txt = txt.replace(/___CAPACITY_KWP___/g, "\nTOTAL INSTALLED CAPACITY (KWP)\n");
#           txt = txt.replace(/___CAPACITY___/g, "\nTOTAL INSTALLED CAPACITY\n");
#           txt = txt.replace(/___INSTALLATIONS___/g, "\nNO. OF INSTALLATIONS\n");

#           txt = txt.replace(/[ \t]+\n/g, "\n").replace(/\n{2,}/g, "\n").trim();
#           const lines = txt.split("\n").map(cleanLine).filter(Boolean);

#           const ALL_LABELS = new Set([
#             "EMAIL(S)",
#             "CONTACT NUMBER(S)",
#             "TOTAL INSTALLED CAPACITY (KWP)",
#             "TOTAL INSTALLED CAPACITY",
#             "NO. OF INSTALLATIONS"
#           ]);

#           function isLabel(s){ return ALL_LABELS.has((s||"").toUpperCase()); }

#           function valueAfter(label){
#             const want = label.toUpperCase();
#             for (let i=0; i<lines.length; i++){
#               const up = lines[i].toUpperCase();
#               if (up === want){
#                 for (let j=i+1; j<Math.min(lines.length, i+12); j++){
#                   if (isLabel(lines[j])) break;
#                   if (lines[j]) return lines[j];
#                 }
#               }
#               if (up.startsWith(want + " ")){
#                 return lines[i].slice(label.length).trim();
#               }
#             }
#             return "";
#           }

#           let emailsRaw = valueAfter("EMAIL(S)");
#           let phonesRaw = valueAfter("CONTACT NUMBER(S)");
#           let capRaw = valueAfter("TOTAL INSTALLED CAPACITY (KWP)") || valueAfter("TOTAL INSTALLED CAPACITY");
#           let instRaw = valueAfter("NO. OF INSTALLATIONS");

#           // Heuristic fallback if label parsing fails
#           if (!emailsRaw) {
#             const candidates = Array.from(region.querySelectorAll("a, span, div"))
#               .map(el => cleanLine(el.innerText || el.textContent))
#               .filter(Boolean);
#             const em = candidates.find(t => t.includes("@") || /\[\s*at\s*\]/i.test(t));
#             if (em) emailsRaw = em;
#           }

#           if (!phonesRaw) {
#             const candidates = Array.from(region.querySelectorAll("a"))
#               .map(el => cleanLine(el.innerText || el.textContent))
#               .filter(Boolean);
#             const ph = candidates.find(t => /\d{8,}/.test(t));
#             if (ph) phonesRaw = ph;
#           }

#           function deobfuscateEmail(s){
#             let x = (s||"").trim();
#             x = x.replace(/\[\s*at\s*\]/gi, "@").replace(/\(\s*at\s*\)/gi, "@");
#             x = x.replace(/\[\s*dot\s*\]/gi, ".").replace(/\(\s*dot\s*\)/gi, ".");
#             x = x.replace(/\s+/g, "");
#             return x;
#           }

#           function extractPhones(s){
#             const nums = ((s||"").match(/\d{8,}/g) || []).map(x => x.trim());
#             const uniq = [];
#             for (const n of nums) if (!uniq.includes(n)) uniq.push(n);
#             return uniq.join("|");
#           }

#           function firstNumber(s){
#             const m = (s||"").match(/(\d[\d,]*)/);
#             return m ? m[1].replace(/,/g, "") : "";
#           }

#           const emails = emailsRaw ? deobfuscateEmail(emailsRaw) : "";
#           const phones = phonesRaw ? extractPhones(phonesRaw) : "";
#           const cap = capRaw ? firstNumber(capRaw) : "";
#           const inst = instRaw ? firstNumber(instRaw) : "";

#           return { ok:true, emails, phones, cap, inst, controls };
#         }
#         """,
#         header_id,
#     )


# def make_seen_key(header_text: str, emails: str, phones: str, cap: str, inst: str) -> str:
#     base = (header_text or "").strip().lower()
#     ph = (phones or "").strip().lower()
#     em = (emails or "").strip().lower()
#     basis = base
#     if ph:
#         basis += "||" + ph
#     elif em:
#         basis += "||" + em
#     basis += f"||{cap or ''}||{inst or ''}"
#     return hashlib.blake2b(basis.encode("utf-8"), digest_size=16).hexdigest()


# def wait_until_vendor_values(page, header_id: str, header_text: str, timeout_ms: int):
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     while time.time() < deadline:
#         out = extract_fields_from_vendor(page, header_id)
#         last = out

#         if out.get("ok"):
#             emails = (out.get("emails") or "").strip()
#             phones = (out.get("phones") or "").strip()
#             cap = (out.get("cap") or "").strip()
#             inst = (out.get("inst") or "").strip()

#             # Fallback: installations from header text
#             if not inst:
#                 m = re.search(r"(\d[\d,]*)\s*$", header_text or "")
#                 if m:
#                     inst = m.group(1).replace(",", "")
#                     out["inst"] = inst

#             if emails or phones or cap or inst:
#                 return out

#         page.wait_for_timeout(250)

#     return last or {"ok": False, "reason": "timeout"}


# def extract_all_vendors_after_loading(page):
#     ensure_csv_header(OUT_CSV)
#     seen = load_seen()
#     processed_ids = set()

#     page.evaluate("window.scrollTo(0,0)")
#     page.wait_for_timeout(600)

#     total_saved = 0

#     for pass_no in range(RECHECK_NEW_HEADERS_PASSES):
#         snap = vendor_items_snapshot(page)
#         if not snap:
#             raise RuntimeError("No vendor header_action found for extraction.")

#         print(f"[INFO] extraction pass={pass_no+1} headers_in_dom={len(snap)} saved={total_saved}")

#         for item in snap:
#             hid = item.get("id", "")
#             htxt = item.get("text", "") or ""
#             if not hid or hid in processed_ids:
#                 continue
#             processed_ids.add(hid)

#             expand_header_by_id(page, hid)
#             page.wait_for_timeout(150)

#             data = wait_until_vendor_values(page, hid, htxt, timeout_ms=EXTRACT_WAIT_PER_VENDOR_MS)

#             emails = (data.get("emails") or "").strip()
#             phones = (data.get("phones") or "").strip()
#             cap = pick_first_number((data.get("cap") or "").strip())
#             inst = pick_first_number((data.get("inst") or "").strip())

#             phones = normalize_phone_list(phones)

#             if not (emails or phones or cap or inst):
#                 continue

#             key = make_seen_key(htxt, emails, phones, cap, inst)
#             if key in seen:
#                 continue

#             append_row_realtime(
#                 OUT_CSV,
#                 {
#                     "state": STATE_NAME,
#                     "district": DISTRICT_NAME,
#                     "emails": emails,
#                     "contact_numbers": phones,
#                     "total_installed_capacity_kwp": cap,
#                     "no_of_installations": inst,
#                 },
#             )
#             append_seen_realtime([key])
#             seen.add(key)
#             total_saved += 1

#             if total_saved % 25 == 0:
#                 print(f"  [PROGRESS] saved={total_saved}")

#             page.wait_for_timeout(SCROLL_PAUSE_MS)

#         # scroll to force DOM to render more (if virtualized)
#         page.evaluate("window.scrollBy(0, 3500)")
#         page.wait_for_timeout(800)
#         wait_for_settled(page, timeout_ms=12_000)

#     print(f"[DONE] total_saved={total_saved} -> {OUT_CSV}")


# # -------------------------
# # Main
# # -------------------------
# def main():
#     ensure_csv_header(OUT_CSV)

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
#         context = browser.new_context(
#             viewport={"width": 1440, "height": 820},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             wait_spa_ready(page)

#             # Ensure Filters exists
#             try:
#                 page.get_by_text("Filters", exact=False).first.wait_for(timeout=15_000)
#             except PWTimeoutError:
#                 print("[WARN] Filters not visible -> hard refresh")
#                 if not hard_refresh(page, URL, tries=2):
#                     raise RuntimeError("Page not loading after hard refresh.")
#                 wait_spa_ready(page)

#             open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
#             open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)

#             click_apply(page)
#             wait_for_settled(page, timeout_ms=25_000)

#             # Ensure vendor list exists
#             try:
#                 page.locator(HEADER_ACTION_SEL).first.wait_for(timeout=25_000)
#             except Exception:
#                 print("[WARN] Vendor list not visible after Apply -> refresh + re-apply once")
#                 if not hard_refresh(page, URL, tries=2):
#                     raise RuntimeError("Hard refresh failed after empty results.")
#                 wait_spa_ready(page)
#                 open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
#                 open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)
#                 click_apply(page)
#                 wait_for_settled(page, timeout_ms=25_000)

#             # 1) Load all vendors
#             load_all_vendors(page)

#             # 2) Extract details
#             extract_all_vendors_after_loading(page)

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="pmsuryaghar_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main()


# ------------------------------------------------updated new  code----------------------------------------------------------------------------------------------------------------

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import csv
import time
import re
import os
import hashlib
from pathlib import Path

URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

STATE_NAME = "GUJARAT"
DISTRICT_NAME = "Mahisagar"

OUT_CSV =  DISTRICT_NAME +".csv"
SEEN_FILE = OUT_CSV + ".seen"

# VIEW
HEADLESS = False
SLOW_MO_MS = 60
WAIT_MS = 60_000

# Dropdown empty -> refresh retry
OPTIONS_WAIT_MS = 20_000
MAX_REFRESH_RETRIES = 6

# Load more
LOAD_MORE_MAX_CLICKS = 600
LOAD_MORE_STUCK_LIMIT = 6
LOAD_MORE_POST_CLICK_WAIT_MS = 25_000

# Extraction
EXTRACT_WAIT_PER_VENDOR_MS = 12_000
SCROLL_PAUSE_MS = 120

# If list is virtualized, do a few passes
RECHECK_NEW_HEADERS_PASSES = 4

CSV_HEADER = [
    "state",
    "district",
    "company_name",  # ✅ ADDED
    "emails",
    "contact_numbers",
    "total_installed_capacity_kwp",
    "no_of_installations",
]


# -------------------------
# Disk-safe CSV helpers
# -------------------------
def _fsync_file(f):
    f.flush()
    os.fsync(f.fileno())


def ensure_csv_header(path: str):
    """
    Create CSV with header if missing.
    If file exists but header is different, rename old file and create new.
    """
    p = Path(path)
    if p.exists() and p.stat().st_size > 0:
        try:
            first = p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()[0].strip()
            expected = ",".join(CSV_HEADER)
            if first.replace("\ufeff", "") != expected:
                ts = int(time.time())
                backup = p.with_suffix(p.suffix + f".bak_{ts}")
                p.rename(backup)
                print(f"[WARN] Existing CSV header mismatch. Renamed old file to: {backup}")
        except Exception:
            pass

    if p.exists() and p.stat().st_size > 0:
        return

    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEADER)
        _fsync_file(f)


def append_row_realtime(path: str, row: dict):
    ensure_csv_header(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADER)
        w.writerow({k: row.get(k, "") for k in CSV_HEADER})
        _fsync_file(f)


def load_seen() -> set:
    p = Path(SEEN_FILE)
    if not p.exists() or p.stat().st_size == 0:
        return set()
    out = set()
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s:
            out.add(s)
    return out


def append_seen_realtime(keys):
    if not keys:
        return
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        for k in keys:
            f.write(k + "\n")
        _fsync_file(f)


# -------------------------
# Debug
# -------------------------
def dump_debug(page, prefix="debug"):
    ts = int(time.time())
    out_dir = Path("pw_debug")
    out_dir.mkdir(exist_ok=True)
    shot = out_dir / f"{prefix}_{ts}.png"
    html = out_dir / f"{prefix}_{ts}.html"
    try:
        page.screenshot(path=str(shot), full_page=True)
    except Exception:
        pass
    try:
        html.write_text(page.content(), encoding="utf-8")
    except Exception:
        pass
    print(f"[DEBUG] Saved: {shot} and {html}")


# -------------------------
# SPA settle / refresh
# -------------------------
def wait_spa_ready(page):
    try:
        page.wait_for_load_state("domcontentloaded", timeout=WAIT_MS)
    except Exception:
        pass
    try:
        page.wait_for_load_state("networkidle", timeout=25_000)
    except Exception:
        pass
    page.wait_for_timeout(900)


def wait_for_settled(page, timeout_ms=25_000):
    deadline = time.time() + timeout_ms / 1000
    last = None
    stable = 0
    while time.time() < deadline:
        try:
            stats = page.evaluate(
                """
                () => {
                  const headers = document.querySelectorAll("[id$='_header_action'][aria-controls]").length;
                  const tlen = (document.body && document.body.innerText) ? document.body.innerText.length : 0;
                  return {headers, tlen};
                }
                """
            )
        except Exception:
            stats = None

        if stats == last and stats is not None:
            stable += 1
            if stable >= 3:
                return
        else:
            stable = 0
            last = stats

        page.wait_for_timeout(250)


def hard_refresh(page, url: str, tries: int = 2) -> bool:
    for _ in range(tries):
        try:
            page.reload(wait_until="domcontentloaded")
            page.wait_for_timeout(1200)
            return True
        except Exception:
            pass

        try:
            bust = int(time.time() * 1000)
            page.goto(f"{url}?cb={bust}", wait_until="domcontentloaded")
            page.wait_for_timeout(1400)
            return True
        except Exception:
            pass

        try:
            page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            page.evaluate(
                """
                async () => {
                  if (navigator.serviceWorker) {
                    const regs = await navigator.serviceWorker.getRegistrations();
                    for (const r of regs) await r.unregister();
                  }
                }
                """
            )
            page.reload(wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            return True
        except Exception:
            pass

    return False


# -------------------------
# Dropdown handling
# -------------------------
OPTION_CONTAINER_SELECTORS = [
    "ng-dropdown-panel .ng-option",
    ".ng-dropdown-panel .ng-option",
    "ng-dropdown-panel [role='option']",
    ".ng-dropdown-panel [role='option']",
    ".cdk-overlay-container [role='option']",
    ".cdk-overlay-container .ng-option",
    "[role='listbox'] [role='option']",
]

SEARCH_INPUT_SELECTORS = [
    "ng-dropdown-panel input[type='text']",
    ".ng-dropdown-panel input[type='text']",
    ".cdk-overlay-container input[type='text']",
    "input[placeholder*='Search' i]",
    "input[type='search']",
]


def close_dropdown(page):
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass
    page.wait_for_timeout(250)


def click_placeholder_dropdown(page, placeholder_text: str):
    loc = page.get_by_text(placeholder_text, exact=False).first
    loc.wait_for(state="visible", timeout=WAIT_MS)
    loc.click(force=True)


def _any_options_count(page) -> int:
    total = 0
    for sel in OPTION_CONTAINER_SELECTORS:
        try:
            total += page.locator(sel).count()
        except Exception:
            pass
    return total


def wait_for_any_options(page, timeout_ms: int) -> bool:
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        if _any_options_count(page) > 0:
            return True
        page.wait_for_timeout(250)
    return False


def _type_in_search_if_present(page, text: str):
    for sel in SEARCH_INPUT_SELECTORS:
        inp = page.locator(sel).first
        try:
            if inp.count() > 0 and inp.is_visible():
                inp.click()
                inp.fill("")
                inp.type(text, delay=35)
                page.wait_for_timeout(300)
                return
        except Exception:
            continue


def click_option_case_insensitive(page, option_text: str) -> bool:
    wanted = option_text.strip().lower()

    try:
        opts = page.get_by_role("option").all()
        for opt in opts:
            try:
                t = (opt.inner_text() or "").strip()
                if t.lower() == wanted and opt.is_visible():
                    opt.click(force=True)
                    return True
            except Exception:
                continue
    except Exception:
        pass

    for sel in OPTION_CONTAINER_SELECTORS:
        try:
            items = page.locator(sel)
            n = items.count()
            for i in range(n):
                it = items.nth(i)
                t = (it.inner_text() or "").strip()
                if t.lower() == wanted:
                    it.scroll_into_view_if_needed()
                    it.wait_for(state="visible", timeout=5000)
                    it.click(force=True)
                    return True
        except Exception:
            continue

    return False


def open_dropdown_and_select_with_refresh(page, placeholder: str, value_text: str):
    for attempt in range(1, MAX_REFRESH_RETRIES + 1):
        click_placeholder_dropdown(page, placeholder)

        ok = wait_for_any_options(page, OPTIONS_WAIT_MS)
        if not ok:
            _type_in_search_if_present(page, value_text)
            ok = wait_for_any_options(page, 7000)

        if ok and click_option_case_insensitive(page, value_text):
            page.wait_for_timeout(500)
            return

        close_dropdown(page)
        print(f"[WARN] '{placeholder}' empty / '{value_text}' not found. Refresh retry {attempt}/{MAX_REFRESH_RETRIES}")
        if not hard_refresh(page, URL, tries=2):
            raise RuntimeError("Hard refresh failed while recovering dropdown empty state.")
        wait_spa_ready(page)

    raise RuntimeError(f"Could not select '{value_text}' from '{placeholder}' after refresh retries.")


def click_apply(page):
    btn = page.get_by_role("button", name="Apply").first
    if btn.count() == 0:
        btn = page.locator("button:has-text('Apply')").first
    btn.wait_for(state="visible", timeout=WAIT_MS)
    btn.click(force=True)


# -------------------------
# Vendor list helpers
# -------------------------
HEADER_ACTION_SEL = "[id$='_header_action'][aria-controls]"


def count_vendor_headers(page) -> int:
    return page.locator(HEADER_ACTION_SEL).count()


def find_load_more_button(page):
    return page.locator("button").filter(has_text=re.compile(r"load\s*more", re.I)).first


def scroll_to_bottom_everywhere(page):
    page.evaluate(
        """
        () => {
          window.scrollTo(0, document.body.scrollHeight);
          const all = Array.from(document.querySelectorAll("*"));
          const scrollables = all
            .map(el => {
              const st = window.getComputedStyle(el);
              const oy = st.overflowY;
              const can = (oy === 'auto' || oy === 'scroll') && (el.scrollHeight > el.clientHeight + 50);
              return can ? el : null;
            })
            .filter(Boolean);

          scrollables.sort((a,b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
          for (const el of scrollables.slice(0, 6)) el.scrollTop = el.scrollHeight;
        }
        """
    )


def click_load_more(page) -> bool:
    btn = find_load_more_button(page)
    try:
        if btn.count() == 0:
            return False
    except Exception:
        return False

    scroll_to_bottom_everywhere(page)
    page.wait_for_timeout(400)

    try:
        btn.scroll_into_view_if_needed()
    except Exception:
        pass

    try:
        if not btn.is_enabled():
            return False
    except Exception:
        pass

    try:
        btn.click(force=True, timeout=5000)
        return True
    except Exception:
        pass

    try:
        btn.evaluate("el => { el.scrollIntoView({block:'center'}); el.click(); }")
        return True
    except Exception:
        return False


def load_all_vendors(page):
    prev = count_vendor_headers(page)
    stuck = 0
    print(f"[INFO] initial vendor headers in DOM = {prev}")

    for i in range(LOAD_MORE_MAX_CLICKS):
        btn = find_load_more_button(page)
        try:
            if btn.count() == 0 or not btn.is_visible():
                print("[INFO] Load More not visible -> done loading")
                break
        except Exception:
            print("[INFO] Load More not accessible -> done loading")
            break

        clicked = click_load_more(page)
        if not clicked:
            print("[INFO] Load More not clickable/disabled -> done loading")
            break

        wait_for_settled(page, timeout_ms=LOAD_MORE_POST_CLICK_WAIT_MS)

        cur = count_vendor_headers(page)
        if cur > prev:
            print(f"[LOAD MORE] click={i+1} headers {prev} -> {cur}")
            prev = cur
            stuck = 0
        else:
            stuck += 1
            print(f"[WARN] Load More clicked but header count not increased (stuck={stuck}/{LOAD_MORE_STUCK_LIMIT})")
            if stuck >= LOAD_MORE_STUCK_LIMIT:
                print("[INFO] stopping load-more due to repeated no-growth (will extract anyway)")
                break

    print(f"[INFO] headers after load more = {count_vendor_headers(page)}")


# -------------------------
# Extraction helpers
# -------------------------
def normalize_phone_list(s: str) -> str:
    """
    Keep multiple numbers separated by '|', do NOT merge them into one big digit blob.
    """
    if not s:
        return ""
    nums = re.findall(r"\d{8,}", s)
    out = []
    for n in nums:
        if n not in out:
            out.append(n)
    return "|".join(out)


def pick_first_number(s: str) -> str:
    if not s:
        return ""
    m = re.search(r"(\d[\d,]*)", s)
    return m.group(1).replace(",", "") if m else s.strip()


def vendor_items_snapshot(page):
    """
    Return all accordion header actions + aria-controls + header text + parsed company name.
    """
    return page.evaluate(
        r"""
        () => {
          function clean(s){ return (s||"").replace(/\s+/g," ").trim(); }
          function isNumericLine(s){ return /^\d[\d,]*$/.test((s||"").trim()); }
          function isLabelLine(s){
            const up = (s||"").toUpperCase();
            return up.startsWith("BRAND NAME")
              || /NO\.?\s*OF\s*INSTALLATIONS/.test(up);
          }

          const els = Array.from(document.querySelectorAll("[id$='_header_action'][aria-controls]"));
          return els.map(el => {
            const text = (el.innerText || el.textContent || "").trim();
            const lines = text.split("\n").map(x => clean(x)).filter(Boolean);

            let company = "";
            for (const ln of lines){
              if (isLabelLine(ln)) continue;
              if (isNumericLine(ln)) continue;
              company = ln;
              break;
            }

            return {
              id: el.id,
              controls: el.getAttribute("aria-controls") || "",
              expanded: (el.getAttribute("aria-expanded") || "").toLowerCase(),
              text,
              company_name: company
            };
          });
        }
        """
    )


def expand_header_by_id(page, header_id: str):
    return page.evaluate(
        """
        (hid) => {
          const el = document.getElementById(hid);
          if (!el) return false;
          const aria = (el.getAttribute('aria-expanded') || '').toLowerCase();
          el.scrollIntoView({block:'center', inline:'nearest'});
          if (aria !== 'true') el.click();
          return true;
        }
        """,
        header_id,
    )


def extract_fields_from_vendor(page, header_id: str):
    """
    Find expanded content using aria-controls (reliable for PrimeNG accordion),
    then parse EMAIL(S), CONTACT NUMBER(S), TOTAL INSTALLED CAPACITY (kWp), NO. OF INSTALLATIONS.
    """
    return page.evaluate(
        r"""
        (hid) => {
          function cleanLine(s){ return (s||"").replace(/\s+/g," ").trim(); }

          const header = document.getElementById(hid);
          if (!header) return {ok:false, reason:"no-header"};

          const controls = header.getAttribute("aria-controls") || "";
          let region = null;

          if (controls) region = document.getElementById(controls);

          // fallback (just in case)
          if (!region) region = document.querySelector(`div[role='region'][aria-labelledby='${hid}']`);
          if (!region) {
            const base = hid.replace(/_header_action$/, "_header");
            region = document.querySelector(`div[role='region'][aria-labelledby='${base}']`);
          }

          if (!region) return {ok:false, reason:"no-region", controls};

          let txt = (region.innerText || region.textContent || "")
            .replace(/\u00a0/g, " ")
            .replace(/\r/g, "\n");

          // Canonicalize labels with placeholders first
          txt = txt.replace(/EMAIL\s*\(S\)/gi, "___EMAILS___");
          txt = txt.replace(/CONTACT\s*NUMBER\s*\(S\)/gi, "___CONTACT_NUMBERS___");
          txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY\s*\(\s*kwp\s*\)/gi, "___CAPACITY_KWP___");
          txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY/gi, "___CAPACITY___");
          txt = txt.replace(/NO\.\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");
          txt = txt.replace(/NO\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");

          // Inject newlines around placeholders to stabilize parsing
          txt = txt.replace(/___EMAILS___/g, "\nEMAIL(S)\n");
          txt = txt.replace(/___CONTACT_NUMBERS___/g, "\nCONTACT NUMBER(S)\n");
          txt = txt.replace(/___CAPACITY_KWP___/g, "\nTOTAL INSTALLED CAPACITY (KWP)\n");
          txt = txt.replace(/___CAPACITY___/g, "\nTOTAL INSTALLED CAPACITY\n");
          txt = txt.replace(/___INSTALLATIONS___/g, "\nNO. OF INSTALLATIONS\n");

          txt = txt.replace(/[ \t]+\n/g, "\n").replace(/\n{2,}/g, "\n").trim();
          const lines = txt.split("\n").map(cleanLine).filter(Boolean);

          const ALL_LABELS = new Set([
            "EMAIL(S)",
            "CONTACT NUMBER(S)",
            "TOTAL INSTALLED CAPACITY (KWP)",
            "TOTAL INSTALLED CAPACITY",
            "NO. OF INSTALLATIONS"
          ]);

          function isLabel(s){ return ALL_LABELS.has((s||"").toUpperCase()); }

          function valueAfter(label){
            const want = label.toUpperCase();
            for (let i=0; i<lines.length; i++){
              const up = lines[i].toUpperCase();
              if (up === want){
                for (let j=i+1; j<Math.min(lines.length, i+12); j++){
                  if (isLabel(lines[j])) break;
                  if (lines[j]) return lines[j];
                }
              }
              if (up.startsWith(want + " ")){
                return lines[i].slice(label.length).trim();
              }
            }
            return "";
          }

          let emailsRaw = valueAfter("EMAIL(S)");
          let phonesRaw = valueAfter("CONTACT NUMBER(S)");
          let capRaw = valueAfter("TOTAL INSTALLED CAPACITY (KWP)") || valueAfter("TOTAL INSTALLED CAPACITY");
          let instRaw = valueAfter("NO. OF INSTALLATIONS");

          // Heuristic fallback if label parsing fails
          if (!emailsRaw) {
            const candidates = Array.from(region.querySelectorAll("a, span, div"))
              .map(el => cleanLine(el.innerText || el.textContent))
              .filter(Boolean);
            const em = candidates.find(t => t.includes("@") || /\[\s*at\s*\]/i.test(t));
            if (em) emailsRaw = em;
          }

          if (!phonesRaw) {
            const candidates = Array.from(region.querySelectorAll("a"))
              .map(el => cleanLine(el.innerText || el.textContent))
              .filter(Boolean);
            const ph = candidates.find(t => /\d{8,}/.test(t));
            if (ph) phonesRaw = ph;
          }

          function deobfuscateEmail(s){
            let x = (s||"").trim();
            x = x.replace(/\[\s*at\s*\]/gi, "@").replace(/\(\s*at\s*\)/gi, "@");
            x = x.replace(/\[\s*dot\s*\]/gi, ".").replace(/\(\s*dot\s*\)/gi, ".");
            x = x.replace(/\s+/g, "");
            return x;
          }

          function extractEmails(s){
            // return any email-like chunks OR deobfuscated string if no obvious emails
            const raw = (s||"").trim();
            const deob = deobfuscateEmail(raw);
            const found = deob.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/ig) || [];
            const uniq = [];
            for (const e of found) if (!uniq.includes(e)) uniq.push(e);
            if (uniq.length) return uniq.join("|");
            return deob || "";
          }

          function extractPhones(s){
            const nums = ((s||"").match(/\d{8,}/g) || []).map(x => x.trim());
            const uniq = [];
            for (const n of nums) if (!uniq.includes(n)) uniq.push(n);
            return uniq.join("|");
          }

          function firstNumber(s){
            const m = (s||"").match(/(\d[\d,]*)/);
            return m ? m[1].replace(/,/g, "") : "";
          }

          const emails = emailsRaw ? extractEmails(emailsRaw) : "";
          const phones = phonesRaw ? extractPhones(phonesRaw) : "";
          const cap = capRaw ? firstNumber(capRaw) : "";
          const inst = instRaw ? firstNumber(instRaw) : "";

          return { ok:true, emails, phones, cap, inst, controls };
        }
        """,
        header_id,
    )


def make_seen_key(company_name: str, emails: str, phones: str, cap: str, inst: str) -> str:
    basis = (company_name or "").strip().lower()
    basis += "||" + (phones or "").strip().lower()
    basis += "||" + (emails or "").strip().lower()
    basis += f"||{cap or ''}||{inst or ''}"
    return hashlib.blake2b(basis.encode("utf-8"), digest_size=16).hexdigest()


def wait_until_vendor_values(page, header_id: str, header_text: str, timeout_ms: int):
    deadline = time.time() + timeout_ms / 1000
    last = None
    while time.time() < deadline:
        out = extract_fields_from_vendor(page, header_id)
        last = out

        if out.get("ok"):
            emails = (out.get("emails") or "").strip()
            phones = (out.get("phones") or "").strip()
            cap = (out.get("cap") or "").strip()
            inst = (out.get("inst") or "").strip()

            # Fallback: installations from header text
            if not inst:
                m = re.search(r"(\d[\d,]*)\s*$", header_text or "")
                if m:
                    inst = m.group(1).replace(",", "")
                    out["inst"] = inst

            if emails or phones or cap or inst:
                return out

        page.wait_for_timeout(250)

    return last or {"ok": False, "reason": "timeout"}


def extract_all_vendors_after_loading(page):
    ensure_csv_header(OUT_CSV)
    seen = load_seen()
    processed_ids = set()

    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(600)

    total_saved = 0

    for pass_no in range(RECHECK_NEW_HEADERS_PASSES):
        snap = vendor_items_snapshot(page)
        if not snap:
            raise RuntimeError("No vendor header_action found for extraction.")

        print(f"[INFO] extraction pass={pass_no+1} headers_in_dom={len(snap)} saved={total_saved}")

        for item in snap:
            hid = item.get("id", "")
            htxt = item.get("text", "") or ""
            company_name = (item.get("company_name") or "").strip()

            if not hid or hid in processed_ids:
                continue
            processed_ids.add(hid)

            expand_header_by_id(page, hid)
            page.wait_for_timeout(150)

            data = wait_until_vendor_values(page, hid, htxt, timeout_ms=EXTRACT_WAIT_PER_VENDOR_MS)

            emails = (data.get("emails") or "").strip()
            phones = (data.get("phones") or "").strip()
            cap = pick_first_number((data.get("cap") or "").strip())
            inst = pick_first_number((data.get("inst") or "").strip())

            phones = normalize_phone_list(phones)

            if not (company_name or emails or phones or cap or inst):
                continue

            key = make_seen_key(company_name, emails, phones, cap, inst)
            if key in seen:
                continue

            append_row_realtime(
                OUT_CSV,
                {
                    "state": STATE_NAME,
                    "district": DISTRICT_NAME,
                    "company_name": company_name,
                    "emails": emails,
                    "contact_numbers": phones,
                    "total_installed_capacity_kwp": cap,
                    "no_of_installations": inst,
                },
            )
            append_seen_realtime([key])
            seen.add(key)
            total_saved += 1

            if total_saved % 25 == 0:
                print(f"  [PROGRESS] saved={total_saved}")

            page.wait_for_timeout(SCROLL_PAUSE_MS)

        # scroll to force DOM to render more (if virtualized)
        page.evaluate("window.scrollBy(0, 3500)")
        page.wait_for_timeout(800)
        wait_for_settled(page, timeout_ms=12_000)

    print(f"[DONE] total_saved={total_saved} -> {OUT_CSV}")


# -------------------------
# Main
# -------------------------
def main():
    ensure_csv_header(OUT_CSV)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
        context = browser.new_context(
            viewport={"width": 1440, "height": 820},
            locale="en-US",
            timezone_id="Asia/Kolkata",
        )
        page = context.new_page()
        page.set_default_timeout(WAIT_MS)

        try:
            page.goto(URL, wait_until="domcontentloaded")
            wait_spa_ready(page)

            # Ensure Filters exists
            try:
                page.get_by_text("Filters", exact=False).first.wait_for(timeout=15_000)
            except PWTimeoutError:
                print("[WARN] Filters not visible -> hard refresh")
                if not hard_refresh(page, URL, tries=2):
                    raise RuntimeError("Page not loading after hard refresh.")
                wait_spa_ready(page)

            open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
            open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)

            click_apply(page)
            wait_for_settled(page, timeout_ms=25_000)

            # Ensure vendor list exists
            try:
                page.locator(HEADER_ACTION_SEL).first.wait_for(timeout=25_000)
            except Exception:
                print("[WARN] Vendor list not visible after Apply -> refresh + re-apply once")
                if not hard_refresh(page, URL, tries=2):
                    raise RuntimeError("Hard refresh failed after empty results.")
                wait_spa_ready(page)
                open_dropdown_and_select_with_refresh(page, "Select State", STATE_NAME)
                open_dropdown_and_select_with_refresh(page, "Select District", DISTRICT_NAME)
                click_apply(page)
                wait_for_settled(page, timeout_ms=25_000)

            # 1) Load all vendors
            load_all_vendors(page)

            # 2) Extract details (now includes company_name)
            extract_all_vendors_after_loading(page)

        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            dump_debug(page, prefix="pmsuryaghar_fail")
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
