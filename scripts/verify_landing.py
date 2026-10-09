"""Exercise the approved landing with the actual native documentation controls."""

import traceback
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def point(page):
    return page.locator("#ts-beam").evaluate("el=>[+el.getAttribute('cx'),+el.getAttribute('cy')]")


def check_navigation(browser, base, output):
    page = browser.new_page(viewport={"width": 1440, "height": 1024})
    page.goto(base)
    page.locator(".ts-search-trigger").focus()
    page.keyboard.press("Enter")
    page.locator('[data-md-component="search-query"]').fill("fixture")
    expect(page.locator(".md-search-result__link").first).to_be_visible(timeout=30000)
    page.keyboard.press("Escape")
    page.locator(".ts-scroll-link").click()
    expect(page.locator("#ts-language-section")).to_be_focused()
    page.locator(".ts-header .md-select button").click()
    link = page.locator('[data-ts-language][lang="es"]')
    fragment = urlsplit(link.get_attribute("href")).fragment
    link.click()
    page.wait_for_url("**/es/**")
    expect(page.locator(".ts-home")).to_have_attribute("data-lang", "es")
    if fragment:
        expect(page.locator("#" + fragment)).to_be_in_viewport()
    page.locator(".ts-cover .ts-primary").click()
    page.wait_for_url("**/es/getting-started/")
    page.locator('label[for="__palette_1"]').click()
    expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "slate")
    page.locator(".md-select button").click()
    page.locator('[data-ts-language][lang="en"]').click()
    page.wait_for_url("**/getting-started/")
    expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "slate")
    assert page.evaluate("""() => {
      const h=document.querySelector('.md-header'),t=document.querySelector('.md-tabs');
      const a=getComputedStyle(h),b=getComputedStyle(t);
      return getComputedStyle(document.body).animationName==='ts-header-flow' &&
        a.backgroundImage===b.backgroundImage && a.backgroundPosition===b.backgroundPosition;
    }""")
    page.screenshot(path=str(output / "documentation-header.png"))
    page.goto(base + "language/")
    anchor = page.locator("h2[id]").nth(3).get_attribute("id")
    page.locator('.md-sidebar--secondary a[href="#' + anchor + '"]').click()
    expect(page.locator("#" + anchor)).to_be_in_viewport()
    page.locator(".md-select button").click()
    link = page.locator('[data-ts-language][lang="es"]')
    translated = link.evaluate("(el,id)=>JSON.parse(el.dataset.tsFragments)[id]", anchor)
    link.click()
    page.wait_for_url("**/es/language/**")
    # Tracking may normalize the address; the translated section must actually be visible.
    expect(page.locator("#" + translated)).to_be_in_viewport()
    expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "slate")
    page.locator(".md-logo").first.click()
    expect(page.locator("#ts-pause")).to_be_visible()
    assert page.locator(".ts-home").get_attribute("data-lang") == "es"
    page.close()


def check_cache(browser, base):
    paths = ("assets/landing.css", "assets/product.js", "assets/style.css", "assets/navigation.js")
    versions = {path: sha256((ROOT / "docs" / path).read_bytes()).hexdigest()[:16] for path in paths}
    for locale in ("", "es/"):
        page = browser.new_page()
        seen = set()

        def cached(route):
            url = urlsplit(route.request.url)
            path = next((path for path in paths if url.path.endswith("/" + path)), None)
            if path is None:
                route.continue_()
            elif parse_qs(url.query).get("content") == [versions[path]]:
                seen.add(path)
                route.continue_()
            else:
                route.fulfill(content_type="text/css" if path.endswith(".css") else "text/javascript",
                              body="body{background:white}" if path.endswith(".css") else "void 0;")

        page.route("**/assets/**", cached)
        page.goto(base + locale)
        expect(page.locator("#ts-pause")).to_be_visible()
        assert seen == set(paths), seen
        page.close()


def check_motion(browser, base, output):
    page = browser.new_page(viewport={"width": 1440, "height": 1024})
    page.goto(base)
    expect(page.locator("#ts-score")).to_have_attribute("data-active", "1", timeout=6000)
    page.locator("#ts-pause").click()
    frozen = point(page)
    page.wait_for_timeout(500)
    assert point(page) == frozen
    page.locator(".ts-concept").last.hover()
    assert point(page) == frozen
    page.emulate_media(reduced_motion="reduce")
    expect(page.locator("#ts-pause")).to_be_disabled()
    expect(page.locator("#ts-score")).to_have_attribute("data-phase", "reduced")
    page.emulate_media(reduced_motion="no-preference")
    expect(page.locator("#ts-pause")).to_be_enabled()
    expect(page.locator("#ts-pause")).to_have_attribute("aria-pressed", "true")
    page.locator("#ts-pause").click()
    page.wait_for_function("p=>{const b=document.querySelector('#ts-beam');return +b.getAttribute('cx')!==p[0] || +b.getAttribute('cy')!==p[1]}", arg=frozen, timeout=5000)
    # Capture the full connected return; each frame must stay geometrically continuous.
    page.evaluate("""() => new Promise(resolve => {
      let last=null,max=0,cycles=0,active='';const started=performance.now();
      function sample(){const b=document.querySelector('#ts-beam'),s=document.querySelector('#ts-score');
        const p=[+b.getAttribute('cx'),+b.getAttribute('cy')];
        if(last)max=Math.max(max,Math.hypot(p[0]-last[0],p[1]-last[1]));
        if(active==='3'&&s.dataset.active==='0')cycles++;
        active=s.dataset.active;last=p;
        if(performance.now()-started>12000){window.motionAudit={max,cycles};resolve();}
        else requestAnimationFrame(sample);
      }sample();
    })""")
    audit = page.evaluate("motionAudit")
    assert audit["cycles"] >= 1 and audit["max"] < 130, audit
    page.screenshot(path=str(output / "connected-motion.png"))
    page.close()


