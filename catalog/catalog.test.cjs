const test = require("node:test");
const assert = require("node:assert/strict");
const { matchesResource } = require("./catalog.js");

const resource = {
  text: "Party Journal & Quest Board known quests campaign-maintenance/session-kits/party-journal",
  phase: ["Campaign maintenance"],
  audience: ["Players"],
  setup: ["Manual prompt", "Canvas generation", "Optional cloud automation"],
  feature: ["Chat prompts", "Canvas", "Cloud automations"],
};

test("search is case-insensitive, matches paths, and requires every word", () => {
  assert.equal(matchesResource(resource, "  QUEST   party-journal ", {}), true);
  assert.equal(matchesResource(resource, "quest missing", {}), false);
  assert.equal(matchesResource(resource, "   ", {}), true);
});

test("filters combine with search and match whole tag values", () => {
  assert.equal(matchesResource(resource, "journal", {
    phase: "Campaign maintenance", audience: "Players",
    setup: "Canvas generation", feature: "Canvas",
  }), true);
  assert.equal(matchesResource(resource, "journal", { audience: "DM" }), false);
  assert.equal(matchesResource(resource, "", { feature: "Cloud" }), false);
  assert.equal(matchesResource(resource, "missing", { feature: "Canvas" }), false);
});

test("empty filters restore matches and multi-audience resources match either audience", () => {
  assert.equal(matchesResource(resource, "", { phase: "", audience: "", setup: "", feature: "" }), true);
  const split = { ...resource, audience: ["DM", "Players"] };
  assert.equal(matchesResource(split, "", { audience: "DM" }), true);
  assert.equal(matchesResource(split, "", { audience: "Players" }), true);
});
