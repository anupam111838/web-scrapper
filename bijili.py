# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import csv
# import time
# import re
# import os
# import hashlib
# from pathlib import Path

# URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

# STATE_NAME = "GUJARAT"
# DISTRICT_NAME = "Mahisagar"

# OUT_CSV =  DISTRICT_NAME +".csv"
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
#     "company_name",  # ✅ ADDED
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
#     """
#     Create CSV with header if missing.
#     If file exists but header is different, rename old file and create new.
#     """
#     p = Path(path)
#     if p.exists() and p.stat().st_size > 0:
#         try:
#             first = p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()[0].strip()
#             expected = ",".join(CSV_HEADER)
#             if first.replace("\ufeff", "") != expected:
#                 ts = int(time.time())
#                 backup = p.with_suffix(p.suffix + f".bak_{ts}")
#                 p.rename(backup)
#                 print(f"[WARN] Existing CSV header mismatch. Renamed old file to: {backup}")
#         except Exception:
#             pass

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
# # Extraction helpers
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
#     Return all accordion header actions + aria-controls + header text + parsed company name.
#     """
#     return page.evaluate(
#         r"""
#         () => {
#           function clean(s){ return (s||"").replace(/\s+/g," ").trim(); }
#           function isNumericLine(s){ return /^\d[\d,]*$/.test((s||"").trim()); }
#           function isLabelLine(s){
#             const up = (s||"").toUpperCase();
#             return up.startsWith("BRAND NAME")
#               || /NO\.?\s*OF\s*INSTALLATIONS/.test(up);
#           }

#           const els = Array.from(document.querySelectorAll("[id$='_header_action'][aria-controls]"));
#           return els.map(el => {
#             const text = (el.innerText || el.textContent || "").trim();
#             const lines = text.split("\n").map(x => clean(x)).filter(Boolean);

#             let company = "";
#             for (const ln of lines){
#               if (isLabelLine(ln)) continue;
#               if (isNumericLine(ln)) continue;
#               company = ln;
#               break;
#             }

#             return {
#               id: el.id,
#               controls: el.getAttribute("aria-controls") || "",
#               expanded: (el.getAttribute("aria-expanded") || "").toLowerCase(),
#               text,
#               company_name: company
#             };
#           });
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
#     Find expanded content using aria-controls (reliable for PrimeNG accordion),
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

#           function extractEmails(s){
#             // return any email-like chunks OR deobfuscated string if no obvious emails
#             const raw = (s||"").trim();
#             const deob = deobfuscateEmail(raw);
#             const found = deob.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/ig) || [];
#             const uniq = [];
#             for (const e of found) if (!uniq.includes(e)) uniq.push(e);
#             if (uniq.length) return uniq.join("|");
#             return deob || "";
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

#           const emails = emailsRaw ? extractEmails(emailsRaw) : "";
#           const phones = phonesRaw ? extractPhones(phonesRaw) : "";
#           const cap = capRaw ? firstNumber(capRaw) : "";
#           const inst = instRaw ? firstNumber(instRaw) : "";

#           return { ok:true, emails, phones, cap, inst, controls };
#         }
#         """,
#         header_id,
#     )


# def make_seen_key(company_name: str, emails: str, phones: str, cap: str, inst: str) -> str:
#     basis = (company_name or "").strip().lower()
#     basis += "||" + (phones or "").strip().lower()
#     basis += "||" + (emails or "").strip().lower()
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
#             company_name = (item.get("company_name") or "").strip()

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

#             if not (company_name or emails or phones or cap or inst):
#                 continue

#             key = make_seen_key(company_name, emails, phones, cap, inst)
#             if key in seen:
#                 continue

#             append_row_realtime(
#                 OUT_CSV,
#                 {
#                     "state": STATE_NAME,
#                     "district": DISTRICT_NAME,
#                     "company_name": company_name,
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

#             # 2) Extract details (now includes company_name)
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

























# ---------------------------------------------------------------------------------------------working code------------------------------------------------------

# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import csv
# import time
# import re
# import os
# import hashlib
# from pathlib import Path

# URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

# STATE_NAME = "GUJARAT"
# DISTRICT_NAME = "Dahod"

# OUT_CSV = DISTRICT_NAME + ".csv"
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
#     "company_name",
#     "contact_name",  # ✅ ADDED (example value: EXECUTIVE)
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
#     """
#     Create CSV with header if missing.
#     If file exists but header is different, rename old file and create new.
#     """
#     p = Path(path)
#     if p.exists() and p.stat().st_size > 0:
#         try:
#             first = p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()[0].strip()
#             expected = ",".join(CSV_HEADER)
#             if first.replace("\ufeff", "") != expected:
#                 ts = int(time.time())
#                 backup = p.with_suffix(p.suffix + f".bak_{ts}")
#                 p.rename(backup)
#                 print(f"[WARN] Existing CSV header mismatch. Renamed old file to: {backup}")
#         except Exception:
#             pass

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
# # Extraction helpers
# # -------------------------
# def normalize_phone_list(s: str) -> str:
#     """Keep multiple numbers separated by '|', do NOT merge into one digit blob."""
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
#     Return all accordion header actions + aria-controls + header text + parsed company name.
#     """
#     return page.evaluate(
#         r"""
#         () => {
#           function clean(s){ return (s||"").replace(/\s+/g," ").trim(); }
#           function isNumericLine(s){ return /^\d[\d,]*$/.test((s||"").trim()); }
#           function isLabelLine(s){
#             const up = (s||"").toUpperCase();
#             return up.startsWith("BRAND NAME")
#               || /NO\.?\s*OF\s*INSTALLATIONS/.test(up);
#           }

#           const els = Array.from(document.querySelectorAll("[id$='_header_action'][aria-controls]"));
#           return els.map(el => {
#             const text = (el.innerText || el.textContent || "").trim();
#             const lines = text.split("\n").map(x => clean(x)).filter(Boolean);

#             let company = "";
#             for (const ln of lines){
#               if (isLabelLine(ln)) continue;
#               if (isNumericLine(ln)) continue;
#               company = ln;
#               break;
#             }

#             return {
#               id: el.id,
#               controls: el.getAttribute("aria-controls") || "",
#               expanded: (el.getAttribute("aria-expanded") || "").toLowerCase(),
#               text,
#               company_name: company
#             };
#           });
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
#     Uses aria-controls to find expanded panel.
#     Extracts: CONTACT (name/designation), EMAIL(S), CONTACT NUMBER(S), CAPACITY, INSTALLATIONS.
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

#           // 1) Canonicalize the most specific labels FIRST
#           txt = txt.replace(/EMAIL\s*\(S\)/gi, "___EMAILS___");
#           txt = txt.replace(/CONTACT\s*NUMBER\s*\(S\)/gi, "___CONTACT_NUMBERS___");
#           txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY\s*\(\s*kwp\s*\)/gi, "___CAPACITY_KWP___");
#           txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY/gi, "___CAPACITY___");
#           txt = txt.replace(/NO\.\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");
#           txt = txt.replace(/NO\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");

#           // 2) CONTACT label (avoid clashing with CONTACT NUMBER(S))
#           txt = txt.replace(/CONTACT\s+NAME/gi, "___CONTACT___");
#           txt = txt.replace(/CONTACT\s+PERSON/gi, "___CONTACT___");
#           // CONTACT as standalone line
#           txt = txt.replace(/(^|\n)\s*CONTACT\s*(?=\n|$)/gi, "$1___CONTACT___");

#           // Inject newlines around placeholders to stabilize parsing
#           txt = txt.replace(/___CONTACT___/g, "\nCONTACT\n");
#           txt = txt.replace(/___EMAILS___/g, "\nEMAIL(S)\n");
#           txt = txt.replace(/___CONTACT_NUMBERS___/g, "\nCONTACT NUMBER(S)\n");
#           txt = txt.replace(/___CAPACITY_KWP___/g, "\nTOTAL INSTALLED CAPACITY (KWP)\n");
#           txt = txt.replace(/___CAPACITY___/g, "\nTOTAL INSTALLED CAPACITY\n");
#           txt = txt.replace(/___INSTALLATIONS___/g, "\nNO. OF INSTALLATIONS\n");

