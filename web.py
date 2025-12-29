# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import pandas as pd
# import time
# from pathlib import Path

# URL = "https://kys.udiseplus.gov.in/#/advancesearch"

# STATE = "GUJARAT"
# DISTRICT = "AHMEDABAD"
# BLOCK = "AMC"
# OUT_CSV = "clusters_guj_ahd_amc.csv"

# ADV_BTN_SELECTOR = ".advanceSearchBtn"
# SELECTS_SELECTOR = "select.form-select.select"

# # ✅ All major waits/timeouts = 1 minute
# WAIT_MS = 60_000


# # ---------------------------
# # Debug helpers
# # ---------------------------
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


# def wait_and_click_advanced(page, timeout_ms=WAIT_MS):
#     """Wait up to 1 minute for Advanced Search button, then click."""
#     page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=timeout_ms)
#     page.locator(ADV_BTN_SELECTOR).first.click(force=True)
#     page.wait_for_timeout(1200)


# def get_select_by_index(page, idx, timeout_ms=WAIT_MS):
#     """Wait up to 1 minute until there are at least idx+1 selects, then return that select."""
#     deadline = time.time() + timeout_ms / 1000
#     while time.time() < deadline:
#         sels = page.locator(SELECTS_SELECTOR)
#         if sels.count() >= (idx + 1):
#             sel = sels.nth(idx)
#             if sel.is_visible():
#                 return sel
#         page.wait_for_timeout(400)
#     raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


# def pick_option_by_text(select_locator, target_text):
#     """
#     Select matching option by visible text (case-insensitive).
#     Uses value if available, else selects by label.
#     """
#     target = target_text.strip().lower()
#     options = select_locator.locator("option")
#     if options.count() == 0:
#         raise PWTimeoutError("No <option> found inside select.")

#     chosen_value = None
#     for i in range(options.count()):
#         opt = options.nth(i)
#         label = (opt.inner_text() or "").strip()
#         value = opt.get_attribute("value") or ""
#         if label.lower() == target:
#             chosen_value = value
#             break

#     if chosen_value is not None and chosen_value != "":
#         select_locator.select_option(value=chosen_value)
#     else:
#         # fallback to label selection
#         select_locator.select_option(label=target_text)


# def extract_all_option_texts(select_locator):
#     """Extract all option texts, excluding placeholders."""
#     options = select_locator.locator("option")
#     out = []
#     for i in range(options.count()):
#         t = (options.nth(i).inner_text() or "").strip()
#         if not t:
#             continue
#         low = t.lower()
#         if low in {"select", "choose", "all", "--select--", "select one"}:
#             continue
#         out.append(t)

#     # de-dup preserve order
#     seen = set()
#     uniq = []
#     for x in out:
#         if x not in seen:
#             seen.add(x)
#             uniq.append(x)
#     return uniq


# def main(headless=False):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless, args=["--no-sandbox"])
#         context = browser.new_context(
#             viewport={"width": 1366, "height": 768},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()

#         # ✅ Default timeout also 1 minute
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)

#             # 1) Click Advanced Search (wait max 1 min)
#             wait_and_click_advanced(page, timeout_ms=WAIT_MS)

#             # 2) Get selects (wait max 1 min each)
#             # Assumed order: 0=State, 1=District, 2=Block, 3=Cluster
#             state_sel = get_select_by_index(page, 0, timeout_ms=WAIT_MS)
#             district_sel = get_select_by_index(page, 1, timeout_ms=WAIT_MS)
#             block_sel = get_select_by_index(page, 2, timeout_ms=WAIT_MS)

#             # 3) Select State -> District -> Block
#             pick_option_by_text(state_sel, STATE)
#             page.wait_for_timeout(1200)

#             pick_option_by_text(district_sel, DISTRICT)
#             page.wait_for_timeout(1200)

#             pick_option_by_text(block_sel, BLOCK)
#             page.wait_for_timeout(1500)

#             # 4) Cluster dropdown (assumed index 3)
#             cluster_sel = get_select_by_index(page, 3, timeout_ms=WAIT_MS)
#             clusters = extract_all_option_texts(cluster_sel)

#             # 5) Save CSV
#             df = pd.DataFrame({
#                 "state": [STATE] * len(clusters),
#                 "district": [DISTRICT] * len(clusters),
#                 "block": [BLOCK] * len(clusters),
#                 "cluster": clusters
#             })
#             df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
#             print(f"Saved {len(clusters)} clusters -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="kys_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     # Run headed once to confirm; then switch to headless=True
#     main(headless=False)


# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import pandas as pd
# import time
# from pathlib import Path

# URL = "https://kys.udiseplus.gov.in/#/advancesearch"

# STATE = "GUJARAT"
# DISTRICT = "AHMEDABAD"

# OUT_CSV = "kys_extract_guj_ahd_all_blocks_all_pages.csv"

# # ---------------------------
# # Selectors
# # ---------------------------
# ADV_BTN_SELECTOR = ".advanceSearchBtn"
# SELECTS_SELECTOR = "select.form-select.select"

# SEARCH_BTN_SELECTOR = ".purpleBtn"
# NEXT_BTN_SELECTOR = ".nextBtn"

# # School name (header)
# SCHOOL_NAME_SEL = ".fw-600"

# # ✅ value selector: custom-word-break mt-2 mb-1 (with blueCol fallback)
# VALUE_SEL = ".custom-word-break.mt-2.mb-1, .blueCol.custom-word-break.mt-2.mb-1"

# # ✅ block option hint (as you asked)
# BLOCK_OPTION_HINT = ".ng-star-inserted"

# # ---------------------------
# # Timeouts
# # ---------------------------
# WAIT_MS = 60_000  # 1 minute


# # ---------------------------
# # Debug helpers
# # ---------------------------
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


# def wait_and_click_advanced(page, timeout_ms=WAIT_MS):
#     page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=timeout_ms)
#     page.locator(ADV_BTN_SELECTOR).first.click(force=True)
#     page.wait_for_timeout(1200)


# def get_select_by_index(page, idx, timeout_ms=WAIT_MS):
#     deadline = time.time() + timeout_ms / 1000
#     while time.time() < deadline:
#         sels = page.locator(SELECTS_SELECTOR)
#         if sels.count() >= (idx + 1):
#             sel = sels.nth(idx)
#             if sel.is_visible():
#                 return sel
#         page.wait_for_timeout(400)
#     raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


# def pick_option_by_text(select_locator, target_text):
#     """Select matching option by visible text (case-insensitive)."""
#     target = target_text.strip().lower()
#     options = select_locator.locator("option")
#     if options.count() == 0:
#         raise PWTimeoutError("No <option> found inside select.")

#     chosen_value = None
#     for i in range(options.count()):
#         opt = options.nth(i)
#         label = (opt.inner_text() or "").strip()
#         value = opt.get_attribute("value") or ""
#         if label.lower() == target:
#             chosen_value = value
#             break

#     if chosen_value is not None and chosen_value != "":
#         select_locator.select_option(value=chosen_value)
#     else:
#         select_locator.select_option(label=target_text)


# def extract_select_option_texts(select_locator, require_ng_star=False):
#     """
#     Extract option texts from a <select>.
#     If require_ng_star=True, prefer options that have class 'ng-star-inserted'
#     (but still fallback to all options if none matched).
#     """
#     options = select_locator.locator("option")
#     out = []

#     # pass 1: only ng-star-inserted options (if requested)
#     if require_ng_star:
#         for i in range(options.count()):
#             opt = options.nth(i)
#             cls = (opt.get_attribute("class") or "")
#             if "ng-star-inserted" not in cls:
#                 continue
#             t = (opt.inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     # pass 2: fallback to all options if nothing found
#     if not out:
#         for i in range(options.count()):
#             t = (options.nth(i).inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     # clean placeholders + dedup
#     cleaned = []
#     for t in out:
#         low = t.strip().lower()
#         if not t.strip():
#             continue
#         if low in {"select", "choose", "all", "--select--", "select one"}:
#             continue
#         cleaned.append(t.strip())

#     seen = set()
#     uniq = []
#     for x in cleaned:
#         if x not in seen:
#             seen.add(x)
#             uniq.append(x)
#     return uniq


# def click_search(page, timeout_ms=WAIT_MS):
#     page.wait_for_selector(SEARCH_BTN_SELECTOR, state="visible", timeout=timeout_ms)
#     page.locator(SEARCH_BTN_SELECTOR).first.click(force=True)

#     # Wait up to 1 minute for results
#     try:
#         page.wait_for_load_state("networkidle", timeout=timeout_ms)
#     except Exception:
#         pass
#     page.wait_for_selector(VALUE_SEL, state="visible", timeout=timeout_ms)
#     page.wait_for_timeout(800)


# def extract_current_page_records(page):
#     """
#     Extract records for current results page.

#     - school_name = first .fw-600 text per container
#     - other fields: header (.fw-600 in same row) -> value (.custom-word-break.mt-2.mb-1)
#     """
#     js = r"""
#     () => {
#       const SCHOOL_NAME_SEL = '.fw-600';
#       const VALUE_SEL = '.custom-word-break.mt-2.mb-1, .blueCol.custom-word-break.mt-2.mb-1';

#       const valueEls = Array.from(document.querySelectorAll(VALUE_SEL));
#       if (valueEls.length === 0) return [];

#       function groupRoot(el) {
#         let cur = el;
#         while (cur && cur !== document.body) {
#           const cls = (cur.className || '').toString();
#           if (/(card|panel|result|box|item|list|accordion|table|mat-card|mat-expansion|ng-star-inserted)/i.test(cls)) {
#             return cur;
#           }
#           cur = cur.parentElement;
#         }
#         return document.body;
#       }

#       const groups = new Map();
#       for (const v of valueEls) {
#         const root = groupRoot(v);
#         if (!groups.has(root)) groups.set(root, []);
#         groups.get(root).push(v);
#       }

#       function cleanKey(s) {
#         return (s || '').trim().replace(/[:\s]+$/g, '');
#       }
#       function textOf(el) {
#         return (el?.textContent || '').trim();
#       }

#       function extractFromRoot(root) {
#         const obj = {};

#         // school name = first fw-600 in this root
#         const sn = root.querySelector(SCHOOL_NAME_SEL);
#         const schoolName = cleanKey(textOf(sn));
#         if (schoolName) obj["school_name"] = schoolName;

#         const vals = Array.from(root.querySelectorAll(VALUE_SEL));
#         const seenRows = new Set();

#         for (const v of vals) {
#           const row = v.closest('div,li,tr,td') || v.parentElement;
#           if (!row || seenRows.has(row)) continue;
#           seenRows.add(row);

#           const value = textOf(row.querySelector(VALUE_SEL));
#           if (!value) continue;

#           const headers = Array.from(row.querySelectorAll(SCHOOL_NAME_SEL));
#           if (!headers.length) continue;

#           // choose a header that's not the main school name when possible
#           let h = null;
#           for (const hh of headers) {
#             if (sn && hh === sn) continue;
#             h = hh;
#             break;
#           }
#           if (!h) h = headers[0];

#           const key = cleanKey(textOf(h));
#           if (!key) continue;

#           if (obj[key] === undefined) obj[key] = value;
#           else {
#             let n = 2;
#             while (obj[`${key}_${n}`] !== undefined) n += 1;
#             obj[`${key}_${n}`] = value;
#           }
#         }

#         return Object.keys(obj).length ? obj : null;
#       }

#       const records = [];
#       for (const [root] of groups.entries()) {
#         const rec = extractFromRoot(root);
#         if (rec) records.push(rec);
#       }

#       if (records.length === 0) {
#         const rec = extractFromRoot(document.body);
#         if (rec) records.push(rec);
#       }

#       return records;
#     }
#     """
#     return page.evaluate(js)


# def next_button_available(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     if btn.count() == 0:
#         return False
#     if not btn.is_visible():
#         return False
#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass
#     cls = (btn.get_attribute("class") or "").lower()
#     if "disabled" in cls:
#         return False
#     aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
#     if aria_disabled in {"true", "1"}:
#         return False
#     disabled_attr = btn.get_attribute("disabled")
#     if disabled_attr is not None:
#         return False
#     return True


# def click_next_and_wait(page, prev_marker=None, timeout_ms=WAIT_MS):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     btn.scroll_into_view_if_needed()
#     btn.click(force=True)

#     # wait up to 1 minute for "page change"
#     deadline = time.time() + timeout_ms / 1000
#     while time.time() < deadline:
#         try:
#             if page.locator(VALUE_SEL).count() > 0:
#                 if prev_marker:
#                     cur_marker = ""
#                     sn = page.locator(SCHOOL_NAME_SEL).first
#                     if sn.count() > 0:
#                         cur_marker = (sn.inner_text() or "").strip()
#                     if cur_marker and cur_marker != prev_marker:
#                         return
#                 else:
#                     return
#         except Exception:
#             pass
#         page.wait_for_timeout(500)

#     page.wait_for_selector(VALUE_SEL, state="visible", timeout=timeout_ms)


# def extract_all_pages_for_current_block(page, state, district, block, block_index):
#     """Extract results for current selected block across pagination."""
#     all_records = []
#     page_no = 1

#     while True:
#         records = extract_current_page_records(page)

#         for r in records:
#             r.setdefault("state", state)
#             r.setdefault("district", district)
#             r.setdefault("block", block)
#             r.setdefault("block_index", block_index)
#             r.setdefault("page_no", page_no)
#         all_records.extend(records)

#         if not next_button_available(page):
#             break

#         prev_marker = ""
#         sn = page.locator(SCHOOL_NAME_SEL).first
#         if sn.count() > 0:
#             prev_marker = (sn.inner_text() or "").strip()

#         click_next_and_wait(page, prev_marker=prev_marker, timeout_ms=WAIT_MS)
#         page_no += 1

#     return all_records, page_no


# def main(headless=False):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless, args=["--no-sandbox"])
#         context = browser.new_context(
#             viewport={"width": 1366, "height": 768},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)

#             # 1) Advanced search
#             wait_and_click_advanced(page, timeout_ms=WAIT_MS)

#             # 2) Select State/District/Block selects (assumed order 0/1/2)
#             state_sel = get_select_by_index(page, 0, timeout_ms=WAIT_MS)
#             district_sel = get_select_by_index(page, 1, timeout_ms=WAIT_MS)
#             block_sel = get_select_by_index(page, 2, timeout_ms=WAIT_MS)

#             # 3) Set State + District
#             pick_option_by_text(state_sel, STATE)
#             page.wait_for_timeout(1200)

#             pick_option_by_text(district_sel, DISTRICT)
#             page.wait_for_timeout(1500)

#             # 4) Extract all blocks from the block dropdown (prefer ng-star-inserted options)
#             blocks = extract_select_option_texts(block_sel, require_ng_star=True)

#             if not blocks:
#                 raise RuntimeError("No blocks found in block dropdown.")

#             print(f"Found {len(blocks)} blocks for district={DISTRICT}: {blocks}")

#             # 5) For each block: select -> search -> paginate extract
#             all_records = []
#             total_pages = 0

#             for i, blk in enumerate(blocks, start=1):
#                 print(f"\n[BLOCK {i}/{len(blocks)}] Selecting block: {blk}")

#                 pick_option_by_text(block_sel, blk)
#                 page.wait_for_timeout(1200)

