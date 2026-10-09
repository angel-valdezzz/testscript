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
  // Keep the documentation header and tabs on the same gradient phase.
  requestAnimationFrame(() => {
    const header = document.querySelector(".md-header"), tabs = document.querySelector(".md-tabs");
    const top = header?.getAnimations().find(animation => animation.animationName === "ts-header-flow");
    const bottom = tabs?.getAnimations().find(animation => animation.animationName === "ts-header-flow");
    if (top && bottom) bottom.currentTime = top.currentTime;
  });
})();
