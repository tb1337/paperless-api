(function () {
  var PIXEL_URL = "https://data.tbsch.de/p/N2J4VgMWJ";

  function count() {
    fetch(PIXEL_URL, { mode: "no-cors", cache: "no-store", keepalive: true });
  }

  // document$ replays on subscribe and re-emits after every instant
  // navigation, so each rendered page counts as one view.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(count);
  } else {
    count();
  }
})();
