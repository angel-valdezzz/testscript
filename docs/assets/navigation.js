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
  // MkDocs Material's automatic locale handler reconstructs destinations from
  // sitemaps and can discard translated anchors. Our generated href is authoritative.
  for (const link of links) link.addEventListener("click", event => event.stopPropagation());
  for (const button of document.querySelectorAll(".md-select button")) {
    button.addEventListener("pointerdown", syncFragments);
    button.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") syncFragments();
    });
  }
  syncFragments();
  addEventListener("hashchange", syncFragments);
})();