#                 # Click purple button to load results for this block
#                 click_search(page, timeout_ms=WAIT_MS)

#                 records, pages = extract_all_pages_for_current_block(
#                     page=page,
#                     state=STATE,
#                     district=DISTRICT,
#                     block=blk,
#                     block_index=i
#                 )
#                 all_records.extend(records)
#                 total_pages += pages

#                 print(f"[BLOCK DONE] {blk} -> rows: {len(records)} | pages: {pages}")

#             # 6) Save CSV
#             if not all_records:
#                 raise RuntimeError("No records extracted across all blocks.")

#             df = pd.DataFrame(all_records)

#             # Put common columns first
#             front = [c for c in ["state", "district", "block", "block_index", "page_no", "school_name"] if c in df.columns]
#             rest = [c for c in df.columns if c not in front]
#             df = df[front + rest]

#             df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
#             print(f"\nSaved {len(df)} row(s) across {len(blocks)} blocks -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="kys_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main(headless=False)  # run headed once; then set True



# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import pandas as pd
# import time
# from pathlib import Path

# URL = "https://kys.udiseplus.gov.in/#/advancesearch"

# STATE = "GUJARAT"
# DISTRICT = "AHMEDABAD"

# # ✅ Realtime output (append as we scrape)
# OUT_CSV = "kys_realtime_guj_ahd_all_blocks_all_pages_long.csv"

# # ---------------------------
# # Selectors
# # ---------------------------
# ADV_BTN_SELECTOR = ".advanceSearchBtn"
# SELECTS_SELECTOR = "select.form-select.select"
# SEARCH_BTN_SELECTOR = ".purpleBtn"
# NEXT_BTN_SELECTOR = ".nextBtn"

# # school name is from fw-600
# SCHOOL_NAME_SEL = ".fw-600"

# # ✅ value selector updated
# VALUE_SEL = ".custom-word-break.mt-2.mb-1, .blueCol.custom-word-break.mt-2.mb-1"

# # ---------------------------
# # Timeouts / waits
# # ---------------------------
# WAIT_MS = 20_000  # ✅ 20 seconds
# WAIT_AFTER_ACTION_MS = 20_000  # ✅ wait 20s then scrape


# # ---------------------------
# # Debug helpers
# # ---------------------------
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


# # ---------------------------
# # CSV realtime writer (stable schema)
# # ---------------------------
# def append_rows_realtime(rows, out_csv=OUT_CSV):
#     """
#     Append rows to CSV in realtime (safe schema: long format).
#     """
#     if not rows:
#         return
#     out_path = Path(out_csv)
#     df = pd.DataFrame(rows)
#     df.to_csv(
#         out_path,
#         mode="a",
#         index=False,
#         header=not out_path.exists(),
#         encoding="utf-8-sig",
#     )


# # ---------------------------
# # Page interaction helpers
# # ---------------------------
# def wait_and_click_advanced(page):
#     page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(ADV_BTN_SELECTOR).first.click(force=True)
#     page.wait_for_timeout(800)


# def get_select_by_index(page, idx):
#     deadline = time.time() + WAIT_MS / 1000
#     while time.time() < deadline:
#         sels = page.locator(SELECTS_SELECTOR)
#         if sels.count() >= (idx + 1):
#             sel = sels.nth(idx)
#             if sel.is_visible():
#                 return sel
#         page.wait_for_timeout(200)
#     raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


# def pick_option_by_text(select_locator, target_text):
#     target = target_text.strip().lower()
#     options = select_locator.locator("option")
#     if options.count() == 0:
#         raise PWTimeoutError("No <option> found inside select.")

#     chosen_value = None
#     for i in range(options.count()):
#         opt = options.nth(i)
#         label = (opt.inner_text() or "").strip()
#         value = opt.get_attribute("value") or ""
#         if label.lower() == target:
#             chosen_value = value
#             break

#     if chosen_value is not None and chosen_value != "":
#         select_locator.select_option(value=chosen_value)
#     else:
#         select_locator.select_option(label=target_text)


# def extract_select_option_texts(select_locator):
#     """
#     Extract block names from <select> options.
#     Prefers options that have class 'ng-star-inserted' (your requirement),
#     but falls back to all options if needed.
#     """
#     options = select_locator.locator("option")
#     out = []

#     # pass 1: prefer ng-star-inserted
#     for i in range(options.count()):
#         opt = options.nth(i)
#         cls = (opt.get_attribute("class") or "")
#         if "ng-star-inserted" not in cls:
#             continue
#         t = (opt.inner_text() or "").strip()
#         if t:
#             out.append(t)

#     # pass 2: fallback
#     if not out:
#         for i in range(options.count()):
#             t = (options.nth(i).inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     # clean placeholders + dedup
#     cleaned = []
#     for t in out:
#         low = t.strip().lower()
#         if not t.strip():
#             continue
#         if low in {"select", "choose", "all", "--select--", "select one"}:
#             continue
#         cleaned.append(t.strip())

#     seen = set()
#     uniq = []
#     for x in cleaned:
#         if x not in seen:
#             seen.add(x)
#             uniq.append(x)
#     return uniq


# def click_search_and_wait_20s(page):
#     page.wait_for_selector(SEARCH_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(SEARCH_BTN_SELECTOR).first.click(force=True)

#     # ✅ wait 20 seconds then scrape
#     page.wait_for_timeout(WAIT_AFTER_ACTION_MS)


# def next_button_available(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     if btn.count() == 0:
#         return False
#     if not btn.is_visible():
#         return False
#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass
#     cls = (btn.get_attribute("class") or "").lower()
#     if "disabled" in cls:
#         return False
#     aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
#     if aria_disabled in {"true", "1"}:
#         return False
#     disabled_attr = btn.get_attribute("disabled")
#     if disabled_attr is not None:
#         return False
#     return True


# def click_next_and_wait_20s(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     btn.scroll_into_view_if_needed()
#     btn.click(force=True)

#     # ✅ wait 20 seconds then scrape
#     page.wait_for_timeout(WAIT_AFTER_ACTION_MS)


# # ---------------------------
# # Extraction (returns list[dict])
# # ---------------------------
# def extract_current_page_records(page):
#     """
#     Extract per "school card/group":
#       - school_name = first .fw-600 text
#       - other fields: header (.fw-600 in same row) -> value (.custom-word-break.mt-2.mb-1...)
#     """
#     js = r"""
#     () => {
#       const SCHOOL_NAME_SEL = '.fw-600';
#       const VALUE_SEL = '.custom-word-break.mt-2.mb-1, .blueCol.custom-word-break.mt-2.mb-1';

#       const valueEls = Array.from(document.querySelectorAll(VALUE_SEL));
#       if (valueEls.length === 0) return [];

#       function groupRoot(el) {
#         let cur = el;
#         while (cur && cur !== document.body) {
#           const cls = (cur.className || '').toString();
#           if (/(card|panel|result|box|item|list|accordion|table|mat-card|mat-expansion|ng-star-inserted)/i.test(cls)) {
#             return cur;
#           }
#           cur = cur.parentElement;
#         }
#         return document.body;
#       }

#       const groups = new Map();
#       for (const v of valueEls) {
#         const root = groupRoot(v);
#         if (!groups.has(root)) groups.set(root, []);
#         groups.get(root).push(v);
#       }

#       function cleanKey(s) {
#         return (s || '').trim().replace(/[:\s]+$/g, '');
#       }
#       function textOf(el) {
#         return (el?.textContent || '').trim();
#       }

#       function extractFromRoot(root) {
#         const obj = {};

#         const sn = root.querySelector(SCHOOL_NAME_SEL);
#         const schoolName = cleanKey(textOf(sn));
#         if (schoolName) obj["school_name"] = schoolName;

#         const vals = Array.from(root.querySelectorAll(VALUE_SEL));
#         const seenRows = new Set();

#         for (const v of vals) {
#           const row = v.closest('div,li,tr,td') || v.parentElement;
#           if (!row || seenRows.has(row)) continue;
#           seenRows.add(row);

#           const value = textOf(row.querySelector(VALUE_SEL));
#           if (!value) continue;

#           const headers = Array.from(row.querySelectorAll(SCHOOL_NAME_SEL));
#           if (!headers.length) continue;

#           let h = null;
#           for (const hh of headers) {
#             if (sn && hh === sn) continue;
#             h = hh;
#             break;
#           }
#           if (!h) h = headers[0];

#           const key = cleanKey(textOf(h));
#           if (!key) continue;

#           if (obj[key] === undefined) obj[key] = value;
#           else {
#             let n = 2;
#             while (obj[`${key}_${n}`] !== undefined) n += 1;
#             obj[`${key}_${n}`] = value;
#           }
#         }

#         return Object.keys(obj).length ? obj : null;
#       }

#       const records = [];
#       for (const [root] of groups.entries()) {
#         const rec = extractFromRoot(root);
#         if (rec) records.push(rec);
#       }

#       if (records.length === 0) {
#         const rec = extractFromRoot(document.body);
#         if (rec) records.push(rec);
#       }

#       return records;
#     }
#     """
#     return page.evaluate(js)


# def dict_records_to_long_rows(records, state, district, block, block_index, page_no):
#     """
#     Convert dict records (variable keys) -> long rows (stable columns) for realtime CSV.
#     One row per (school_name, field, value).
#     """
#     rows = []
#     for r in records or []:
#         school_name = r.get("school_name", "")
#         for k, v in r.items():
#             if k in {"school_name"}:
#                 continue
#             rows.append(
#                 {
#                     "state": state,
#                     "district": district,
#                     "block": block,
#                     "block_index": block_index,
#                     "page_no": page_no,
#                     "school_name": school_name,
#                     "field": k,
#                     "value": v,
#                 }
#             )

#         # if only school_name exists, still write one row so you can see progress
#         if len(r.keys()) == 1 and school_name:
#             rows.append(
#                 {
#                     "state": state,
#                     "district": district,
#                     "block": block,
#                     "block_index": block_index,
#                     "page_no": page_no,
#                     "school_name": school_name,
#                     "field": "",
#                     "value": "",
#                 }
#             )
#     return rows


# # ---------------------------
# # Main
# # ---------------------------
# def main(headless=False):
#     # (optional) clear old file each run
#     out_path = Path(OUT_CSV)
#     if out_path.exists():
#         out_path.unlink()

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless, args=["--no-sandbox"])
#         context = browser.new_context(
#             viewport={"width": 1366, "height": 768},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()

#         # ✅ default timeout 20 seconds
#         page.set_default_timeout(WAIT_MS)

#         total_written = 0

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             page.wait_for_timeout(1000)

#             # 1) Advanced search
#             wait_and_click_advanced(page)

#             # 2) Select dropdowns (assumed: 0=State, 1=District, 2=Block)
#             state_sel = get_select_by_index(page, 0)
#             district_sel = get_select_by_index(page, 1)
#             block_sel = get_select_by_index(page, 2)

#             # 3) Set State + District
#             pick_option_by_text(state_sel, STATE)
#             page.wait_for_timeout(600)

#             pick_option_by_text(district_sel, DISTRICT)
#             page.wait_for_timeout(800)

#             # 4) Get all blocks and loop
#             blocks = extract_select_option_texts(block_sel)
#             if not blocks:
#                 raise RuntimeError("No blocks found in block dropdown.")

#             print(f"Found {len(blocks)} blocks: {blocks}")

#             for bi, blk in enumerate(blocks, start=1):
#                 print(f"\n[BLOCK {bi}/{len(blocks)}] {blk}")
#                 pick_option_by_text(block_sel, blk)
#                 page.wait_for_timeout(600)

#                 # Search + wait 20s
#                 click_search_and_wait_20s(page)

#                 page_no = 1
#                 while True:
#                     records = extract_current_page_records(page)

#                     # realtime save for this page
#                     rows = dict_records_to_long_rows(
#                         records=records,
#                         state=STATE,
#                         district=DISTRICT,
#                         block=blk,
#                         block_index=bi,
#                         page_no=page_no,
#                     )
#                     append_rows_realtime(rows, OUT_CSV)
#                     total_written += len(rows)

#                     print(f"  page {page_no}: records={len(records)} | rows_written_now={len(rows)} | total_rows={total_written}")

#                     if not next_button_available(page):
#                         break

#                     click_next_and_wait_20s(page)
#                     page_no += 1

#             print(f"\nDONE ✅ Total rows written: {total_written}")
#             print(f"Saved realtime CSV -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="kys_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main(headless=False)  # run headed once, then set True





# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import pandas as pd
# import time
# from pathlib import Path

# URL = "https://kys.udiseplus.gov.in/#/advancesearch"

# STATE = "GUJARAT"
# DISTRICT = "AHMEDABAD"

# OUT_CSV = "kys_realtime_guj_ahd_all_blocks_all_pages.csv"

# # ---------------------------
# # Selectors
# # ---------------------------
# ADV_BTN_SELECTOR = ".advanceSearchBtn"
# SELECTS_SELECTOR = "select.form-select.select"
# SEARCH_BTN_SELECTOR = ".purpleBtn"
# NEXT_BTN_SELECTOR = ".nextBtn"

# HEADER_SEL = ".fw-600"
# FIELD_VALUE_SEL = ".blueCol.custom-word-break"
# SCHOOL_NAME_VALUE_SEL = ".custom-word-break.mt-2.mb-1"

# # ---------------------------
# # Timeouts / waits
# # ---------------------------
# WAIT_MS = 30_000                 # max waits
# WAIT_AFTER_ACTION_MS = 30_000    # ✅ minimum wait after Search/Next (your requirement)

# # If a page is slow, we additionally wait for DOM to "settle" up to this limit:
# SETTLE_TIMEOUT_MS = 90_000


# # ---------------------------
# # Debug helpers
# # ---------------------------
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


# # ---------------------------
# # Realtime writer (wide format)
# # ---------------------------
# def write_realtime_wide(all_records, out_csv=OUT_CSV):
#     """
#     Wide CSV. We OVERWRITE after each page so columns stay consistent as new keys appear.
#     Only columns produced: state, district, block, school_name, plus extracted fields.
#     """
#     if not all_records:
#         return
#     df = pd.DataFrame(all_records)
#     front = [c for c in ["state", "district", "block", "school_name"] if c in df.columns]
#     rest = [c for c in df.columns if c not in front]
#     df = df[front + rest]
#     df.to_csv(out_csv, index=False, encoding="utf-8-sig")


# # ---------------------------
# # Page interaction helpers
# # ---------------------------
# def wait_and_click_advanced(page):
#     page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(ADV_BTN_SELECTOR).first.click(force=True)
#     page.wait_for_timeout(1000)


# def get_select_by_index(page, idx):
#     deadline = time.time() + WAIT_MS / 1000
#     while time.time() < deadline:
#         sels = page.locator(SELECTS_SELECTOR)
#         if sels.count() >= (idx + 1):
#             sel = sels.nth(idx)
#             if sel.is_visible():
#                 return sel
#         page.wait_for_timeout(250)
#     raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


# def pick_option_by_text(select_locator, target_text):
#     target = target_text.strip().lower()
#     options = select_locator.locator("option")
#     if options.count() == 0:
#         raise PWTimeoutError("No <option> found inside select.")