#           txt = txt.replace(/[ \t]+\n/g, "\n").replace(/\n{2,}/g, "\n").trim();
#           const lines = txt.split("\n").map(cleanLine).filter(Boolean);

#           const ALL_LABELS = new Set([
#             "CONTACT",
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

#               // exact label
#               if (up === want){
#                 for (let j=i+1; j<Math.min(lines.length, i+12); j++){
#                   if (isLabel(lines[j])) break;
#                   if (lines[j]) return lines[j];
#                 }
#               }

#               // label + inline value on same line
#               if (up.startsWith(want + " ")){
#                 return lines[i].slice(label.length).trim();
#               }
#             }
#             return "";
#           }

#           let contactRaw = valueAfter("CONTACT");
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

#           function extractEmails(s){
#             const raw = (s||"").trim();
#             const deob = deobfuscateEmail(raw);
#             const found = deob.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/ig) || [];
#             const uniq = [];
#             for (const e of found) if (!uniq.includes(e)) uniq.push(e);
#             if (uniq.length) return uniq.join("|");
#             return deob || "";
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

#           const contact_name = contactRaw ? cleanLine(contactRaw) : "";
#           const emails = emailsRaw ? extractEmails(emailsRaw) : "";
#           const phones = phonesRaw ? extractPhones(phonesRaw) : "";
#           const cap = capRaw ? firstNumber(capRaw) : "";
#           const inst = instRaw ? firstNumber(instRaw) : "";

#           return { ok:true, contact_name, emails, phones, cap, inst, controls };
#         }
#         """,
#         header_id,
#     )


# def make_seen_key(company_name: str, contact_name: str, emails: str, phones: str, cap: str, inst: str) -> str:
#     basis = (company_name or "").strip().lower()
#     basis += "||" + (contact_name or "").strip().lower()
#     basis += "||" + (phones or "").strip().lower()
#     basis += "||" + (emails or "").strip().lower()
#     basis += f"||{cap or ''}||{inst or ''}"
#     return hashlib.blake2b(basis.encode("utf-8"), digest_size=16).hexdigest()


# def wait_until_vendor_values(page, header_id: str, header_text: str, timeout_ms: int):
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     while time.time() < deadline:
#         out = extract_fields_from_vendor(page, header_id)
#         last = out

#         if out.get("ok"):
#             contact_name = (out.get("contact_name") or "").strip()
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

#             if contact_name or emails or phones or cap or inst:
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
#             company_name = (item.get("company_name") or "").strip()

#             if not hid or hid in processed_ids:
#                 continue
#             processed_ids.add(hid)

#             expand_header_by_id(page, hid)
#             page.wait_for_timeout(150)

#             data = wait_until_vendor_values(page, hid, htxt, timeout_ms=EXTRACT_WAIT_PER_VENDOR_MS)

#             contact_name = (data.get("contact_name") or "").strip()
#             emails = (data.get("emails") or "").strip()
#             phones = (data.get("phones") or "").strip()
#             cap = pick_first_number((data.get("cap") or "").strip())
#             inst = pick_first_number((data.get("inst") or "").strip())

#             phones = normalize_phone_list(phones)

#             if not (company_name or contact_name or emails or phones or cap or inst):
#                 continue

#             key = make_seen_key(company_name, contact_name, emails, phones, cap, inst)
#             if key in seen:
#                 continue

#             append_row_realtime(
#                 OUT_CSV,
#                 {
#                     "state": STATE_NAME,
#                     "district": DISTRICT_NAME,
#                     "company_name": company_name,
#                     "contact_name": contact_name,
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

#             # 2) Extract details (now includes contact_name)
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



# -------------------------------------------------------------modified code-------------------------------------------------------------

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import csv
import time
import re
import os
import hashlib
from pathlib import Path

