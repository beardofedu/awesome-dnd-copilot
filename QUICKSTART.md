# Five-minute quickstart

Try a DM-only workspace with one instruction profile and the Session Bridge kit,
then inspect its fictional recap. No Copilot account is needed to install and
inspect files; using the prompts needs a supported
[Copilot surface](./COMPATIBILITY.md).

## 1. Choose (about one minute)

You need Git, Python 3.9+, and a Bash-compatible terminal. Clone the library, or
open a terminal at the root of your existing checkout:

```bash
git clone https://github.com/beardofedu/awesome-dnd-copilot.git
cd awesome-dnd-copilot
python3 tools/campaign-starter/install.py --list
```

Choose **one** profile: `campaign-creation` for world-building,
`campaign-maintenance` for notes and continuity, or `running-campaign` for
at-the-table help. The commands below use `campaign-maintenance` and the
[Session Bridge](./campaign-maintenance/session-kits/session-bridge/README.md)
kit so you can inspect a recap immediately. No custom agent is required.

## 2. Preview, then install (about two minutes)

Use the same terminal for the remaining commands. Choose a fresh local
destination **outside this library checkout**, reserved for the DM:

```bash
campaign_dir="$HOME/dnd-quickstart"
mkdir -p "$campaign_dir"
python3 tools/campaign-starter/install.py "$campaign_dir" \
  --profile campaign-maintenance \
  --kit campaign-maintenance/session-bridge --starter
```

The preview lists source-to-destination mappings and writes nothing to the
destination. Expect `.github/copilot-instructions.md`, the whole kit under
`.github/session-kits/session-bridge/`, empty campaign workspace files, and
`LICENSE`. Review those mappings, then explicitly apply the same selection:

```bash
python3 tools/campaign-starter/install.py "$campaign_dir" \
  --profile campaign-maintenance \
  --kit campaign-maintenance/session-bridge --starter --apply
```

If the destination already contains conflicting files, the installer refuses
the selection before writing; choose a fresh directory rather than overwriting
your campaign. Keep `LICENSE`. For other selections and safeguards, see the
[selective installer guide](./tools/campaign-starter/README.md).

## 3. Inspect the fictional result (about two minutes)

Open the destination in your editor. Read `.github/copilot-instructions.md`
and `.github/session-kits/session-bridge/README.md`, then print the sample:

```bash
python3 -m json.tool \
  "$campaign_dir/.github/session-kits/session-bridge/state.example.json"
```

Look for `reviewStatus: "sample"` and **The Lantern at Reedbridge**. The recap
describes a recovered lantern; `facts` places the mill north of Reedbridge,
while `suggestions` proposes Mira offering supplies. That proposal is not
established canon. The sample stays inside the kit; your `canon/`, `sessions/`,
and `prep/` folders contain guidance, not an installed campaign story.

**Stop here for a local trial.** The installer creates no GitHub repository,
changes no permissions, and activates no workflows, Canvases, automations, or
Pages. Keep any real DM repository private to the DM team. Folders and audience
labels do not restrict access. Start empty before real play; samples are not
approved canon. Share only explicitly reviewed material through a separate
player workspace, never by granting players access to DM files or history.

For the longer setup-to-sharing path, continue with the
[first campaign walkthrough](./examples/first-campaign/README.md).
