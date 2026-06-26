# GitHub Copilot Instructions — awesome-dnd-copilot-

This repository is a curated library of GitHub Copilot instruction files and custom agents for Dungeons & Dragons. When assisting in this repository:

- **Be helpful with D&D content**: This repo contains Markdown files with Copilot instructions and agent definitions. Help improve prompts, add specificity, and ensure they produce high-quality D&D content.
- **Maintain tone consistency**: D&D content ranges from high fantasy to gritty realism. Match the tone of the campaign folder you are working in.
- **D&D 5e is the default ruleset** unless another edition is explicitly mentioned.
- **Respect the folder structure**: Each top-level folder (`campaign-creation/`, `campaign-maintenance/`, `running-campaign/`) has a distinct purpose. Keep contributions in the appropriate folder.
- **Agent files are Markdown**: Files under `agents/` directories are Copilot custom agent definitions. They must follow the format: a YAML front-matter block with `description` and `tools` fields, followed by a Markdown body with the agent's system prompt.
- **Quality over quantity**: Every file should be immediately useful to a DM or player who copies it into their own repository.