URL = "https://pmsuryaghar.gov.in/#/registered-vendors"

# =========================
# ✅ INPUTS
# =========================
REPORT_FILTER_VALUE = "State Wise Installations DESC"   # <-- your exact option text
STATE_NAME = "GUJARAT"
DISTRICT_NAME = "Ahmedabad"

OUT_CSV = DISTRICT_NAME + ".csv"
SEEN_FILE = OUT_CSV + ".seen"

# VIEW
HEADLESS = False
SLOW_MO_MS = 60
WAIT_MS = 60_000

# Dropdown empty -> refresh retry
OPTIONS_WAIT_MS = 20_000
MAX_REFRESH_RETRIES = 6  # for filters apply loop

# Load more
LOAD_MORE_MAX_CLICKS = 600
LOAD_MORE_STUCK_LIMIT = 5  # stop after 5 no-growth tries
LOAD_MORE_POST_CLICK_WAIT_MS = 25_000

# Extraction
EXTRACT_WAIT_PER_VENDOR_MS = 12_000
SCROLL_PAUSE_MS = 120

# If list is virtualized, do a few passes
RECHECK_NEW_HEADERS_PASSES = 4

CSV_HEADER = [
    "state",
    "district",
    "company_name",
    "contact_name",
    "emails",
    "contact_numbers",
    "total_installed_capacity_kwp",
    "no_of_installations",
]

# =========================
# Selectors: PrimeNG p-dropdown (Report filter)
# =========================
PDROPDOWN_ROOT = ".p-dropdown.p-component"
PDROPDOWN_TRIGGER = ".p-dropdown-trigger"
PDROPDOWN_LABEL = ".p-dropdown-label"
PDROPDOWN_PANEL = ".p-dropdown-panel"
PDROPDOWN_ITEM = ".p-dropdown-item"
PDROPDOWN_ITEMS_WRAPPER = ".p-dropdown-items-wrapper"
PDROPDOWN_FILTER_INPUT = "input.p-dropdown-filter"

# =========================
# Selectors: Vendor list
# =========================
HEADER_ACTION_SEL = "[id$='_header_action'][aria-controls]"


# -------------------------
# Disk-safe CSV helpers
# -------------------------
def _fsync_file(f):
    f.flush()
    os.fsync(f.fileno())


def ensure_csv_header(path: str):
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


def error_toast_visible(page) -> bool:
    try:
        return (
            page.get_by_text("Error 500", exact=False).first.is_visible()
            or page.get_by_text("Unable to fetch", exact=False).first.is_visible()
        )
    except Exception:
        return False


# -------------------------
# Filters panel scoping
# -------------------------
def get_filters_panel(page):
    filters_txt = page.get_by_text("Filters", exact=False).first
    filters_txt.wait_for(timeout=15_000)
    panel = filters_txt.locator(
        "xpath=ancestor::div[.//button[contains(normalize-space(.),'Apply')]][1]"
    ).first
    return panel


# -------------------------
# Helpers: normalization / close overlays
# -------------------------
def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("…", "").replace("...", "")).strip().lower()


def close_any_dropdown(page):
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass
    page.wait_for_timeout(200)


def report_label_text(panel) -> str:
    try:
        dd = panel.locator(PDROPDOWN_ROOT).first
        if dd.count() == 0:
            return ""
        return (dd.locator(PDROPDOWN_LABEL).first.inner_text() or "").strip()
    except Exception:
        return ""


def report_is_selected(panel, wanted_text: str) -> bool:
    lab = _norm(report_label_text(panel))
    want = _norm(wanted_text)
    return (want in lab) or (lab in want and lab != "")


