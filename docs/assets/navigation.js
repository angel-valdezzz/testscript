/* Language destinations are generated per page; retain translated sections. */
(() => {
  "use strict";
  const entryFragment = location.hash;
  const links = document.querySelectorAll("[data-ts-language]");
  function syncFragments() {
    let fragment;
    try { fragment = decodeURIComponent(location.hash.slice(1)); }
    catch { fragment = ""; }
    for (const link of links) {
      const url = new URL(link.href);
      const fragments = JSON.parse(link.dataset.tsFragments || "{}");
      url.hash = fragments[fragment] || "";
      link.href = url.href;
    }
  }
  syncFragments();
  addEventListener("hashchange", syncFragments);
  // Tracking uses replaceState after scrolling. Refresh before choosing a language,
  // without rewriting the clicked destination after focus has changed the scroll position.
  let scrollRefresh;
  addEventListener("scroll", () => {
    clearTimeout(scrollRefresh);
    scrollRefresh = setTimeout(syncFragments, 350);
  }, {passive: true});
  // Restore incoming anchors after fonts and native layout have settled. Otherwise
  // tracking can clear the hash while the translated document is still at the top.
  addEventListener("load", async () => {
    if (!entryFragment) return;
    if (document.fonts) await document.fonts.ready;
    let id;
    try { id = decodeURIComponent(entryFragment.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target) return;
    requestAnimationFrame(() => {
      history.replaceState(history.state, "", entryFragment);
      target.scrollIntoView();
      syncFragments();
    });
  }, {once: true});
})();