#     chosen_value = None
#     for i in range(options.count()):
#         opt = options.nth(i)
#         label = (opt.inner_text() or "").strip()
#         value = opt.get_attribute("value") or ""
#         if label.lower() == target:
#             chosen_value = value
#             break

#     if chosen_value is not None and chosen_value != "":
#         select_locator.select_option(value=chosen_value)
#     else:
#         select_locator.select_option(label=target_text)


# def extract_block_names(block_select_locator):
#     """Extract block names from <select> options (prefers ng-star-inserted)."""
#     options = block_select_locator.locator("option")
#     out = []

#     for i in range(options.count()):
#         opt = options.nth(i)
#         cls = (opt.get_attribute("class") or "")
#         if "ng-star-inserted" not in cls:
#             continue
#         t = (opt.inner_text() or "").strip()
#         if t:
#             out.append(t)

#     if not out:
#         for i in range(options.count()):
#             t = (options.nth(i).inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     cleaned = []
#     for t in out:
#         low = t.strip().lower()
#         if not t.strip():
#             continue
#         if low in {"select", "choose", "all", "--select--", "select one"}:
#             continue
#         cleaned.append(t.strip())

#     seen = set()
#     uniq = []
#     for x in cleaned:
#         if x not in seen:
#             seen.add(x)
#             uniq.append(x)
#     return uniq


# def click_search(page):
#     page.wait_for_selector(SEARCH_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(SEARCH_BTN_SELECTOR).first.click(force=True)

#     # ✅ minimum wait
#     page.wait_for_timeout(WAIT_AFTER_ACTION_MS)


# def next_button_available(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     if btn.count() == 0:
#         return False
#     if not btn.is_visible():
#         return False
#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass
#     cls = (btn.get_attribute("class") or "").lower()
#     if "disabled" in cls:
#         return False
#     aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
#     if aria_disabled in {"true", "1"}:
#         return False
#     if btn.get_attribute("disabled") is not None:
#         return False
#     return True


# def click_next(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     btn.scroll_into_view_if_needed()
#     btn.click(force=True)

#     # ✅ minimum wait
#     page.wait_for_timeout(WAIT_AFTER_ACTION_MS)


# # ---------------------------
# # Robust waiting / settling
# # ---------------------------
# def wait_for_dom_settle(page, timeout_ms=SETTLE_TIMEOUT_MS, stable_checks=5, interval_ms=600):
#     """
#     Wait until counts of important elements stop changing for stable_checks intervals.
#     This prevents scraping while Angular is still updating.
#     """
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     stable = 0

#     while time.time() < deadline:
#         stats = page.evaluate(
#             """
#             (sels) => {
#               const sn = document.querySelectorAll(sels.school).length;
#               const h  = document.querySelectorAll(sels.header).length;
#               const v  = document.querySelectorAll(sels.value).length;
#               const tlen = (document.body && document.body.innerText) ? document.body.innerText.length : 0;
#               return {sn, h, v, tlen};
#             }
#             """,
#             {"school": SCHOOL_NAME_VALUE_SEL, "header": HEADER_SEL, "value": FIELD_VALUE_SEL},
#         )

#         if last == stats and stats["sn"] > 0:
#             stable += 1
#             if stable >= stable_checks:
#                 return
#         else:
#             stable = 0
#             last = stats

#         page.wait_for_timeout(interval_ms)


# # ---------------------------
# # Scrolling (handles virtualized lists)
# # ---------------------------
# def scroll_to_top(page):
#     page.evaluate(
#         """
#         () => {
#           function pickScrollable() {
#             const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#             if (preferred) return preferred;

#             const candidates = Array.from(document.querySelectorAll('*'))
#               .filter(el => {
#                 const st = getComputedStyle(el);
#                 const oy = st.overflowY || '';
#                 return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#               });

#             // choose the one containing most school_name nodes
#             let best = null, bestScore = -1;
#             for (const el of candidates) {
#               const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#               if (score > bestScore) { bestScore = score; best = el; }
#             }
#             return best || null;
#           }

#           const el = pickScrollable();
#           if (el) el.scrollTop = 0;
#           else window.scrollTo(0, 0);
#         }
#         """
#     )
#     page.wait_for_timeout(500)


# def scroll_step(page, step_px=900):
#     """
#     Scroll inside the best scroll container (virtual scroll or overflow container).
#     Returns at_bottom True when we reached end.
#     """
#     return page.evaluate(
#         """
#         (stepPx) => {
#           function pickScrollable() {
#             const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#             if (preferred) return {type: 'el', el: preferred};

#             const candidates = Array.from(document.querySelectorAll('*'))
#               .filter(el => {
#                 const st = getComputedStyle(el);
#                 const oy = st.overflowY || '';
#                 return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#               });

#             let best = null, bestScore = -1;
#             for (const el of candidates) {
#               const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#               if (score > bestScore) { bestScore = score; best = el; }
#             }
#             if (best) return {type: 'el', el: best};

#             return {type: 'win', el: null};
#           }

#           const target = pickScrollable();

#           if (target.type === 'win') {
#             const before = window.scrollY;
#             const max = document.documentElement.scrollHeight - window.innerHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             window.scrollTo(0, after);
#             return {before, after, max, at_bottom: after >= max - 2, mode: 'window'};
#           } else {
#             const el = target.el;
#             const before = el.scrollTop;
#             const max = el.scrollHeight - el.clientHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             el.scrollTop = after;
#             return {before, after, max, at_bottom: after >= max - 2, mode: 'element'};
#           }
#         }
#         """,
#         step_px,
#     )


# # ---------------------------
# # Extraction (wide dict per record)
# # ---------------------------
# def extract_current_dom_records(page):
#     """
#     Extract records visible in current DOM:
#     - school_name from .custom-word-break.mt-2.mb-1
#     - header from .fw-600
#     - value from .blueCol.custom-word-break
#     - if header text missing => unknown_#
#     """
#     js = r"""
#     () => {
#       const HEADER_SEL = '.fw-600';
#       const VALUE_SEL = '.blueCol.custom-word-break';
#       const SCHOOL_SEL = '.custom-word-break.mt-2.mb-1';

#       const schoolEls = Array.from(document.querySelectorAll(SCHOOL_SEL));
#       const valueEls  = Array.from(document.querySelectorAll(VALUE_SEL));
#       if (schoolEls.length === 0 && valueEls.length === 0) return [];

#       function clean(s) { return (s || '').trim(); }
#       function cleanKey(s) { return clean(s).replace(/[:\s]+$/g, ''); }

#       function bestRoot(el) {
#         let cur = el;
#         for (let i=0; i<10 && cur && cur !== document.body; i++) {
#           const p = cur.parentElement;
#           if (!p) break;
#           const h = p.querySelectorAll(HEADER_SEL).length;
#           const v = p.querySelectorAll(VALUE_SEL).length;
#           const s = p.querySelectorAll(SCHOOL_SEL).length;
#           if (v >= 2 && (h >= 1 || v >= 4) && s >= 1) return p;
#           cur = p;
#         }
#         return el.parentElement || document.body;
#       }

#       const roots = new Set();
#       for (const sEl of schoolEls) roots.add(bestRoot(sEl));
#       if (roots.size === 0) roots.add(document.body);

#       function extractFromRoot(root) {
#         const obj = {};

#         // school_name
#         const snEl = root.querySelector(SCHOOL_SEL);
#         const sn = cleanKey(snEl ? snEl.textContent : '');
#         if (sn) obj.school_name = sn;

#         // row-based pairing via values (more reliable if headers sometimes blank)
#         const vals = Array.from(root.querySelectorAll(VALUE_SEL));
#         let unk = 0;

#         for (const vEl of vals) {
#           const row = vEl.closest('div,li,tr,td') || vEl.parentElement;
#           const val = clean(vEl.textContent);
#           if (!val) continue;

#           let key = '';
#           if (row) {
#             const hEl = row.querySelector(HEADER_SEL);
#             if (hEl) key = cleanKey(hEl.textContent || '');
#           }

#           if (!key) {
#             // fallback: try previous siblings
#             let prev = vEl.previousElementSibling;
#             while (prev && !prev.matches(HEADER_SEL)) prev = prev.previousElementSibling;
#             if (prev) key = cleanKey(prev.textContent || '');
#           }

#           if (!key) {
#             unk += 1;
#             key = `unknown_${unk}`;
#           }

#           // avoid overwriting school_name accidentally
#           if (key.toLowerCase() === 'school name' && !obj.school_name) {
#             obj.school_name = val;
#             continue;
#           }

#           if (obj[key] === undefined) obj[key] = val;
#           else {
#             let n = 2;
#             while (obj[`${key}_${n}`] !== undefined) n += 1;
#             obj[`${key}_${n}`] = val;
#           }
#         }

#         return Object.keys(obj).length ? obj : null;
#       }

#       const out = [];
#       for (const r of roots) {
#         const rec = extractFromRoot(r);
#         if (rec) out.push(rec);
#       }
#       return out;
#     }
#     """
#     return page.evaluate(js)


# def record_uid(rec: dict) -> str:
#     """
#     Create a stable unique id for merging while scrolling.
#     Prefer any UDISE-like field if present; else use school_name.
#     """
#     if not rec:
#         return ""
#     # try udise-ish keys
#     for k, v in rec.items():
#         if k and isinstance(k, str) and "udise" in k.lower():
#             vv = str(v).strip()
#             if vv:
#                 return f"UDISE::{vv}"
#     sn = str(rec.get("school_name", "")).strip()
#     if sn:
#         return f"SN::{sn}"
#     # last fallback
#     return f"RAW::{hash(tuple(sorted(rec.items())))}"


# def collect_full_page_records(page, max_steps=80):
#     """
#     Handles virtual scroll: repeatedly scrape visible DOM, scroll down, and merge new records.
#     Stops when bottom reached and no new records found for a few steps.
#     """
#     # ensure page has loaded something
#     wait_for_dom_settle(page)

#     collected = {}
#     no_new_steps = 0

#     scroll_to_top(page)
#     wait_for_dom_settle(page)

#     for _ in range(max_steps):
#         dom_recs = extract_current_dom_records(page)
#         new_added = 0

#         for r in dom_recs:
#             uid = record_uid(r)
#             if not uid:
#                 continue
#             if uid not in collected:
#                 collected[uid] = r
#                 new_added += 1
#             else:
#                 # merge: keep existing, add missing keys
#                 old = collected[uid]
#                 for k, v in r.items():
#                     if k not in old or (not old.get(k) and v):
#                         old[k] = v

#         if new_added == 0:
#             no_new_steps += 1
#         else:
#             no_new_steps = 0

#         info = scroll_step(page, step_px=900)
#         page.wait_for_timeout(500)
#         wait_for_dom_settle(page, timeout_ms=20_000, stable_checks=3, interval_ms=500)

#         if info.get("at_bottom") and no_new_steps >= 3:
#             # one last scrape at bottom
#             dom_recs = extract_current_dom_records(page)
#             for r in dom_recs:
#                 uid = record_uid(r)
#                 if uid and uid not in collected:
#                     collected[uid] = r
#             break

#     return list(collected.values())


# # ---------------------------
# # Main
# # ---------------------------
# def main(headless=False):
#     out_path = Path(OUT_CSV)
#     if out_path.exists():
#         out_path.unlink()

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless, args=["--no-sandbox"])
#         context = browser.new_context(
#             viewport={"width": 1366, "height": 768},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         all_records = []

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             page.wait_for_timeout(1500)

#             wait_and_click_advanced(page)

#             # Dropdown order assumed: 0=State, 1=District, 2=Block
#             state_sel = get_select_by_index(page, 0)
#             district_sel = get_select_by_index(page, 1)
#             block_sel = get_select_by_index(page, 2)

#             pick_option_by_text(state_sel, STATE)
#             page.wait_for_timeout(900)

#             pick_option_by_text(district_sel, DISTRICT)
#             page.wait_for_timeout(1200)

#             blocks = extract_block_names(block_sel)
#             if not blocks:
#                 raise RuntimeError("No blocks found in block dropdown.")
#             print(f"Found {len(blocks)} blocks: {blocks}")

#             for blk in blocks:
#                 print(f"\n[BLOCK] {blk}")
#                 pick_option_by_text(block_sel, blk)
#                 page.wait_for_timeout(900)

#                 click_search(page)
#                 wait_for_dom_settle(page)

#                 while True:
#                     # ✅ scrape FULL page (handles virtual scroll)
#                     page_records = collect_full_page_records(page)

#                     for r in page_records:
#                         r.setdefault("state", STATE)
#                         r.setdefault("district", DISTRICT)
#                         r.setdefault("block", blk)

#                     all_records.extend(page_records)

#                     write_realtime_wide(all_records, OUT_CSV)
#                     print(f"  extracted this page: {len(page_records)} | total saved: {len(all_records)}")

#                     if not next_button_available(page):
#                         break

#                     click_next(page)
#                     wait_for_dom_settle(page)

#             print(f"\nDONE ✅ Total records saved: {len(all_records)}")
#             print(f"Saved -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="kys_fail")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main(headless=False)  # run headed once, then set headless=True










# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import pandas as pd
# from pandas.errors import EmptyDataError
# import time
# from pathlib import Path

# URL = "https://kys.udiseplus.gov.in/#/advancesearch"
# STATE = "GUJARAT"

# # ✅ Same file: resume if exists, else create it
# OUT_CSV = "kys_realtime_guj_ahd_all_blocks_all_pages.csv"

# # ---------------------------
# # Selectors
# # ---------------------------
# ADV_BTN_SELECTOR = ".advanceSearchBtn"
# SELECTS_SELECTOR = "select.form-select.select"
# SEARCH_BTN_SELECTOR = ".purpleBtn"
# NEXT_BTN_SELECTOR = ".nextBtn"

# # ✅ your extraction rules
# HEADER_SEL = ".fw-600"
# FIELD_VALUE_SEL = ".blueCol.custom-word-break"
# SCHOOL_NAME_VALUE_SEL = ".custom-word-break.mt-2.mb-1"

# # ---------------------------
# # Speed / accuracy tuning
# # ---------------------------
# WAIT_MS = 20_000            # selector timeout
# RESULTS_READY_MS = 30_000   # wait for results appear + stabilize
# SCROLL_MAX_STEPS = 65       # virtual scroll passes per page
# SCROLL_STEP_PX = 1400       # bigger = faster
# HEADLESS = False            # set False to see browser


# # ---------------------------
# # Debug helpers
# # ---------------------------
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


# # ---------------------------
# # CSV create/load/save (REALTIME)
# # ---------------------------
# def ensure_csv_exists(csv_path: str):
#     p = Path(csv_path)
#     if p.exists():
#         return
#     # create an empty CSV with base columns so you can open it immediately
#     pd.DataFrame(columns=["state", "district", "block", "school_name"]).to_csv(
#         csv_path, index=False, encoding="utf-8-sig"
#     )
#     print(f"[INIT] Created empty CSV -> {csv_path}")


# def record_uid(rec: dict) -> str:
#     """UID for dedupe/merge across pages/reruns."""
#     if not rec:
#         return ""
#     key_hints = ["udise", "school code", "sch code", "school id", "udise code", "udise no", "udise number"]
#     for k, v in rec.items():
#         if isinstance(k, str) and any(h in k.lower() for h in key_hints):
#             vv = str(v).strip()
#             if vv:
#                 return f"ID::{vv}"