def main():
    server_root = ROOT / "build/docs-server"
    server_root.mkdir(parents=True, exist_ok=True)
    mount = server_root / "testscript"
    if not mount.exists():
        mount.symlink_to(ROOT / "site", target_is_directory=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(server_root)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}/testscript/"
    output = ROOT / "build/landing-checks"
    output.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=["--no-sandbox"])
            check_cache(browser, base)
            for locale in ("en", "es"):
                for width, height in ((1440, 1024), (1366, 625), (820, 1180), (390, 844), (320, 900)):
                    page = browser.new_page(viewport={"width": width, "height": height})
                    errors = []
                    page.on("pageerror", lambda error, found=errors: found.append(str(error)))
                    page.goto(base + ("es/" if locale == "es" else ""))
                    try:
                        expect(page.locator("#ts-pause")).to_be_visible()
                    except AssertionError as error:
                        page.screenshot(path=str(output / f"{locale}-{width}-{height}-failure.png"), full_page=True)
                        raise AssertionError((locale, width, errors)) from error
                    page.evaluate("document.fonts.ready")
                    assert page.locator("h1").count() == 1
                    assert page.locator("pre,code,canvas,table").count() == 0
                    assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
                    assert page.locator(".ts-home").get_attribute("data-lang") == locale
                    assert page.locator(".ts-header .md-select button").evaluate(
                        "el=>el.getBoundingClientRect().right<=document.querySelector('.ts-search-trigger').getBoundingClientRect().left"
                    )
                    if width >= 760:
                        assert page.locator(".ts-cover .ts-primary").evaluate("el=>el.getBoundingClientRect().bottom<=innerHeight")
                    page.screenshot(path=str(output / f"{locale}-{width}-{height}.png"), full_page=True)
                    # Connector lanes must stay outside all visible descriptions and keywords.
                    collision = page.evaluate("""() => {
                      const s=document.querySelector('#ts-score').getBoundingClientRect();
                      const p=document.querySelector('#ts-track'),n=p.getTotalLength();
                      const boxes=[...document.querySelectorAll('.ts-concept h2,.ts-concept p')].map(e=>e.getBoundingClientRect());
                      for(let d=0;d<n;d+=3){const q=p.getPointAtLength(d),x=q.x+s.left,y=q.y+s.top;
                        const hit=boxes.find(b=>x>b.left+1&&x<b.right-1&&y>b.top+1&&y<b.bottom-1);
                        if(hit)return {x,y,box:{left:hit.left,right:hit.right,top:hit.top,bottom:hit.bottom},score:{width:s.width,height:s.height}};}
                      return null;
                    }""")
                    assert collision is None, (locale, width, collision)
                    page.screenshot(path=str(output / f"{locale}-{width}-{height}.png"), full_page=True)
                    page.locator('label[for="__palette_1"]').click()
                    expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "slate")
                    cover = page.locator(".ts-cover").evaluate("el=>getComputedStyle(el).backgroundColor")
                    page.locator('label[for="__palette_0"]').click()
                    expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "default")
                    assert cover == page.locator(".ts-cover").evaluate("el=>getComputedStyle(el).backgroundColor")
                    assert not errors, errors
                    page.close()
            failures = []
            for name, check in (("navigation", check_navigation), ("motion", check_motion)):
                try:
                    check(browser, base, output)
                except Exception as error:
                    traceback.print_exc()
                    failures.append((name, str(error)))
                    for context in browser.contexts:
                        for page in context.pages:
                            page.screenshot(path=str(output / (name + "-failure.png")), full_page=True)
                            page.close()
            reduced = browser.new_page(reduced_motion="reduce")
            reduced.goto(base)
            expect(reduced.locator("#ts-pause")).to_be_disabled()
            reduced.close()
            static = browser.new_page(java_script_enabled=False)
            static.goto(base + "es/")
            expect(static.locator("h1")).to_contain_text("Más intención.")
            expect(static.locator("#ts-pause")).to_be_hidden()
            static.screenshot(path=str(output / "no-javascript.png"))
            static.close()
            browser.close()
            assert not failures, failures
        print("Chromium passed: EN/ES, five viewports, native search/navigation/palette, fixed cover palette, "
              "text-safe connector lanes, complete motion loop, pause, reduced motion, no-JS and asset cache.")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
