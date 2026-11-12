/* Evil Santa: the landing-page comic booklet (uses page-flip, MIT licence). */
(function () {
  "use strict";
  const book = document.getElementById("spirit-book");
  if (!book || !window.St || !window.St.PageFlip) return;

  const pages = Array.from(document.querySelectorAll(".spirit-comic-page"));
  const counter = document.getElementById("spirit-comic-counter");
  const total = pages.length;

  // Size the book to the space between the navbar and the bottom of the screen.
  const nav = document.querySelector(".navbar.fixed-top");
  const navH = nav ? nav.offsetHeight : 56;
  const availH = window.innerHeight - navH - 150;
  const pageH = Math.max(420, Math.min(1100, availH));
  const pageW = Math.round(pageH * 2 / 3);
  book.style.maxWidth = pageW * 2 + "px";

  const flip = new St.PageFlip(book, {
    width: pageW,
    height: pageH,
    size: "stretch",
    minWidth: 240,
    maxWidth: pageW,
    minHeight: 360,
    maxHeight: pageH,
    showCover: true,
    usePortrait: true,
    mobileScrollSupport: false,
    maxShadowOpacity: 0.5,
    flippingTime: 900,
    clickEventForward: true,
  });
  flip.loadFromHTML(pages);

  function label(i) {
    if (i === 0) return "Front cover";
    if (i === total - 1) return "Back cover";
    return "Page " + i + " of " + (total - 2);
  }
  function update() {
    const i = flip.getCurrentPageIndex();
    // A closed book shows only one page: slide it to the centre
    const twoUp = flip.getOrientation() === "landscape";
    book.classList.toggle("is-front", twoUp && i === 0);
    book.classList.toggle("is-back", twoUp && i >= total - 1);
    if (counter) counter.textContent = label(i);
    document.querySelector(".spirit-comic-nav.prev").disabled = i === 0;
    document.querySelector(".spirit-comic-nav.next").disabled = i >= total - 1;
  }
  flip.on("flip", update);
  flip.on("changeOrientation", update);
  update();

  document.querySelector(".spirit-comic-nav.prev").addEventListener("click", () => flip.flipPrev());
  document.querySelector(".spirit-comic-nav.next").addEventListener("click", () => flip.flipNext());
  document.addEventListener("keydown", (e) => {
    if (e.target.closest("input, textarea, select")) return;
    if (e.key === "ArrowRight") flip.flipNext();
    if (e.key === "ArrowLeft") flip.flipPrev();
  });
})();