#     sn = str(rec.get("school_name", "")).strip()
#     if sn:
#         extra = ""
#         for k, v in rec.items():
#             if k == "school_name":
#                 continue
#             vv = str(v).strip()
#             if vv:
#                 extra = vv
#                 break
#         return f"SN::{sn}::{extra}"

#     return f"RAW::{hash(tuple(sorted(rec.items())))}"


# def load_existing_global_records(csv_path: str):
#     """
#     Resume: load existing rows into dict so reruns don't duplicate.
#     Handles empty file safely.
#     """
#     p = Path(csv_path)
#     if not p.exists():
#         return {}

#     try:
#         df = pd.read_csv(p, dtype=str, keep_default_na=False)
#     except EmptyDataError:
#         return {}

#     if df.empty:
#         return {}

#     global_records = {}
#     for i, row in df.iterrows():
#         r = row.to_dict()
#         dist = (r.get("district", "") or "").strip()
#         blk = (r.get("block", "") or "").strip()
#         uid = record_uid(r) or f"ROW::{i}"
#         gkey = f"{dist}||{blk}||{uid}"
#         global_records[gkey] = r

#     print(f"[LOAD] Existing rows kept from CSV: {len(global_records)}")
#     return global_records


# def write_realtime_wide(global_records_dict, out_csv=OUT_CSV):
#     """
#     REALTIME write: overwrite the file so new columns appear immediately.
#     Keeps Ahmedabad rows at top (if present).
#     """
#     if not global_records_dict:
#         # keep empty file alive
#         ensure_csv_exists(out_csv)
#         return

#     df = pd.DataFrame(list(global_records_dict.values()))

#     if "district" in df.columns:
#         ahd = "AHMEDABAD"
#         df["_dist_sort"] = (
#             df["district"].fillna("").astype(str).str.strip().str.upper()
#             .apply(lambda x: 0 if x == ahd else 1)
#         )
#         sort_cols = ["_dist_sort", "district"]
#         if "block" in df.columns:
#             sort_cols.append("block")
#         if "school_name" in df.columns:
#             sort_cols.append("school_name")
#         df = df.sort_values(sort_cols, kind="stable").drop(columns=["_dist_sort"])

#     front = [c for c in ["state", "district", "block", "school_name"] if c in df.columns]
#     rest = [c for c in df.columns if c not in front]
#     df = df[front + rest]

#     df.to_csv(out_csv, index=False, encoding="utf-8-sig")


# # ---------------------------
# # Playwright helpers
# # ---------------------------
# def wait_and_click_advanced(page):
#     page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(ADV_BTN_SELECTOR).first.click(force=True)


# def get_select_by_index(page, idx):
#     deadline = time.time() + WAIT_MS / 1000
#     while time.time() < deadline:
#         sels = page.locator(SELECTS_SELECTOR)
#         if sels.count() >= (idx + 1):
#             sel = sels.nth(idx)
#             if sel.is_visible():
#                 return sel
#         page.wait_for_timeout(200)
#     raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


# def pick_option_by_text(select_locator, target_text):
#     target = target_text.strip().lower()
#     options = select_locator.locator("option")
#     if options.count() == 0:
#         raise PWTimeoutError("No <option> found inside select.")

#     chosen_value = None
#     for i in range(options.count()):
#         opt = options.nth(i)
#         label = (opt.inner_text() or "").strip()
#         value = opt.get_attribute("value") or ""
#         if label.lower() == target:
#             chosen_value = value
#             break

#     if chosen_value is not None and chosen_value != "":
#         select_locator.select_option(value=chosen_value)
#     else:
#         select_locator.select_option(label=target_text)


# def extract_option_texts(select_locator, prefer_ng_star=True):
#     options = select_locator.locator("option")
#     out = []

#     if prefer_ng_star:
#         for i in range(options.count()):
#             opt = options.nth(i)
#             cls = (opt.get_attribute("class") or "")
#             if "ng-star-inserted" not in cls:
#                 continue
#             t = (opt.inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     if not out:
#         for i in range(options.count()):
#             t = (options.nth(i).inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     cleaned = []
#     for t in out:
#         low = t.strip().lower()
#         if not t.strip():
#             continue
#         if low in {"select", "choose", "all", "--select--", "select one"}:
#             continue
#         cleaned.append(t.strip())

#     seen = set()
#     uniq = []
#     for x in cleaned:
#         if x not in seen:
#             seen.add(x)
#             uniq.append(x)
#     return uniq


# def next_button_available(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     if btn.count() == 0 or not btn.is_visible():
#         return False
#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass
#     cls = (btn.get_attribute("class") or "").lower()
#     if "disabled" in cls:
#         return False
#     aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
#     if aria_disabled in {"true", "1"}:
#         return False
#     if btn.get_attribute("disabled") is not None:
#         return False
#     return True


# # ---------------------------
# # Fast stable waiting (no fixed 30s sleep)
# # ---------------------------
# def wait_for_results_ready(page, timeout_ms=RESULTS_READY_MS):
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     stable = 0

#     # wait until at least one school appears (or timeout)
#     while time.time() < deadline:
#         if page.locator(SCHOOL_NAME_VALUE_SEL).count() > 0:
#             break
#         page.wait_for_timeout(200)

#     # stabilize
#     while time.time() < deadline:
#         stats = page.evaluate(
#             """
#             (sels) => ({
#               sn: document.querySelectorAll(sels.school).length,
#               h:  document.querySelectorAll(sels.header).length,
#               v:  document.querySelectorAll(sels.value).length,
#             })
#             """,
#             {"school": SCHOOL_NAME_VALUE_SEL, "header": HEADER_SEL, "value": FIELD_VALUE_SEL},
#         )
#         if stats == last and stats["sn"] > 0:
#             stable += 1
#             if stable >= 3:
#                 return
#         else:
#             stable = 0
#             last = stats
#         page.wait_for_timeout(250)


# def click_search(page):
#     page.wait_for_selector(SEARCH_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(SEARCH_BTN_SELECTOR).first.click(force=True)
#     wait_for_results_ready(page)


# def click_next(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     btn.scroll_into_view_if_needed()
#     btn.click(force=True)
#     wait_for_results_ready(page)


# # ---------------------------
# # Virtual-scroll safe scrolling
# # ---------------------------
# def scroll_to_top(page):
#     page.evaluate(
#         """
#         () => {
#           const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#           if (preferred) { preferred.scrollTop = 0; return; }

#           const candidates = Array.from(document.querySelectorAll('*'))
#             .filter(el => {
#               const st = getComputedStyle(el);
#               const oy = st.overflowY || '';
#               return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#             });

#           let best = null, bestScore = -1;
#           for (const el of candidates) {
#             const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#             if (score > bestScore) { bestScore = score; best = el; }
#           }
#           if (best) best.scrollTop = 0;
#           else window.scrollTo(0, 0);
#         }
#         """
#     )
#     page.wait_for_timeout(200)


# def scroll_step(page, step_px=SCROLL_STEP_PX):
#     return page.evaluate(
#         """
#         (stepPx) => {
#           function pickScrollable() {
#             const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#             if (preferred) return {type: 'el', el: preferred};

#             const candidates = Array.from(document.querySelectorAll('*'))
#               .filter(el => {
#                 const st = getComputedStyle(el);
#                 const oy = st.overflowY || '';
#                 return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#               });

#             let best = null, bestScore = -1;
#             for (const el of candidates) {
#               const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#               if (score > bestScore) { bestScore = score; best = el; }
#             }
#             if (best) return {type: 'el', el: best};

#             return {type: 'win', el: null};
#           }

#           const target = pickScrollable();

#           if (target.type === 'win') {
#             const before = window.scrollY;
#             const max = document.documentElement.scrollHeight - window.innerHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             window.scrollTo(0, after);
#             return {before, after, max, at_bottom: after >= max - 2};
#           } else {
#             const el = target.el;
#             const before = el.scrollTop;
#             const max = el.scrollHeight - el.clientHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             el.scrollTop = after;
#             return {before, after, max, at_bottom: after >= max - 2};
#           }
#         }
#         """,
#         step_px,
#     )


# # ---------------------------
# # Extraction (your exact rule)
# # ---------------------------
# def extract_current_dom_records(page):
#     js = r"""
#     () => {
#       const HEADER_SEL = '.fw-600';
#       const VALUE_SEL = '.blueCol.custom-word-break';
#       const SCHOOL_SEL = '.custom-word-break.mt-2.mb-1';

#       const schoolEls = Array.from(document.querySelectorAll(SCHOOL_SEL));
#       const valueEls  = Array.from(document.querySelectorAll(VALUE_SEL));
#       if (schoolEls.length === 0 && valueEls.length === 0) return [];

#       function clean(s) { return (s || '').trim(); }
#       function cleanKey(s) { return clean(s).replace(/[:\s]+$/g, ''); }

#       function bestRoot(el) {
#         let cur = el;
#         for (let i=0; i<10 && cur && cur !== document.body; i++) {
#           const p = cur.parentElement;
#           if (!p) break;
#           const h = p.querySelectorAll(HEADER_SEL).length;
#           const v = p.querySelectorAll(VALUE_SEL).length;
#           const s = p.querySelectorAll(SCHOOL_SEL).length;
#           if (v >= 2 && (h >= 1 || v >= 4) && s >= 1) return p;
#           cur = p;
#         }
#         return el.parentElement || document.body;
#       }

#       const roots = new Set();
#       for (const sEl of schoolEls) roots.add(bestRoot(sEl));
#       if (roots.size === 0) roots.add(document.body);

#       function extractFromRoot(root) {
#         const obj = {};

#         const snEl = root.querySelector(SCHOOL_SEL);
#         const sn = cleanKey(snEl ? snEl.textContent : '');
#         if (sn) obj.school_name = sn;

#         const vals = Array.from(root.querySelectorAll(VALUE_SEL));
#         let unk = 0;

#         for (const vEl of vals) {
#           const row = vEl.closest('div,li,tr,td') || vEl.parentElement;
#           const val = clean(vEl.textContent);
#           if (!val) continue;

#           let key = '';
#           if (row) {
#             const hEl = row.querySelector(HEADER_SEL);
#             if (hEl) key = cleanKey(hEl.textContent || '');
#           }

#           if (!key) {
#             let prev = vEl.previousElementSibling;
#             while (prev && !prev.matches(HEADER_SEL)) prev = prev.previousElementSibling;
#             if (prev) key = cleanKey(prev.textContent || '');
#           }

#           if (!key) {
#             unk += 1;
#             key = `unknown_${unk}`;
#           }

#           if (key.toLowerCase() === 'school name' && !obj.school_name) {
#             obj.school_name = val;
#             continue;
#           }

#           if (obj[key] === undefined) obj[key] = val;
#           else {
#             let n = 2;
#             while (obj[`${key}_${n}`] !== undefined) n += 1;
#             obj[`${key}_${n}`] = val;
#           }
#         }

#         return Object.keys(obj).length ? obj : null;
#       }

#       const out = [];
#       for (const r of roots) {
#         const rec = extractFromRoot(r);
#         if (rec) out.push(rec);
#       }
#       return out;
#     }
#     """
#     return page.evaluate(js)


# def collect_full_page_records(page):
#     scroll_to_top(page)
#     wait_for_results_ready(page)

#     collected = {}
#     no_new = 0

#     for _ in range(SCROLL_MAX_STEPS):
#         dom_recs = extract_current_dom_records(page)
#         new_added = 0

#         for r in dom_recs:
#             uid = record_uid(r)
#             if not uid:
#                 continue
#             if uid not in collected:
#                 collected[uid] = r
#                 new_added += 1
#             else:
#                 old = collected[uid]
#                 for k, v in r.items():
#                     if k not in old or (not old.get(k) and v):
#                         old[k] = v

#         no_new = no_new + 1 if new_added == 0 else 0

#         info = scroll_step(page, SCROLL_STEP_PX)
#         page.wait_for_timeout(200)

#         if info.get("at_bottom") and no_new >= 2:
#             break

#     return list(collected.values())


# # ---------------------------
# # Main
# # ---------------------------
# def main():
#     # ✅ Create file if missing (so you can open it immediately)
#     ensure_csv_exists(OUT_CSV)

#     # ✅ Resume from existing file
#     global_records = load_existing_global_records(OUT_CSV)
#     # ✅ Write immediately so you see file updated at start too
#     write_realtime_wide(global_records, OUT_CSV)

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=HEADLESS, args=["--no-sandbox"])
#         context = browser.new_context(
#             viewport={"width": 1366, "height": 768},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )
#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             wait_and_click_advanced(page)

#             # select order: 0=State, 1=District, 2=Block
#             state_sel = get_select_by_index(page, 0)
#             pick_option_by_text(state_sel, STATE)
#             page.wait_for_timeout(800)

#             district_sel = get_select_by_index(page, 1)
#             districts = extract_option_texts(district_sel, prefer_ng_star=True)
#             if not districts:
#                 raise RuntimeError("No districts found after selecting state.")

#             print(f"Districts total={len(districts)} (INCLUDING AHMEDABAD)")

#             for di, dist in enumerate(districts, start=1):
#                 print(f"\n[DISTRICT {di}/{len(districts)}] {dist}")

#                 district_sel = get_select_by_index(page, 1)
#                 pick_option_by_text(district_sel, dist)
#                 page.wait_for_timeout(900)

#                 block_sel = get_select_by_index(page, 2)
#                 blocks = extract_option_texts(block_sel, prefer_ng_star=True)
#                 if not blocks:
#                     print(f"  [WARN] No blocks for district={dist}, skipping.")
#                     continue
#                 print(f"  Blocks={len(blocks)}")

#                 for bi, blk in enumerate(blocks, start=1):
#                     print(f"  [BLOCK {bi}/{len(blocks)}] {blk}")

#                     block_sel = get_select_by_index(page, 2)
#                     pick_option_by_text(block_sel, blk)
#                     page.wait_for_timeout(300)

#                     click_search(page)

#                     page_no = 0
#                     while True:
#                         before = len(global_records)

#                         page_records = collect_full_page_records(page)

#                         changed = False
#                         for r in page_records:
#                             r.setdefault("state", STATE)
#                             r.setdefault("district", dist)
#                             r.setdefault("block", blk)

#                             uid = record_uid(r)
#                             if not uid:
#                                 continue
#                             gkey = f"{dist}||{blk}||{uid}"

#                             if gkey not in global_records:
#                                 global_records[gkey] = r
#                                 changed = True
#                             else:
#                                 old = global_records[gkey]
#                                 for k, v in r.items():
#                                     if k not in old or (not old.get(k) and v):
#                                         old[k] = v
#                                         changed = True

#                         page_no += 1
#                         after = len(global_records)
#                         print(f"    page={page_no} extracted={len(page_records)} total_saved={after} (+{after-before})")

#                         # ✅ REALTIME update after every page (only if something changed)
#                         if changed:
#                             write_realtime_wide(global_records, OUT_CSV)
#                             print(f"    [WRITE] realtime CSV updated -> {OUT_CSV}")

#                         if not next_button_available(page):
#                             break
#                         click_next(page)

#                     # ✅ checkpoint at end of block (always write)
#                     write_realtime_wide(global_records, OUT_CSV)
#                     print(f"  [BLOCK DONE] CSV checkpoint written ({blk})")

