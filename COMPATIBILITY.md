# Compatibility and requirements

This guide describes the capabilities each resource type needs; it does not
promise that a feature is available to every Copilot account or repository.
Copilot plans, previews, organization policies, and GitHub product behavior can
change. Check current product documentation and your repository's settings
before enabling a feature.

| Resource | Needs | Important limits |
|---|---|---|
| Repository instructions | A Copilot surface that reads repository custom instructions; install the selected profile as `.github/copilot-instructions.md` | Use one profile at a time. Support and instruction handling can vary by surface. |
| Custom agents | A Copilot surface that supports repository custom agents; install selected agent files under `.github/agents/` | Agent files use the repository's YAML-front-matter Markdown format. The presence of a file does not make every Copilot surface offer that agent. |
| Manual prompts and session kits | A Copilot interface where you can provide the prompt and relevant files | These can be used without Canvas or cloud automations. Prompts are guidance, not deterministic guarantees. |
| Canvas starter kits | GitHub Copilot App with Canvas support and the ability to create a Canvas from the included prompt | The files are setup prompts, not prebuilt extensions. Generate and review the Canvas in the App; copying files does not register it. |
| Cloud automation recipes | Eligible Copilot cloud automation access, repository eligibility, permission, and any required administrator approval | Recipes are optional setup data. They are not GitHub Actions workflows; copying them does not create or activate an automation. Availability and billing depend on current product and ownership settings. |
| GitHub Actions workflow templates | GitHub Actions enabled, plus any provider-specific credentials, permissions, and dependencies documented by that workflow | Templates remain inactive until deliberately installed as workflows. Review triggers, permissions, and secrets before use. |
| Python validators and installer | Python 3.9+ for the campaign starter installer; individual tools may have their own requirements | The repository CI uses Python 3.12. Follow each tool's README for its local test command. |
| Campaign player-site scaffold | A static-file preview for local review; GitHub Pages or another static host for deployment | The site has no framework or build step. Publication is a separate, explicit decision; treat a public site as publicly readable. |

## Verify before setup

Read the selected resource's README for exact commands and limitations. In
particular, distinguish manual prompts, Canvas generation, automation
registration, GitHub Actions workflows, and Pages publication: none is
automatically activated merely by copying a file.

- [Copilot App and Canvas setup](./session-kits.md#three-canvas-starter-kits)
- [Cloud automation setup](./session-kits.md#set-up-an-optional-automation)
- [Campaign starter requirements](./tools/campaign-starter/README.md)
- [Player-site publication steps](./campaign-creation/templates/campaign-player-site/README.md#enable-github-pages-explicitly)
- [Repository CI checks](./.github/workflows/prompt-regression.yml)