# -------------------------
# ✅ Report dropdown select (PrimeNG p-dropdown-trigger)
# -------------------------
def select_report_filter_once(panel, page, value_text: str) -> bool:
    """
    Try selecting REPORT_FILTER_VALUE once (no refresh inside).
    Returns True only if label verification passes.
    """
    wanted_raw = (value_text or "").strip()
    wanted = _norm(wanted_raw)

    if report_is_selected(panel, wanted_raw):
        print(f"[OK] Report filter already selected: {report_label_text(panel)}")
        return True

    dd = panel.locator(PDROPDOWN_ROOT).first
    if dd.count() == 0:
        print("[WARN] Report p-dropdown not found in Filters panel.")
        return False

    close_any_dropdown(page)

    # Open dropdown (try trigger, fallback click whole dropdown)
    try:
        trig = dd.locator(PDROPDOWN_TRIGGER).first
        if trig.count() > 0:
            trig.click(force=True)
        else:
            dd.click(force=True)
    except Exception:
        try:
            dd.click(force=True)
        except Exception:
            return False

    # Wait visible panel
    try:
        overlay = page.locator(f"{PDROPDOWN_PANEL}:visible").last
        overlay.wait_for(state="visible", timeout=OPTIONS_WAIT_MS)
    except Exception:
        print("[WARN] Report dropdown panel did not open.")
        close_any_dropdown(page)
        return False

    # If filter input exists, type
    try:
        filt = overlay.locator(PDROPDOWN_FILTER_INPUT).first
        if filt.count() > 0 and filt.is_visible():
            filt.click()
            filt.fill("")
            filt.type(wanted_raw, delay=25)
            page.wait_for_timeout(250)
    except Exception:
        pass

    items = overlay.locator("li[role='option'], .p-dropdown-item")
    wrapper = overlay.locator(PDROPDOWN_ITEMS_WRAPPER).first

    # Try to find + click while scrolling
    clicked = False
    for _ in range(80):
        try:
            # exact match
            opt = items.filter(has_text=re.compile(rf"^\s*{re.escape(wanted_raw)}\s*$", re.I)).first
            if opt.count() == 0:
                # contains match
                opt = items.filter(has_text=re.compile(re.escape(wanted_raw), re.I)).first

            if opt.count() > 0:
                opt.scroll_into_view_if_needed()
                opt.click(force=True)
                clicked = True
                break
        except Exception:
            pass

        # scroll down inside panel
        try:
            if wrapper.count() > 0:
                wrapper.evaluate("el => { el.scrollTop = el.scrollTop + el.clientHeight * 0.85; }")
        except Exception:
            pass

        page.wait_for_timeout(120)

    if not clicked:
        print(f"[WARN] Could not find/click report option: {wanted_raw}")
        close_any_dropdown(page)
        return False

    # Wait UI update and verify label
    page.wait_for_timeout(500)
    lab = report_label_text(panel)
    ok = (wanted in _norm(lab)) or (_norm(lab) in wanted and _norm(lab) != "")
    print(f"[INFO] Report label after click = '{lab}' (wanted='{wanted_raw}')")
    return ok


# -------------------------
# ng-select dropdown handling (State/District)
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


def click_placeholder_dropdown_in_panel(panel, placeholder_text: str):
    loc = panel.get_by_text(placeholder_text, exact=False).first
    loc.wait_for(state="visible", timeout=WAIT_MS)
    loc.click(force=True)


def open_ngselect_and_select_with_refresh(panel, page, placeholder: str, value_text: str):
    for attempt in range(1, MAX_REFRESH_RETRIES + 1):
        click_placeholder_dropdown_in_panel(panel, placeholder)

        ok = wait_for_any_options(page, OPTIONS_WAIT_MS)
        if not ok:
            _type_in_search_if_present(page, value_text)
            ok = wait_for_any_options(page, 7000)

        if ok and click_option_case_insensitive(page, value_text):
            page.wait_for_timeout(500)
            return

        close_any_dropdown(page)
        print(f"[WARN] '{placeholder}' empty / '{value_text}' not found. Refresh retry {attempt}/{MAX_REFRESH_RETRIES}")
        if not hard_refresh(page, URL, tries=2):
            raise RuntimeError("Hard refresh failed while recovering dropdown empty state.")
        wait_spa_ready(page)
        panel = get_filters_panel(page)

    raise RuntimeError(f"Could not select '{value_text}' from '{placeholder}' after refresh retries.")