#             # final write
#             write_realtime_wide(global_records, OUT_CSV)
#             print(f"\nDONE ✅ Total rows in file: {len(global_records)}")
#             print(f"Saved -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="kys_fail_realtime")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main()













# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import pandas as pd
# from pandas.errors import EmptyDataError
# import time
# from pathlib import Path

# URL = "https://kys.udiseplus.gov.in/#/advancesearch"

# STATE = "GUJARAT"
# OUT_CSV = "kys_realtime_guj_ahd_all_blocks_all_pages.csv"
# START_DISTRICT = "AHMEDABAD"   # start from here, then continue in dropdown order

# # ---------------------------
# # VIEW MODE ✅
# # ---------------------------
# HEADLESS = False        # show browser
# SLOW_MO_MS = 200        # slow actions so you can see (0 for fastest)
# BLOCK_HEAVY_RESOURCES = False  # True => faster but visuals may reduce

# # ---------------------------
# # Selectors
# # ---------------------------
# ADV_BTN_SELECTOR = ".advanceSearchBtn"
# SELECTS_SELECTOR = "select.form-select.select"
# SEARCH_BTN_SELECTOR = ".purpleBtn"
# NEXT_BTN_SELECTOR = ".nextBtn"

# # extraction rules you specified
# HEADER_SEL = ".fw-600"
# FIELD_VALUE_SEL = ".blueCol.custom-word-break"
# SCHOOL_NAME_VALUE_SEL = ".custom-word-break.mt-2.mb-1"

# # ---------------------------
# # Tuning
# # ---------------------------
# WAIT_MS = 20_000
# RESULTS_SETTLE_MS = 35_000
# SCROLL_MAX_STEPS = 90
# SCROLL_STEP_PX = 1400


# # ---------------------------
# # CSV helpers (create + resume + realtime update)
# # ---------------------------
# def ensure_csv_exists(csv_path: str):
#     p = Path(csv_path)
#     if p.exists():
#         return
#     pd.DataFrame(columns=["state", "district", "school_name"]).to_csv(
#         csv_path, index=False, encoding="utf-8-sig"
#     )
#     print(f"[INIT] Created empty CSV -> {csv_path}")


# def record_uid(rec: dict) -> str:
#     """UID for dedupe/merge across virtual-scroll + pages + reruns."""
#     if not rec:
#         return ""
#     key_hints = ["udise", "school code", "sch code", "school id", "udise code", "udise no", "udise number"]
#     for k, v in rec.items():
#         if isinstance(k, str) and any(h in k.lower() for h in key_hints):
#             vv = str(v).strip()
#             if vv:
#                 return f"ID::{vv}"

#     sn = str(rec.get("school_name", "")).strip()
#     if sn:
#         extra = ""
#         for k, v in rec.items():
#             if k == "school_name":
#                 continue
#             vv = str(v).strip()
#             if vv:
#                 extra = vv
#                 break
#         return f"SN::{sn}::{extra}"

#     return f"RAW::{hash(tuple(sorted(rec.items())))}"


# def load_existing_global_records(csv_path: str):
#     p = Path(csv_path)
#     if not p.exists():
#         return {}
#     try:
#         df = pd.read_csv(p, dtype=str, keep_default_na=False)
#     except EmptyDataError:
#         return {}
#     if df.empty:
#         return {}

#     global_records = {}
#     for i, row in df.iterrows():
#         r = row.to_dict()
#         dist = (r.get("district", "") or "").strip()
#         uid = record_uid(r) or f"ROW::{i}"
#         gkey = f"{dist}||{uid}"
#         global_records[gkey] = r

#     print(f"[LOAD] Existing rows kept from CSV: {len(global_records)}")
#     return global_records


# def write_realtime_wide(global_records_dict, out_csv=OUT_CSV):
#     """Overwrite so new columns appear immediately; keep key columns first."""
#     if not global_records_dict:
#         ensure_csv_exists(out_csv)
#         return

#     df = pd.DataFrame(list(global_records_dict.values()))

#     # keep Ahmedabad on top (optional but helpful while watching)
#     if "district" in df.columns:
#         ahd = "AHMEDABAD"
#         df["_dist_sort"] = (
#             df["district"].fillna("").astype(str).str.strip().str.upper()
#             .apply(lambda x: 0 if x == ahd else 1)
#         )
#         sort_cols = ["_dist_sort", "district"]
#         if "school_name" in df.columns:
#             sort_cols.append("school_name")
#         df = df.sort_values(sort_cols, kind="stable").drop(columns=["_dist_sort"])

#     front = [c for c in ["state", "district", "school_name"] if c in df.columns]
#     rest = [c for c in df.columns if c not in front]
#     df = df[front + rest]

#     df.to_csv(out_csv, index=False, encoding="utf-8-sig")


# # ---------------------------
# # Debug helpers
# # ---------------------------
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


# # ---------------------------
# # Playwright helpers
# # ---------------------------
# def wait_and_click_advanced(page):
#     page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(ADV_BTN_SELECTOR).first.click(force=True)


# def get_select_by_index(page, idx):
#     deadline = time.time() + WAIT_MS / 1000
#     while time.time() < deadline:
#         sels = page.locator(SELECTS_SELECTOR)
#         if sels.count() >= (idx + 1):
#             sel = sels.nth(idx)
#             if sel.is_visible():
#                 return sel
#         page.wait_for_timeout(200)
#     raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


# def pick_option_by_text(select_locator, target_text):
#     target = target_text.strip().lower()
#     options = select_locator.locator("option")
#     if options.count() == 0:
#         raise PWTimeoutError("No <option> found inside select.")

#     chosen_value = None
#     for i in range(options.count()):
#         opt = options.nth(i)
#         label = (opt.inner_text() or "").strip()
#         value = opt.get_attribute("value") or ""
#         if label.lower() == target:
#             chosen_value = value
#             break

#     if chosen_value is not None and chosen_value != "":
#         select_locator.select_option(value=chosen_value)
#     else:
#         select_locator.select_option(label=target_text)


# def extract_option_texts(select_locator, prefer_ng_star=True):
#     options = select_locator.locator("option")
#     out = []

#     if prefer_ng_star:
#         for i in range(options.count()):
#             opt = options.nth(i)
#             cls = (opt.get_attribute("class") or "")
#             if "ng-star-inserted" not in cls:
#                 continue
#             t = (opt.inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     if not out:
#         for i in range(options.count()):
#             t = (options.nth(i).inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     cleaned = []
#     for t in out:
#         low = t.strip().lower()
#         if not t.strip():
#             continue
#         if low in {"select", "choose", "all", "--select--", "select one"}:
#             continue
#         cleaned.append(t.strip())

#     # de-dup preserve order
#     seen = set()
#     uniq = []
#     for x in cleaned:
#         if x not in seen:
#             seen.add(x)
#             uniq.append(x)
#     return uniq


# def next_button_available(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     if btn.count() == 0 or not btn.is_visible():
#         return False
#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass
#     cls = (btn.get_attribute("class") or "").lower()
#     if "disabled" in cls:
#         return False
#     aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
#     if aria_disabled in {"true", "1"}:
#         return False
#     if btn.get_attribute("disabled") is not None:
#         return False
#     return True


# def wait_for_results_settled(page, timeout_ms=RESULTS_SETTLE_MS):
#     """SPA-safe: wait until DOM counts stabilize (works even if 0 results)."""
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     stable = 0
#     while time.time() < deadline:
#         stats = page.evaluate(
#             """
#             (sels) => ({
#               sn: document.querySelectorAll(sels.school).length,
#               h:  document.querySelectorAll(sels.header).length,
#               v:  document.querySelectorAll(sels.value).length,
#               t:  (document.body && document.body.innerText) ? document.body.innerText.length : 0
#             })
#             """,
#             {"school": SCHOOL_NAME_VALUE_SEL, "header": HEADER_SEL, "value": FIELD_VALUE_SEL},
#         )
#         if stats == last:
#             stable += 1
#             if stable >= 3:
#                 return
#         else:
#             stable = 0
#             last = stats
#         page.wait_for_timeout(250)


# def click_search(page):
#     page.wait_for_selector(SEARCH_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(SEARCH_BTN_SELECTOR).first.click(force=True)
#     wait_for_results_settled(page)


# def click_next(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     btn.scroll_into_view_if_needed()
#     btn.click(force=True)
#     wait_for_results_settled(page)


# # ---------------------------
# # Virtual scroll tools (so you don't miss hidden rows)
# # ---------------------------
# def scroll_to_top(page):
#     page.evaluate(
#         """
#         () => {
#           const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#           if (preferred) { preferred.scrollTop = 0; return; }

#           const candidates = Array.from(document.querySelectorAll('*'))
#             .filter(el => {
#               const st = getComputedStyle(el);
#               const oy = st.overflowY || '';
#               return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#             });

#           let best = null, bestScore = -1;
#           for (const el of candidates) {
#             const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#             if (score > bestScore) { bestScore = score; best = el; }
#           }
#           if (best) best.scrollTop = 0;
#           else window.scrollTo(0, 0);
#         }
#         """
#     )
#     page.wait_for_timeout(150)


# def scroll_step(page, step_px=SCROLL_STEP_PX):
#     return page.evaluate(
#         """
#         (stepPx) => {
#           function pickScrollable() {
#             const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#             if (preferred) return {type: 'el', el: preferred};

#             const candidates = Array.from(document.querySelectorAll('*'))
#               .filter(el => {
#                 const st = getComputedStyle(el);
#                 const oy = st.overflowY || '';
#                 return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#               });

#             let best = null, bestScore = -1;
#             for (const el of candidates) {
#               const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#               if (score > bestScore) { bestScore = score; best = el; }
#             }
#             if (best) return {type: 'el', el: best};
#             return {type: 'win', el: null};
#           }

#           const target = pickScrollable();

#           if (target.type === 'win') {
#             const before = window.scrollY;
#             const max = document.documentElement.scrollHeight - window.innerHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             window.scrollTo(0, after);
#             return {before, after, max, at_bottom: after >= max - 2};
#           } else {
#             const el = target.el;
#             const before = el.scrollTop;
#             const max = el.scrollHeight - el.clientHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             el.scrollTop = after;
#             return {before, after, max, at_bottom: after >= max - 2};
#           }
#         }
#         """,
#         step_px,
#     )


# # ---------------------------
# # Extraction (your mapping)
# # ---------------------------
# def extract_current_dom_records(page):
#     """
#     - school_name from .custom-word-break.mt-2.mb-1
#     - field key from .fw-600 (if missing => unknown_*)
#     - field value from .blueCol.custom-word-break
#     """
#     js = r"""
#     () => {
#       const HEADER_SEL = '.fw-600';
#       const VALUE_SEL = '.blueCol.custom-word-break';
#       const SCHOOL_SEL = '.custom-word-break.mt-2.mb-1';

#       const schoolEls = Array.from(document.querySelectorAll(SCHOOL_SEL));
#       const valueEls  = Array.from(document.querySelectorAll(VALUE_SEL));
#       if (schoolEls.length === 0 && valueEls.length === 0) return [];

#       function clean(s) { return (s || '').trim(); }
#       function cleanKey(s) { return clean(s).replace(/[:\s]+$/g, ''); }

#       function bestRoot(el) {
#         let cur = el;
#         for (let i=0; i<10 && cur && cur !== document.body; i++) {
#           const p = cur.parentElement;
#           if (!p) break;
#           const h = p.querySelectorAll(HEADER_SEL).length;
#           const v = p.querySelectorAll(VALUE_SEL).length;
#           const s = p.querySelectorAll(SCHOOL_SEL).length;
#           if (v >= 2 && (h >= 1 || v >= 4) && s >= 1) return p;
#           cur = p;
#         }
#         return el.parentElement || document.body;
#       }

#       const roots = new Set();
#       for (const sEl of schoolEls) roots.add(bestRoot(sEl));
#       if (roots.size === 0) roots.add(document.body);

#       function extractFromRoot(root) {
#         const obj = {};

#         const snEl = root.querySelector(SCHOOL_SEL);
#         const sn = cleanKey(snEl ? snEl.textContent : '');
#         if (sn) obj.school_name = sn;

#         const vals = Array.from(root.querySelectorAll(VALUE_SEL));
#         let unk = 0;

#         for (const vEl of vals) {
#           const row = vEl.closest('div,li,tr,td') || vEl.parentElement;
#           const val = clean(vEl.textContent);
#           if (!val) continue;

#           let key = '';
#           if (row) {
#             const hEl = row.querySelector(HEADER_SEL);
#             if (hEl) key = cleanKey(hEl.textContent || '');
#           }

#           if (!key) {
#             let prev = vEl.previousElementSibling;
#             while (prev && !prev.matches(HEADER_SEL)) prev = prev.previousElementSibling;
#             if (prev) key = cleanKey(prev.textContent || '');
#           }

#           if (!key) {
#             unk += 1;
#             key = `unknown_${unk}`;
#           }

#           if (obj[key] === undefined) obj[key] = val;
#           else {
#             let n = 2;
#             while (obj[`${key}_${n}`] !== undefined) n += 1;
#             obj[`${key}_${n}`] = val;
#           }
#         }

#         return Object.keys(obj).length ? obj : null;
#       }

#       const out = [];
#       for (const r of roots) {
#         const rec = extractFromRoot(r);
#         if (rec) out.push(rec);
#       }
#       return out;
#     }
#     """
#     return page.evaluate(js)


# def collect_full_page_records(page):
#     """Scroll through virtual list and merge everything into a full set for this page."""
#     scroll_to_top(page)
#     wait_for_results_settled(page)

#     collected = {}
#     no_new = 0

#     for _ in range(SCROLL_MAX_STEPS):
#         dom_recs = extract_current_dom_records(page)
#         new_added = 0

#         for r in dom_recs:
#             uid = record_uid(r)
#             if not uid:
#                 continue
#             if uid not in collected:
#                 collected[uid] = r
#                 new_added += 1
#             else:
#                 old = collected[uid]
#                 for k, v in r.items():
#                     if k not in old or (not old.get(k) and v):
#                         old[k] = v

#         no_new = no_new + 1 if new_added == 0 else 0
#         info = scroll_step(page, SCROLL_STEP_PX)
#         page.wait_for_timeout(180)

#         if info.get("at_bottom") and no_new >= 2:
#             break

#     return list(collected.values())


# def rotate_list_from(items, start_item):
#     if not start_item:
#         return items
#     up = [x.strip().upper() for x in items]
#     s = start_item.strip().upper()
#     if s not in up:
#         return items
#     idx = up.index(s)
#     return items[idx:] + items[:idx]


# # ---------------------------
# # Main
# # ---------------------------
# def main():
#     ensure_csv_exists(OUT_CSV)
#     global_records = load_existing_global_records(OUT_CSV)
#     write_realtime_wide(global_records, OUT_CSV)

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=HEADLESS,
#             slow_mo=SLOW_MO_MS,
#             args=["--no-sandbox"],
#         )
#         context = browser.new_context(
#             viewport={"width": 1366, "height": 768},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )

#         if BLOCK_HEAVY_RESOURCES:
#             def route_handler(route, request):
#                 if request.resource_type in {"image", "font", "media"}:
#                     return route.abort()
#                 return route.continue_()
#             context.route("**/*", route_handler)

#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             wait_and_click_advanced(page)

