/* Language destinations are generated per page; retain translated sections. */
(() => {
  "use strict";
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
  // Material's tracking can use replaceState, which does not emit hashchange.
  for (const link of links) link.addEventListener("click", syncFragments);
})();