def click_apply(panel):
    btn = panel.get_by_role("button", name="Apply").first
    if btn.count() == 0:
        btn = panel.locator("button:has-text('Apply')").first
    btn.wait_for(state="visible", timeout=WAIT_MS)
    btn.click(force=True)


# -------------------------
# ✅ Apply all filters with refresh-if-report-not-changed
# -------------------------
def apply_filters_with_retry(page):
    """
    If report filter doesn't actually change, hard refresh and re-apply everything.
    """
    for attempt in range(1, MAX_REFRESH_RETRIES + 1):
        panel = get_filters_panel(page)

        print(f"[INFO] Applying filters attempt {attempt}/{MAX_REFRESH_RETRIES}")
        print(f"       Report(before) = '{report_label_text(panel)}'")

        ok_report = select_report_filter_once(panel, page, REPORT_FILTER_VALUE)
        panel = get_filters_panel(page)  # avoid stale locators

        if not ok_report:
            print("[WARN] Report value did NOT change -> hard refresh and retry full apply")
            if not hard_refresh(page, URL, tries=2):
                raise RuntimeError("Hard refresh failed while fixing report dropdown selection.")
            wait_spa_ready(page)
            continue

        print(f"       Report(after)  = '{report_label_text(panel)}'")

        # State/District + Apply
        open_ngselect_and_select_with_refresh(panel, page, "Select State", STATE_NAME)
        panel = get_filters_panel(page)
        open_ngselect_and_select_with_refresh(panel, page, "Select District", DISTRICT_NAME)
        panel = get_filters_panel(page)

        click_apply(panel)
        wait_for_settled(page, timeout_ms=25_000)

        # Error 500 toast -> refresh and retry full apply
        if error_toast_visible(page):
            print("[WARN] Error toast detected after Apply -> refresh and retry full apply")
            page.wait_for_timeout(6000)
            if not hard_refresh(page, URL, tries=2):
                raise RuntimeError("Hard refresh failed after Error 500.")
            wait_spa_ready(page)
            continue

        # Ensure vendor list exists
        try:
            page.locator(HEADER_ACTION_SEL).first.wait_for(timeout=25_000)
        except Exception:
            print("[WARN] Vendor list not visible after Apply -> refresh and retry full apply")
            if not hard_refresh(page, URL, tries=2):
                raise RuntimeError("Hard refresh failed after empty results.")
            wait_spa_ready(page)
            continue

        return  # ✅ success

    raise RuntimeError("Failed to apply filters reliably after multiple refresh attempts.")