#             # ✅ ONLY state + district (no block)
#             state_sel = get_select_by_index(page, 0)
#             pick_option_by_text(state_sel, STATE)
#             page.wait_for_timeout(600)

#             district_sel = get_select_by_index(page, 1)
#             districts = extract_option_texts(district_sel, prefer_ng_star=True)
#             if not districts:
#                 raise RuntimeError("No districts found after selecting state.")

#             districts = rotate_list_from(districts, START_DISTRICT)
#             print(f"Districts total={len(districts)} | starting from {START_DISTRICT}")

#             for di, dist in enumerate(districts, start=1):
#                 print(f"\n[DISTRICT {di}/{len(districts)}] {dist}")

#                 # select district
#                 district_sel = get_select_by_index(page, 1)
#                 district_sel.scroll_into_view_if_needed()
#                 pick_option_by_text(district_sel, dist)
#                 page.wait_for_timeout(500)

#                 click_search(page)

#                 page_no = 0
#                 while True:
#                     before = len(global_records)
#                     page_records = collect_full_page_records(page)

#                     changed = False
#                     for r in page_records:
#                         r.setdefault("state", STATE)
#                         r.setdefault("district", dist)

#                         uid = record_uid(r)
#                         if not uid:
#                             continue
#                         gkey = f"{dist}||{uid}"

#                         if gkey not in global_records:
#                             global_records[gkey] = r
#                             changed = True
#                         else:
#                             old = global_records[gkey]
#                             for k, v in r.items():
#                                 if k not in old or (not old.get(k) and v):
#                                     old[k] = v
#                                     changed = True

#                     page_no += 1
#                     after = len(global_records)
#                     print(f"  page={page_no} extracted={len(page_records)} total_saved={after} (+{after-before})")

#                     # realtime update after each page
#                     if changed:
#                         write_realtime_wide(global_records, OUT_CSV)
#                         print(f"  [WRITE] realtime CSV updated -> {OUT_CSV}")

#                     # stop if no next page
#                     if not next_button_available(page):
#                         # also stop if this page had zero records (nothing left)
#                         break

#                     click_next(page)

#                 write_realtime_wide(global_records, OUT_CSV)
#                 print(f"[DISTRICT DONE] {dist} checkpoint saved")

#             write_realtime_wide(global_records, OUT_CSV)
#             print(f"\nDONE ✅ Total rows in file: {len(global_records)}")
#             print(f"Saved -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="kys_fail_state_district_only")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main()





# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
# import pandas as pd
# from pandas.errors import EmptyDataError
# import time
# from pathlib import Path

# URL = "https://kys.udiseplus.gov.in/#/advancesearch"

# STATE = "GUJARAT"
# OUT_CSV = "kys_realtime_guj_ahd_all_blocks_all_pages.csv"
# START_DISTRICT = "AHMEDABAD"  # start here, then continue in dropdown order

# # ---------------------------
# # VIEW MODE ✅
# # ---------------------------
# HEADLESS = False        # show browser
# SLOW_MO_MS = 150        # slow actions so you can see (0 = fastest)
# BLOCK_HEAVY_RESOURCES = False  # True => faster but visuals may reduce

# # ---------------------------
# # Selectors
# # ---------------------------
# ADV_BTN_SELECTOR = ".advanceSearchBtn"
# SELECTS_SELECTOR = "select.form-select.select"
# SEARCH_BTN_SELECTOR = ".purpleBtn"
# NEXT_BTN_SELECTOR = ".nextBtn"

# # extraction rules
# HEADER_SEL = ".fw-600"
# FIELD_VALUE_SEL = ".blueCol.custom-word-break"
# SCHOOL_NAME_VALUE_SEL = ".custom-word-break.mt-2.mb-1"

# # ---------------------------
# # Tuning
# # ---------------------------
# WAIT_MS = 25_000
# RESULTS_SETTLE_MS = 45_000

# SCROLL_MAX_STEPS = 95
# SCROLL_STEP_PX = 1400

# # pagination safety
# ZERO_PAGE_RETRY_WAIT_MS = 8000       # if extracted=0, wait and retry once
# MAX_NEXT_NOCHANGE_RETRIES = 2        # if Next doesn't change signature, stop
# MAX_ZERO_PAGES_IN_A_ROW = 2          # 0 extracted twice => stop district


# # ---------------------------
# # CSV helpers (create + resume + realtime update)
# # ---------------------------
# def ensure_csv_exists(csv_path: str):
#     p = Path(csv_path)
#     if p.exists():
#         return
#     pd.DataFrame(columns=["state", "district", "school_name"]).to_csv(
#         csv_path, index=False, encoding="utf-8-sig"
#     )
#     print(f"[INIT] Created empty CSV -> {csv_path}")


# def record_uid(rec: dict) -> str:
#     """UID for dedupe/merge across virtual-scroll + pages + reruns."""
#     if not rec:
#         return ""
#     key_hints = ["udise", "school code", "sch code", "school id", "udise code", "udise no", "udise number"]
#     for k, v in rec.items():
#         if isinstance(k, str) and any(h in k.lower() for h in key_hints):
#             vv = str(v).strip()
#             if vv:
#                 return f"ID::{vv}"

#     sn = str(rec.get("school_name", "")).strip()
#     if sn:
#         extra = ""
#         for k, v in rec.items():
#             if k == "school_name":
#                 continue
#             vv = str(v).strip()
#             if vv:
#                 extra = vv
#                 break
#         return f"SN::{sn}::{extra}"

#     return f"RAW::{hash(tuple(sorted(rec.items())))}"


# def load_existing_global_records(csv_path: str):
#     p = Path(csv_path)
#     if not p.exists():
#         return {}
#     try:
#         df = pd.read_csv(p, dtype=str, keep_default_na=False)
#     except EmptyDataError:
#         return {}
#     if df.empty:
#         return {}

#     global_records = {}
#     for i, row in df.iterrows():
#         r = row.to_dict()
#         dist = (r.get("district", "") or "").strip()
#         uid = record_uid(r) or f"ROW::{i}"
#         gkey = f"{dist}||{uid}"
#         global_records[gkey] = r

#     print(f"[LOAD] Existing rows kept from CSV: {len(global_records)}")
#     return global_records


# def write_realtime_wide(global_records_dict, out_csv=OUT_CSV):
#     """Overwrite so new columns appear immediately; keep key columns first."""
#     if not global_records_dict:
#         ensure_csv_exists(out_csv)
#         return

#     df = pd.DataFrame(list(global_records_dict.values()))

#     # keep Ahmedabad on top (optional)
#     if "district" in df.columns:
#         ahd = "AHMEDABAD"
#         df["_dist_sort"] = (
#             df["district"].fillna("").astype(str).str.strip().str.upper()
#             .apply(lambda x: 0 if x == ahd else 1)
#         )
#         sort_cols = ["_dist_sort", "district"]
#         if "school_name" in df.columns:
#             sort_cols.append("school_name")
#         df = df.sort_values(sort_cols, kind="stable").drop(columns=["_dist_sort"])

#     front = [c for c in ["state", "district", "school_name"] if c in df.columns]
#     rest = [c for c in df.columns if c not in front]
#     df = df[front + rest]

#     df.to_csv(out_csv, index=False, encoding="utf-8-sig")


# # ---------------------------
# # Debug helpers
# # ---------------------------
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


# # ---------------------------
# # Playwright helpers
# # ---------------------------
# def wait_and_click_advanced(page):
#     page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(ADV_BTN_SELECTOR).first.click(force=True)


# def get_select_by_index(page, idx):
#     deadline = time.time() + WAIT_MS / 1000
#     while time.time() < deadline:
#         sels = page.locator(SELECTS_SELECTOR)
#         if sels.count() >= (idx + 1):
#             sel = sels.nth(idx)
#             if sel.is_visible():
#                 return sel
#         page.wait_for_timeout(200)
#     raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


# def pick_option_by_text(select_locator, target_text):
#     target = target_text.strip().lower()
#     options = select_locator.locator("option")
#     if options.count() == 0:
#         raise PWTimeoutError("No <option> found inside select.")

#     chosen_value = None
#     for i in range(options.count()):
#         opt = options.nth(i)
#         label = (opt.inner_text() or "").strip()
#         value = opt.get_attribute("value") or ""
#         if label.lower() == target:
#             chosen_value = value
#             break

#     if chosen_value is not None and chosen_value != "":
#         select_locator.select_option(value=chosen_value)
#     else:
#         select_locator.select_option(label=target_text)


# def get_selected_option_text(select_locator) -> str:
#     try:
#         return select_locator.evaluate(
#             """(sel) => {
#                 const opt = sel.options[sel.selectedIndex];
#                 return opt ? (opt.textContent || '').trim() : '';
#             }"""
#         )
#     except Exception:
#         return ""


# def extract_option_texts(select_locator, prefer_ng_star=True):
#     options = select_locator.locator("option")
#     out = []

#     if prefer_ng_star:
#         for i in range(options.count()):
#             opt = options.nth(i)
#             cls = (opt.get_attribute("class") or "")
#             if "ng-star-inserted" not in cls:
#                 continue
#             t = (opt.inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     if not out:
#         for i in range(options.count()):
#             t = (options.nth(i).inner_text() or "").strip()
#             if t:
#                 out.append(t)

#     cleaned = []
#     for t in out:
#         low = t.strip().lower()
#         if not t.strip():
#             continue
#         if low in {"select", "choose", "all", "--select--", "select one"}:
#             continue
#         cleaned.append(t.strip())

#     seen = set()
#     uniq = []
#     for x in cleaned:
#         if x not in seen:
#             seen.add(x)
#             uniq.append(x)
#     return uniq


# def next_button_available(page):
#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     if btn.count() == 0 or not btn.is_visible():
#         return False
#     try:
#         if not btn.is_enabled():
#             return False
#     except Exception:
#         pass
#     cls = (btn.get_attribute("class") or "").lower()
#     if "disabled" in cls:
#         return False
#     aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
#     if aria_disabled in {"true", "1"}:
#         return False
#     if btn.get_attribute("disabled") is not None:
#         return False
#     return True


# def wait_for_results_settled(page, timeout_ms=RESULTS_SETTLE_MS):
#     """SPA-safe: wait until DOM counts stabilize (works even if 0 results)."""
#     deadline = time.time() + timeout_ms / 1000
#     last = None
#     stable = 0
#     while time.time() < deadline:
#         stats = page.evaluate(
#             """
#             (sels) => ({
#               sn: document.querySelectorAll(sels.school).length,
#               h:  document.querySelectorAll(sels.header).length,
#               v:  document.querySelectorAll(sels.value).length,
#               t:  (document.body && document.body.innerText) ? document.body.innerText.length : 0
#             })
#             """,
#             {"school": SCHOOL_NAME_VALUE_SEL, "header": HEADER_SEL, "value": FIELD_VALUE_SEL},
#         )
#         if stats == last:
#             stable += 1
#             if stable >= 3:
#                 return
#         else:
#             stable = 0
#             last = stats
#         page.wait_for_timeout(250)


# def click_search(page):
#     page.wait_for_selector(SEARCH_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
#     page.locator(SEARCH_BTN_SELECTOR).first.click(force=True)
#     wait_for_results_settled(page)


# def page_signature(page):
#     """Small signature to detect page change on Next."""
#     return page.evaluate(
#         """
#         () => {
#           const els = Array.from(document.querySelectorAll('.custom-word-break.mt-2.mb-1'));
#           const first = els.slice(0, 4).map(e => (e.textContent || '').trim()).filter(Boolean);
#           const count = els.length;
#           return {count, first};
#         }
#         """
#     )


# def click_next_safe(page):
#     """Click next, then wait for signature to change. Return True if changed, else False."""
#     before = page_signature(page)

#     btn = page.locator(NEXT_BTN_SELECTOR).first
#     btn.scroll_into_view_if_needed()
#     btn.click(force=True)

#     # Wait for change (or settle)
#     deadline = time.time() + (RESULTS_SETTLE_MS / 1000)
#     while time.time() < deadline:
#         wait_for_results_settled(page, timeout_ms=10_000)
#         after = page_signature(page)
#         if after != before:
#             return True
#         page.wait_for_timeout(300)

#     return False


# # ---------------------------
# # Virtual scroll tools (so you don't miss hidden rows)
# # ---------------------------
# def scroll_to_top(page):
#     page.evaluate(
#         """
#         () => {
#           const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#           if (preferred) { preferred.scrollTop = 0; return; }

#           const candidates = Array.from(document.querySelectorAll('*'))
#             .filter(el => {
#               const st = getComputedStyle(el);
#               const oy = st.overflowY || '';
#               return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#             });

#           let best = null, bestScore = -1;
#           for (const el of candidates) {
#             const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#             if (score > bestScore) { bestScore = score; best = el; }
#           }
#           if (best) best.scrollTop = 0;
#           else window.scrollTo(0, 0);
#         }
#         """
#     )
#     page.wait_for_timeout(150)


# def scroll_step(page, step_px=SCROLL_STEP_PX):
#     return page.evaluate(
#         """
#         (stepPx) => {
#           function pickScrollable() {
#             const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
#             if (preferred) return {type: 'el', el: preferred};

#             const candidates = Array.from(document.querySelectorAll('*'))
#               .filter(el => {
#                 const st = getComputedStyle(el);
#                 const oy = st.overflowY || '';
#                 return (oy.includes('auto') || oy.includes('scroll')) && (el.scrollHeight - el.clientHeight > 200);
#               });

#             let best = null, bestScore = -1;
#             for (const el of candidates) {
#               const score = el.querySelectorAll('.custom-word-break.mt-2.mb-1').length;
#               if (score > bestScore) { bestScore = score; best = el; }
#             }
#             if (best) return {type: 'el', el: best};
#             return {type: 'win', el: null};
#           }

#           const target = pickScrollable();

#           if (target.type === 'win') {
#             const before = window.scrollY;
#             const max = document.documentElement.scrollHeight - window.innerHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             window.scrollTo(0, after);
#             return {before, after, max, at_bottom: after >= max - 2};
#           } else {
#             const el = target.el;
#             const before = el.scrollTop;
#             const max = el.scrollHeight - el.clientHeight;
#             const after = Math.min(before + stepPx, Math.max(0, max));
#             el.scrollTop = after;
#             return {before, after, max, at_bottom: after >= max - 2};
#           }
#         }
#         """,
#         step_px,
#     )


# # ---------------------------
# # Extraction (your mapping)
# # ---------------------------
# def extract_current_dom_records(page):
#     js = r"""
#     () => {
#       const HEADER_SEL = '.fw-600';
#       const VALUE_SEL = '.blueCol.custom-word-break';
#       const SCHOOL_SEL = '.custom-word-break.mt-2.mb-1';

#       const schoolEls = Array.from(document.querySelectorAll(SCHOOL_SEL));
#       const valueEls  = Array.from(document.querySelectorAll(VALUE_SEL));
#       if (schoolEls.length === 0 && valueEls.length === 0) return [];

#       function clean(s) { return (s || '').trim(); }
#       function cleanKey(s) { return clean(s).replace(/[:\s]+$/g, ''); }

