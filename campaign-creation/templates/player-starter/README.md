# Player campaign workspace

An empty, player-facing workspace. This template does not create a repository,
change permissions, activate services, or publish a website. Use it in a
separate repository containing only information its readers may know.

Fill in `campaign.md` using approved shared facts. Add reviewed recaps to
`journal/`, known quests to `quests/`, and discovered places and people to
`world/`. Character choices belong to their players; distinguish theories from
facts. These folders are organizational, not access controls.

Keep DM canon, private preparation, unreleased lore, secret backstories,
personal disclosures, and credentials in the DM-only repository. The DM
manually transfers only reviewed player material. Website publication requires
separate approval for public use, even if players already know the information.

The installed `.github/copilot-instructions.md` limits routine assistance to
this player-facing context. Review it before use; instructions do not enforce
repository permissions or guarantee confidentiality.

If you also selected the player site, customize `docs/` using
`.github/prompts/customize-campaign-site.prompt.md`. Preview with:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Then follow the library's
[site setup guide](https://github.com/beardofedu/awesome-dnd-copilot/blob/main/campaign-creation/templates/campaign-player-site/README.md).
Only `docs/` is the recommended Pages source; the workspace directories are
not automatically rendered. They remain readable to repository readers.