# -------------------------
# Vendor list helpers
# -------------------------
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
# Extraction
# -------------------------
def normalize_phone_list(s: str) -> str:
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
    return page.evaluate(
        r"""
        (hid) => {
          function cleanLine(s){ return (s||"").replace(/\s+/g," ").trim(); }

          const header = document.getElementById(hid);
          if (!header) return {ok:false, reason:"no-header"};

          const controls = header.getAttribute("aria-controls") || "";
          let region = null;

          if (controls) region = document.getElementById(controls);
          if (!region) region = document.querySelector(`div[role='region'][aria-labelledby='${hid}']`);
          if (!region) {
            const base = hid.replace(/_header_action$/, "_header");
            region = document.querySelector(`div[role='region'][aria-labelledby='${base}']`);
          }
          if (!region) return {ok:false, reason:"no-region", controls};

          let txt = (region.innerText || region.textContent || "")
            .replace(/\u00a0/g, " ")
            .replace(/\r/g, "\n");

          txt = txt.replace(/EMAIL\s*\(S\)/gi, "___EMAILS___");
          txt = txt.replace(/CONTACT\s*NUMBER\s*\(S\)/gi, "___CONTACT_NUMBERS___");
          txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY\s*\(\s*kwp\s*\)/gi, "___CAPACITY_KWP___");
          txt = txt.replace(/TOTAL\s*INSTALLED\s*CAPACITY/gi, "___CAPACITY___");
          txt = txt.replace(/NO\.\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");
          txt = txt.replace(/NO\s*OF\s*INSTALLATIONS/gi, "___INSTALLATIONS___");

          txt = txt.replace(/CONTACT\s+NAME/gi, "___CONTACT___");
          txt = txt.replace(/CONTACT\s+PERSON/gi, "___CONTACT___");
          txt = txt.replace(/(^|\n)\s*CONTACT\s*(?=\n|$)/gi, "$1___CONTACT___");

          txt = txt.replace(/___CONTACT___/g, "\nCONTACT\n");
          txt = txt.replace(/___EMAILS___/g, "\nEMAIL(S)\n");
          txt = txt.replace(/___CONTACT_NUMBERS___/g, "\nCONTACT NUMBER(S)\n");
          txt = txt.replace(/___CAPACITY_KWP___/g, "\nTOTAL INSTALLED CAPACITY (KWP)\n");
          txt = txt.replace(/___CAPACITY___/g, "\nTOTAL INSTALLED CAPACITY\n");
          txt = txt.replace(/___INSTALLATIONS___/g, "\nNO. OF INSTALLATIONS\n");

          txt = txt.replace(/[ \t]+\n/g, "\n").replace(/\n{2,}/g, "\n").trim();
          const lines = txt.split("\n").map(cleanLine).filter(Boolean);

          const ALL_LABELS = new Set([
            "CONTACT","EMAIL(S)","CONTACT NUMBER(S)",
            "TOTAL INSTALLED CAPACITY (KWP)","TOTAL INSTALLED CAPACITY",
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

          let contactRaw = valueAfter("CONTACT");
          let emailsRaw = valueAfter("EMAIL(S)");
          let phonesRaw = valueAfter("CONTACT NUMBER(S)");
          let capRaw = valueAfter("TOTAL INSTALLED CAPACITY (KWP)") || valueAfter("TOTAL INSTALLED CAPACITY");
          let instRaw = valueAfter("NO. OF INSTALLATIONS");

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

          const contact_name = contactRaw ? cleanLine(contactRaw) : "";
          const emails = emailsRaw ? extractEmails(emailsRaw) : "";
          const phones = phonesRaw ? extractPhones(phonesRaw) : "";
          const cap = capRaw ? firstNumber(capRaw) : "";
          const inst = instRaw ? firstNumber(instRaw) : "";

          return { ok:true, contact_name, emails, phones, cap, inst, controls };
        }
        """,
        header_id,
    )


def make_seen_key(company_name: str, contact_name: str, emails: str, phones: str, cap: str, inst: str) -> str:
    basis = (company_name or "").strip().lower()
    basis += "||" + (contact_name or "").strip().lower()
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
            contact_name = (out.get("contact_name") or "").strip()
            emails = (out.get("emails") or "").strip()
            phones = (out.get("phones") or "").strip()
            cap = (out.get("cap") or "").strip()
            inst = (out.get("inst") or "").strip()

            if not inst:
                m = re.search(r"(\d[\d,]*)\s*$", header_text or "")
                if m:
                    inst = m.group(1).replace(",", "")
                    out["inst"] = inst

            if contact_name or emails or phones or cap or inst:
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

            contact_name = (data.get("contact_name") or "").strip()
            emails = (data.get("emails") or "").strip()
            phones = (data.get("phones") or "").strip()
            cap = pick_first_number((data.get("cap") or "").strip())
            inst = pick_first_number((data.get("inst") or "").strip())

            phones = normalize_phone_list(phones)

            if not (company_name or contact_name or emails or phones or cap or inst):
                continue

            key = make_seen_key(company_name, contact_name, emails, phones, cap, inst)
            if key in seen:
                continue

            append_row_realtime(
                OUT_CSV,
                {
                    "state": STATE_NAME,
                    "district": DISTRICT_NAME,
                    "company_name": company_name,
                    "contact_name": contact_name,
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

            # ✅ Apply filters with refresh loop if report value doesn’t change
            apply_filters_with_retry(page)

            # ✅ Load all vendors
            load_all_vendors(page)

            # ✅ Extract
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