#       function bestRoot(el) {
#         let cur = el;
#         for (let i=0; i<10 && cur && cur !== document.body; i++) {
#           const p = cur.parentElement;
#           if (!p) break;
#           const h = p.querySelectorAll(HEADER_SEL).length;
#           const v = p.querySelectorAll(VALUE_SEL).length;
#           const s = p.querySelectorAll(SCHOOL_SEL).length;
#           if (v >= 2 && (h >= 1 || v >= 4) && s >= 1) return p;
#           cur = p;
#         }
#         return el.parentElement || document.body;
#       }

#       const roots = new Set();
#       for (const sEl of schoolEls) roots.add(bestRoot(sEl));
#       if (roots.size === 0) roots.add(document.body);

#       function extractFromRoot(root) {
#         const obj = {};

#         const snEl = root.querySelector(SCHOOL_SEL);
#         const sn = cleanKey(snEl ? snEl.textContent : '');
#         if (sn) obj.school_name = sn;

#         const vals = Array.from(root.querySelectorAll(VALUE_SEL));
#         let unk = 0;

#         for (const vEl of vals) {
#           const row = vEl.closest('div,li,tr,td') || vEl.parentElement;
#           const val = clean(vEl.textContent);
#           if (!val) continue;

#           let key = '';
#           if (row) {
#             const hEl = row.querySelector(HEADER_SEL);
#             if (hEl) key = cleanKey(hEl.textContent || '');
#           }

#           if (!key) {
#             let prev = vEl.previousElementSibling;
#             while (prev && !prev.matches(HEADER_SEL)) prev = prev.previousElementSibling;
#             if (prev) key = cleanKey(prev.textContent || '');
#           }

#           if (!key) {
#             unk += 1;
#             key = `unknown_${unk}`;
#           }

#           if (obj[key] === undefined) obj[key] = val;
#           else {
#             let n = 2;
#             while (obj[`${key}_${n}`] !== undefined) n += 1;
#             obj[`${key}_${n}`] = val;
#           }
#         }

#         return Object.keys(obj).length ? obj : null;
#       }

#       const out = [];
#       for (const r of roots) {
#         const rec = extractFromRoot(r);
#         if (rec) out.push(rec);
#       }
#       return out;
#     }
#     """
#     return page.evaluate(js)


# def collect_full_page_records(page):
#     """Scroll through virtual list and merge everything into a full set for this page."""
#     scroll_to_top(page)
#     wait_for_results_settled(page)

#     collected = {}
#     no_new = 0

#     for _ in range(SCROLL_MAX_STEPS):
#         dom_recs = extract_current_dom_records(page)
#         new_added = 0

#         for r in dom_recs:
#             uid = record_uid(r)
#             if not uid:
#                 continue
#             if uid not in collected:
#                 collected[uid] = r
#                 new_added += 1
#             else:
#                 old = collected[uid]
#                 for k, v in r.items():
#                     if k not in old or (not old.get(k) and v):
#                         old[k] = v

#         no_new = no_new + 1 if new_added == 0 else 0
#         info = scroll_step(page, SCROLL_STEP_PX)
#         page.wait_for_timeout(180)

#         if info.get("at_bottom") and no_new >= 2:
#             break

#     return list(collected.values())


# def rotate_list_from(items, start_item):
#     if not start_item:
#         return items
#     up = [x.strip().upper() for x in items]
#     s = start_item.strip().upper()
#     if s not in up:
#         return items
#     idx = up.index(s)
#     return items[idx:] + items[:idx]


# # ---------------------------
# # Main
# # ---------------------------
# def main():
#     ensure_csv_exists(OUT_CSV)
#     global_records = load_existing_global_records(OUT_CSV)
#     write_realtime_wide(global_records, OUT_CSV)

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=HEADLESS,
#             slow_mo=SLOW_MO_MS,
#             args=["--no-sandbox"],
#         )
#         context = browser.new_context(
#             viewport={"width": 1366, "height": 768},
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#         )

#         if BLOCK_HEAVY_RESOURCES:
#             def route_handler(route, request):
#                 if request.resource_type in {"image", "font", "media"}:
#                     return route.abort()
#                 return route.continue_()
#             context.route("**/*", route_handler)

#         page = context.new_page()
#         page.set_default_timeout(WAIT_MS)

#         try:
#             page.goto(URL, wait_until="domcontentloaded")
#             wait_and_click_advanced(page)

#             # ONLY state + district
#             state_sel = get_select_by_index(page, 0)
#             pick_option_by_text(state_sel, STATE)
#             page.wait_for_timeout(600)

#             district_sel = get_select_by_index(page, 1)
#             districts = extract_option_texts(district_sel, prefer_ng_star=True)
#             if not districts:
#                 raise RuntimeError("No districts found after selecting state.")

#             districts = rotate_list_from(districts, START_DISTRICT)
#             print(f"Districts total={len(districts)} | starting from {START_DISTRICT}")

#             for di, dist in enumerate(districts, start=1):
#                 print(f"\n[DISTRICT {di}/{len(districts)}] {dist}")

#                 # Force UI to top so dropdown is reachable after long paging
#                 page.evaluate("window.scrollTo(0,0)")
#                 page.wait_for_timeout(200)

#                 # Select district with verification + retry
#                 for attempt in range(3):
#                     district_sel = get_select_by_index(page, 1)
#                     district_sel.scroll_into_view_if_needed()
#                     pick_option_by_text(district_sel, dist)
#                     page.wait_for_timeout(500)

#                     selected = get_selected_option_text(district_sel).strip().upper()
#                     if selected == dist.strip().upper():
#                         break
#                     if attempt == 2:
#                         raise RuntimeError(f"District not selecting properly. Wanted={dist}, got={selected}")

#                 click_search(page)

#                 page_no = 0
#                 zero_pages_in_a_row = 0

#                 while True:
#                     page_no += 1

#                     # collect
#                     page_records = collect_full_page_records(page)

#                     # if 0, retry once with extra wait (avoids false 0 due to slow render)
#                     if len(page_records) == 0:
#                         page.wait_for_timeout(ZERO_PAGE_RETRY_WAIT_MS)
#                         page_records = collect_full_page_records(page)

#                     if len(page_records) == 0:
#                         zero_pages_in_a_row += 1
#                     else:
#                         zero_pages_in_a_row = 0

#                     before = len(global_records)

#                     changed = False
#                     for r in page_records:
#                         r.setdefault("state", STATE)
#                         r.setdefault("district", dist)

#                         uid = record_uid(r)
#                         if not uid:
#                             continue
#                         gkey = f"{dist}||{uid}"

#                         if gkey not in global_records:
#                             global_records[gkey] = r
#                             changed = True
#                         else:
#                             old = global_records[gkey]
#                             for k, v in r.items():
#                                 if k not in old or (not old.get(k) and v):
#                                     old[k] = v
#                                     changed = True

#                     after = len(global_records)
#                     print(f"  page={page_no} extracted={len(page_records)} total_saved={after} (+{after-before})")

#                     if changed:
#                         write_realtime_wide(global_records, OUT_CSV)
#                         print(f"  [WRITE] realtime CSV updated -> {OUT_CSV}")

#                     # ✅ STOP conditions to prevent getting stuck (your exact issue)
#                     if zero_pages_in_a_row >= MAX_ZERO_PAGES_IN_A_ROW:
#                         print("  [STOP] extracted=0 twice -> assuming no more pages -> moving to next district")
#                         break

#                     if not next_button_available(page):
#                         break

#                     # Click next safely; if it doesn't actually change, stop and move on
#                     moved = False
#                     for _ in range(MAX_NEXT_NOCHANGE_RETRIES):
#                         if not next_button_available(page):
#                             break
#                         if click_next_safe(page):
#                             moved = True
#                             break
#                         page.wait_for_timeout(600)

#                     if not moved:
#                         print("  [STOP] Next did not change page -> moving to next district")
#                         break

#                 # District checkpoint
#                 write_realtime_wide(global_records, OUT_CSV)
#                 print(f"[DISTRICT DONE] {dist} checkpoint saved")

#             write_realtime_wide(global_records, OUT_CSV)
#             print(f"\nDONE ✅ Total rows in file: {len(global_records)}")
#             print(f"Saved -> {OUT_CSV}")

#         except Exception as e:
#             print(f"[ERROR] {type(e).__name__}: {e}")
#             dump_debug(page, prefix="kys_fail_next_district")
#             raise
#         finally:
#             context.close()
#             browser.close()


# if __name__ == "__main__":
#     main()





from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import csv
import os
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple
import hashlib

URL = "https://kys.udiseplus.gov.in/#/advancesearch"

STATE = "GUJARAT"
OUT_CSV = "kys_realtime_guj_ahd_all_blocks_all_pages.csv"
START_DISTRICT = "AHMEDABAD"  # fallback start if no checkpoint

# ---------------------------
# VIEW MODE ✅
# ---------------------------
HEADLESS = False
SLOW_MO_MS = 150
BLOCK_HEAVY_RESOURCES = False

# ---------------------------
# Selectors
# ---------------------------
ADV_BTN_SELECTOR = ".advanceSearchBtn"
SELECTS_SELECTOR = "select.form-select.select"
SEARCH_BTN_SELECTOR = ".purpleBtn"
NEXT_BTN_SELECTOR = ".nextBtn"

# extraction rules (your mapping)
HEADER_SEL = ".fw-600"                         # header
FIELD_VALUE_SEL = ".blueCol.custom-word-break" # value
SCHOOL_NAME_VALUE_SEL = ".custom-word-break.mt-2.mb-1"  # school_name

# ---------------------------
# Tuning
# ---------------------------
WAIT_MS = 25_000
RESULTS_SETTLE_MS = 45_000

SCROLL_MAX_STEPS = 95
SCROLL_STEP_PX = 1400

ZERO_PAGE_RETRY_WAIT_MS = 8000
MAX_NEXT_NOCHANGE_RETRIES = 2
MAX_ZERO_PAGES_IN_A_ROW = 2

# ---------------------------
# Crash-safe persistence
# ---------------------------
CHECKPOINT_FILE = "kys_checkpoint.txt"
SEEN_FILE = OUT_CSV + ".seen"
COMPLETED_FILE = "kys_completed_districts.txt"

BASE_COLUMNS = ["state", "district", "school_name"]  # always first


# ---------------------------
# Low-level safe write helpers
# ---------------------------
def _fsync_file(f):
    f.flush()
    os.fsync(f.fileno())


def ensure_csv_exists(csv_path: str):
    p = Path(csv_path)
    if p.exists() and p.stat().st_size > 0:
        return
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(BASE_COLUMNS)
        _fsync_file(f)
    print(f"[INIT] Created CSV -> {csv_path}")


def read_csv_header(csv_path: str) -> List[str]:
    p = Path(csv_path)
    if not p.exists() or p.stat().st_size == 0:
        return BASE_COLUMNS[:]
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        header = next(r, [])
    header = [h.strip() for h in header if h is not None]
    if not header:
        return BASE_COLUMNS[:]
    return header


def atomic_rewrite_csv_with_new_header(csv_path: str, new_header: List[str]):
    """
    Rewrite whole CSV with expanded header (atomic rename => prevents corruption on crash).
    Uses streaming copy (no giant memory).
    """
    src = Path(csv_path)
    tmp = src.with_suffix(".tmp")

    with open(src, "r", encoding="utf-8-sig", newline="") as fin, \
         open(tmp, "w", encoding="utf-8-sig", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=new_header, extrasaction="ignore")
        writer.writeheader()

        for row in reader:
            # ensure all header keys exist (missing => blank)
            out_row = {k: (row.get(k, "") if row.get(k, "") is not None else "") for k in new_header}
            writer.writerow(out_row)

        _fsync_file(fout)

    os.replace(str(tmp), str(src))
    # fsync directory for extra safety
    try:
        dir_fd = os.open(str(src.parent), os.O_DIRECTORY)
        os.fsync(dir_fd)
        os.close(dir_fd)
    except Exception:
        pass


def ensure_header_has_keys(csv_path: str, header: List[str], rows: List[Dict]) -> List[str]:
    needed = set()
    for r in rows:
        needed.update(r.keys())

    # keep order: BASE first, then existing, then new keys sorted for stability
    cur = list(header)
    missing = [k for k in sorted(needed) if k not in cur]
    if not missing:
        return cur

    # ensure BASE columns are first
    base = [c for c in BASE_COLUMNS if c in cur]
    rest = [c for c in cur if c not in base]
    new_header = base + rest + missing

    atomic_rewrite_csv_with_new_header(csv_path, new_header)
    print(f"[SCHEMA] Expanded columns by {len(missing)} -> total_cols={len(new_header)}")
    return new_header


def append_rows_wide(csv_path: str, header: List[str], rows: List[Dict]):
    if not rows:
        return
    with open(csv_path, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        for r in rows:
            out = {k: (r.get(k, "") if r.get(k, "") is not None else "") for k in header}
            w.writerow(out)
        _fsync_file(f)


def write_checkpoint(dist_u: str, page_no: int):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(f"{dist_u}\t{page_no}\t{int(time.time())}\n")
        _fsync_file(f)


def read_checkpoint() -> Tuple[str, int]:
    p = Path(CHECKPOINT_FILE)
    if not p.exists() or p.stat().st_size == 0:
        return ("", 0)
    try:
        parts = p.read_text(encoding="utf-8").strip().split("\t")
        dist_u = (parts[0] or "").strip().upper()
        page_no = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return (dist_u, page_no)
    except Exception:
        return ("", 0)


def load_completed_districts() -> Set[str]:
    p = Path(COMPLETED_FILE)
    if not p.exists():
        return set()
    out = set()
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        d = line.strip().upper()
        if d:
            out.add(d)
    return out


def mark_district_completed(dist_u: str):
    with open(COMPLETED_FILE, "a", encoding="utf-8") as f:
        f.write(dist_u + "\n")
        _fsync_file(f)


def stable_hash64(s: str) -> int:
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "big")


def load_seen() -> Set[int]:
    p = Path(SEEN_FILE)
    if not p.exists() or p.stat().st_size == 0:
        return set()
    out = set()
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.add(int(line))
            except Exception:
                pass
    return out


def append_seen(hashes: List[int]):
    if not hashes:
        return
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        for h in hashes:
            f.write(str(h) + "\n")
        _fsync_file(f)


# ---------------------------
# Debug helpers
# ---------------------------
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


