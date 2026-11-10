/* Progressive enhancement: the generated resource list works without scripts. */
"use strict";

function matchesResource(resource, query, filters) {
  const words = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return words.every((word) => resource.text.toLowerCase().includes(word)) &&
    Object.entries(filters).every(([key, value]) =>
      !value || resource[key].includes(value));
}

if (typeof module !== "undefined") {
  module.exports = { matchesResource };
}

if (typeof document !== "undefined") {
  const form = document.querySelector("#filters");
  const query = document.querySelector("#query");
  const keys = ["phase", "audience", "setup", "feature"];
  const selects = keys.map((key) => document.getElementById(key));
  const cards = [...document.querySelectorAll(".resource")].map((element) => ({
    element,
    text: element.textContent,
    ...Object.fromEntries(keys.map((key) => [key, element.dataset[key].split("|")])),
  }));
  const count = document.querySelector("#result-count");
  const empty = document.querySelector("#empty");

  function update() {
    const filters = Object.fromEntries(selects.map((select) => [select.id, select.value]));
    let visible = 0;
    for (const card of cards) {
      const matches = matchesResource(card, query.value, filters);
      card.element.hidden = !matches;
      if (matches) visible += 1;
    }
    count.textContent = `${visible} of ${cards.length} resources`;
    empty.hidden = visible !== 0;
  }

  form.addEventListener("input", update);
  form.addEventListener("change", update);
  form.addEventListener("submit", (event) => event.preventDefault());
  form.addEventListener("reset", () => {
    // Reset values are applied by the browser after the event handler returns.
    setTimeout(update, 0);
  });
  form.hidden = false;
  update();
}