# ---------------------------
# Playwright helpers
# ---------------------------
def wait_and_click_advanced(page):
    page.wait_for_selector(ADV_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
    page.locator(ADV_BTN_SELECTOR).first.click(force=True)


def get_select_by_index(page, idx):
    deadline = time.time() + WAIT_MS / 1000
    while time.time() < deadline:
        sels = page.locator(SELECTS_SELECTOR)
        if sels.count() >= (idx + 1):
            sel = sels.nth(idx)
            if sel.is_visible():
                return sel
        page.wait_for_timeout(200)
    raise PWTimeoutError(f"Could not find select index={idx} using selector {SELECTS_SELECTOR}")


def pick_option_by_text(select_locator, target_text):
    target = target_text.strip().lower()
    options = select_locator.locator("option")
    if options.count() == 0:
        raise PWTimeoutError("No <option> found inside select.")

    chosen_value = None
    for i in range(options.count()):
        opt = options.nth(i)
        label = (opt.inner_text() or "").strip()
        value = opt.get_attribute("value") or ""
        if label.lower() == target:
            chosen_value = value
            break

    if chosen_value is not None and chosen_value != "":
        select_locator.select_option(value=chosen_value)
    else:
        select_locator.select_option(label=target_text)


def get_selected_option_text(select_locator) -> str:
    try:
        return select_locator.evaluate(
            """(sel) => {
                const opt = sel.options[sel.selectedIndex];
                return opt ? (opt.textContent || '').trim() : '';
            }"""
        )
    except Exception:
        return ""


def extract_option_texts(select_locator, prefer_ng_star=True):
    options = select_locator.locator("option")
    out = []

    if prefer_ng_star:
        for i in range(options.count()):
            opt = options.nth(i)
            cls = (opt.get_attribute("class") or "")
            if "ng-star-inserted" not in cls:
                continue
            t = (opt.inner_text() or "").strip()
            if t:
                out.append(t)

    if not out:
        for i in range(options.count()):
            t = (options.nth(i).inner_text() or "").strip()
            if t:
                out.append(t)

    cleaned = []
    for t in out:
        low = t.strip().lower()
        if not t.strip():
            continue
        if low in {"select", "choose", "all", "--select--", "select one"}:
            continue
        cleaned.append(t.strip())

    seen = set()
    uniq = []
    for x in cleaned:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def next_button_available(page):
    btn = page.locator(NEXT_BTN_SELECTOR).first
    if btn.count() == 0 or not btn.is_visible():
        return False
    try:
        if not btn.is_enabled():
            return False
    except Exception:
        pass
    cls = (btn.get_attribute("class") or "").lower()
    if "disabled" in cls:
        return False
    aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
    if aria_disabled in {"true", "1"}:
        return False
    if btn.get_attribute("disabled") is not None:
        return False
    return True


def wait_for_results_settled(page, timeout_ms=RESULTS_SETTLE_MS):
    deadline = time.time() + timeout_ms / 1000
    last = None
    stable = 0
    while time.time() < deadline:
        stats = page.evaluate(
            """
            (sels) => ({
              sn: document.querySelectorAll(sels.school).length,
              h:  document.querySelectorAll(sels.header).length,
              v:  document.querySelectorAll(sels.value).length,
              t:  (document.body && document.body.innerText) ? document.body.innerText.length : 0
            })
            """,
            {"school": SCHOOL_NAME_VALUE_SEL, "header": HEADER_SEL, "value": FIELD_VALUE_SEL},
        )
        if stats == last:
            stable += 1
            if stable >= 3:
                return
        else:
            stable = 0
            last = stats
        page.wait_for_timeout(250)


def click_search(page):
    page.wait_for_selector(SEARCH_BTN_SELECTOR, state="visible", timeout=WAIT_MS)
    page.locator(SEARCH_BTN_SELECTOR).first.click(force=True)
    wait_for_results_settled(page)


def page_signature(page):
    return page.evaluate(
        """
        () => {
          const els = Array.from(document.querySelectorAll('.custom-word-break.mt-2.mb-1'));
          const first = els.slice(0, 4).map(e => (e.textContent || '').trim()).filter(Boolean);
          const count = els.length;
          return {count, first};
        }
        """
    )


def click_next_safe(page):
    before = page_signature(page)
    btn = page.locator(NEXT_BTN_SELECTOR).first
    btn.scroll_into_view_if_needed()
    btn.click(force=True)

    deadline = time.time() + (RESULTS_SETTLE_MS / 1000)
    while time.time() < deadline:
        wait_for_results_settled(page, timeout_ms=10_000)
        after = page_signature(page)
        if after != before:
            return True
        page.wait_for_timeout(300)
    return False


# ---------------------------
# Virtual scroll tools
# ---------------------------
def scroll_to_top(page):
    page.evaluate(
        """
        () => {
          const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
          if (preferred) { preferred.scrollTop = 0; return; }
          window.scrollTo(0, 0);
        }
        """
    )
    page.wait_for_timeout(150)


def scroll_step(page, step_px=SCROLL_STEP_PX):
    return page.evaluate(
        """
        (stepPx) => {
          const preferred = document.querySelector('cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport');
          if (preferred) {
            const before = preferred.scrollTop;
            const max = preferred.scrollHeight - preferred.clientHeight;
            const after = Math.min(before + stepPx, Math.max(0, max));
            preferred.scrollTop = after;
            return {before, after, max, at_bottom: after >= max - 2};
          }
          const before = window.scrollY;
          const max = document.documentElement.scrollHeight - window.innerHeight;
          const after = Math.min(before + stepPx, Math.max(0, max));
          window.scrollTo(0, after);
          return {before, after, max, at_bottom: after >= max - 2};
        }
        """,
        step_px,
    )


# ---------------------------
# Extraction updated to EXACT mapping:
#   fw-600 -> header
#   blueCol custom-word-break -> value under that header
#   custom-word-break mt-2 mb-1 -> school_name
# ---------------------------
def extract_current_dom_records(page):
    js = r"""
    () => {
      const HEADER_SEL = '.fw-600';
      const VALUE_SEL  = '.blueCol.custom-word-break';
      const SCHOOL_SEL = '.custom-word-break.mt-2.mb-1';

      function clean(s) { return (s || '').trim(); }
      function cleanKey(s) { return clean(s).replace(/[:\s]+$/g, ''); }

      const schoolEls = Array.from(document.querySelectorAll(SCHOOL_SEL));
      const valueEls  = Array.from(document.querySelectorAll(VALUE_SEL));
      if (schoolEls.length === 0 && valueEls.length === 0) return [];

      // Choose a card/root container for a given element
      function bestRoot(el) {
        let cur = el;
        for (let i=0; i<12 && cur && cur !== document.body; i++) {
          const p = cur.parentElement;
          if (!p) break;
          const s = p.querySelectorAll(SCHOOL_SEL).length;
          const v = p.querySelectorAll(VALUE_SEL).length;
          if (s >= 1 && v >= 2) return p;
          cur = p;
        }
        return el.parentElement || document.body;
      }

      const roots = new Set();
      for (const sEl of schoolEls) roots.add(bestRoot(sEl));
      if (roots.size === 0) roots.add(document.body);

      // Find nearest header for a value element (robust: same row/closest y-distance)
      function headerForValue(vEl, root) {
        // try a few ancestor levels and choose the header closest by screen position
        const vRect = vEl.getBoundingClientRect();
        let bestText = '';
        let bestDist = 1e18;

        function consider(container) {
          const hs = Array.from(container.querySelectorAll(HEADER_SEL));
          for (const h of hs) {
            const t = cleanKey(h.textContent || '');
            if (!t) continue;
            const hRect = h.getBoundingClientRect();
            const dist = Math.abs(hRect.top - vRect.top) + Math.abs(hRect.left - vRect.left) * 0.02;
            if (dist < bestDist) {
              bestDist = dist;
              bestText = t;
            }
          }
        }

        // 1) same row-ish container
        let cur = vEl;
        for (let i=0; i<6 && cur && cur !== root; i++) {
          const p = cur.parentElement;
          if (!p) break;
          consider(p);
          cur = p;
        }

        // 2) fallback: consider entire root (still limited to this card)
        if (!bestText) consider(root);

        return bestText;
      }

      function extractFromRoot(root) {
        const obj = {};
        const snEl = root.querySelector(SCHOOL_SEL);
        const school_name = cleanKey(snEl ? snEl.textContent : '');
        if (!school_name) return null;
        obj.school_name = school_name;

        const vals = Array.from(root.querySelectorAll(VALUE_SEL));
        let unk = 0;

        for (const vEl of vals) {
          const val = clean(vEl.textContent);
          if (!val) continue;

          let key = headerForValue(vEl, root);
          if (!key) {
            unk += 1;
            key = `unknown_${unk}`;
          }

          // handle duplicate keys inside same card
          if (obj[key] === undefined) obj[key] = val;
          else {
            let n = 2;
            while (obj[`${key}_${n}`] !== undefined) n += 1;
            obj[`${key}_${n}`] = val;
          }
        }

        return obj;
      }

      const out = [];
      for (const r of roots) {
        const rec = extractFromRoot(r);
        if (rec) out.push(rec);
      }
      return out;
    }
    """
    return page.evaluate(js)


def record_uid(rec: Dict) -> str:
    """
    Stable-ish UID to dedupe rows.
    Prefers UDISE-like fields if present; else school_name + first other field.
    """
    if not rec:
        return ""

    key_hints = ["udise", "school code", "sch code", "school id", "udise code", "udise no", "udise number"]
    for k, v in rec.items():
        if isinstance(k, str) and any(h in k.lower() for h in key_hints):
            vv = str(v).strip()
            if vv:
                return f"ID::{vv}"

    sn = str(rec.get("school_name", "")).strip()
    if sn:
        extra = ""
        for k, v in rec.items():
            if k == "school_name":
                continue
            vv = str(v).strip()
            if vv:
                extra = vv
                break
        return f"SN::{sn}::{extra}"

    # stable fallback (not python hash)
    canon = "|".join([f"{k}={rec[k]}" for k in sorted(rec.keys())])
    return "RAW::" + hashlib.md5(canon.encode("utf-8")).hexdigest()


def collect_full_page_records(page):
    """
    Scroll through virtual list and merge everything into a full set for this page.
    (This prevents “some pages give limited data” due to virtualization / lazy render.)
    """
    scroll_to_top(page)
    wait_for_results_settled(page)

    collected = {}
    no_new = 0

    for _ in range(SCROLL_MAX_STEPS):
        dom_recs = extract_current_dom_records(page)
        new_added = 0

        for r in dom_recs:
            uid = record_uid(r)
            if not uid:
                continue
            if uid not in collected:
                collected[uid] = r
                new_added += 1
            else:
                old = collected[uid]
                for k, v in r.items():
                    if k not in old or (not old.get(k) and v):
                        old[k] = v

        no_new = no_new + 1 if new_added == 0 else 0

        info = scroll_step(page, SCROLL_STEP_PX)

        # extra settle to avoid missing rows on slow pages
        page.wait_for_timeout(250)
        wait_for_results_settled(page, timeout_ms=8_000)

        if info.get("at_bottom") and no_new >= 2:
            break

    return list(collected.values())


def rotate_list_from(items, start_item_u):
    if not start_item_u:
        return items
    up = [x.strip().upper() for x in items]
    if start_item_u not in up:
        return items
    idx = up.index(start_item_u)
    return items[idx:] + items[:idx]


# ---------------------------
# Main
# ---------------------------
def main():
    ensure_csv_exists(OUT_CSV)

    completed = load_completed_districts()
    seen = load_seen()
    header = read_csv_header(OUT_CSV)

    ck_dist_u, ck_page = read_checkpoint()
    start_u = (ck_dist_u or START_DISTRICT.strip().upper())

    print(f"[RESUME] checkpoint district={ck_dist_u or '(none)'} page={ck_page}")
    print(f"[RESUME] starting from={start_u}")
    print(f"[RESUME] completed districts={len(completed)} | seen rows={len(seen)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO_MS,
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-breakpad",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Kolkata",
        )

        if BLOCK_HEAVY_RESOURCES:
            def route_handler(route, request):
                if request.resource_type in {"image", "font", "media"}:
                    return route.abort()
                return route.continue_()
            context.route("**/*", route_handler)

        page = context.new_page()
        page.set_default_timeout(WAIT_MS)

        try:
            page.goto(URL, wait_until="domcontentloaded")
            page.wait_for_timeout(800)
            wait_and_click_advanced(page)

            # State
            state_sel = get_select_by_index(page, 0)
            pick_option_by_text(state_sel, STATE)
            page.wait_for_timeout(600)

            # District list
            district_sel = get_select_by_index(page, 1)
            districts = extract_option_texts(district_sel, prefer_ng_star=True)
            if not districts:
                raise RuntimeError("No districts found after selecting state.")

            districts = rotate_list_from(districts, start_u)
            print(f"Districts total={len(districts)} | rotated from {start_u}")

            for di, dist in enumerate(districts, start=1):
                dist_u = dist.strip().upper()

                if dist_u in completed:
                    print(f"[SKIP] {dist} already completed")
                    continue

                print(f"\n[DISTRICT {di}/{len(districts)}] {dist}")
                write_checkpoint(dist_u, 0)

                # Ensure dropdown reachable
                page.evaluate("window.scrollTo(0,0)")
                page.wait_for_timeout(200)

                # Select district reliably
                for attempt in range(3):
                    district_sel = get_select_by_index(page, 1)
                    district_sel.scroll_into_view_if_needed()
                    pick_option_by_text(district_sel, dist)
                    page.wait_for_timeout(700)

                    selected = get_selected_option_text(district_sel).strip().upper()
                    if selected == dist_u:
                        break
                    if attempt == 2:
                        raise RuntimeError(f"District not selecting. Wanted={dist}, got={selected}")

                click_search(page)

                page_no = 0
                zero_pages_in_a_row = 0

                while True:
                    page_no += 1

                    page_records = collect_full_page_records(page)

                    # retry once if 0 (slow render)
                    if len(page_records) == 0:
                        page.wait_for_timeout(ZERO_PAGE_RETRY_WAIT_MS)
                        page_records = collect_full_page_records(page)

                    if len(page_records) == 0:
                        zero_pages_in_a_row += 1
                    else:
                        zero_pages_in_a_row = 0

                    # Convert to rows to append (wide)
                    to_append: List[Dict] = []
                    new_seen_hashes: List[int] = []

                    for rec in page_records:
                        rec["state"] = STATE
                        rec["district"] = dist
                        # school_name already comes from SCHOOL_NAME_VALUE_SEL in JS

                        uid = record_uid(rec)
                        key = stable_hash64(dist_u + "||" + uid)
                        if key in seen:
                            continue

                        seen.add(key)
                        new_seen_hashes.append(key)
                        to_append.append(rec)

                    # Ensure schema has all keys, then append (crash safe)
                    if to_append:
                        header = ensure_header_has_keys(OUT_CSV, header, to_append)
                        append_rows_wide(OUT_CSV, header, to_append)
                        append_seen(new_seen_hashes)

                    # Always checkpoint (even if appended=0)
                    write_checkpoint(dist_u, page_no)

                    print(f"  page={page_no} cards={len(page_records)} appended_rows={len(to_append)}")

                    # stop conditions
                    if zero_pages_in_a_row >= MAX_ZERO_PAGES_IN_A_ROW:
                        print("  [STOP] 0 results twice -> next district")
                        break

                    if not next_button_available(page):
                        break

                    moved = False
                    for _ in range(MAX_NEXT_NOCHANGE_RETRIES):
                        if not next_button_available(page):
                            break
                        if click_next_safe(page):
                            moved = True
                            break
                        page.wait_for_timeout(600)

                    if not moved:
                        print("  [STOP] Next did not change -> next district")
                        break

                # mark district completed (so restart skips it)
                completed.add(dist_u)
                mark_district_completed(dist_u)

                # checkpoint to next district (so restart continues)
                next_u = ""
                for j in range(di, len(districts)):
                    cand_u = districts[j].strip().upper()
                    if cand_u not in completed:
                        next_u = cand_u
                        break
                if next_u:
                    write_checkpoint(next_u, 0)

                print(f"[DISTRICT DONE] {dist}")

            print(f"\nDONE ✅ Saved -> {OUT_CSV}")

        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            dump_debug(page, prefix="kys_fail_mapping")
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()



