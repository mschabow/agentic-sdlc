# Google Drive Conventions

Google Drive is the source of record for raw background material: meeting transcripts, research documents, vendor docs, and decisions that haven't yet been promoted into ADRs or Linear. It is not a filing cabinet for finished artifacts — those live in GitHub (designs, code) or Linear (tickets, PRDs).

The folder structure mirrors the Linear project hierarchy so that Pass 1 context gathering in the design and build phases is targeted, not a full-Drive search.

## Folder structure

```
Google Drive/
├── _evergreen/                         ← cross-project reference docs; always included in Pass 1
│   ├── architecture-overview.md
│   ├── tech-stack.md
│   └── ...
│
├── [Linear Project Area A]/            ← one folder per Linear project or product area
│   ├── _background/                    ← research, vendor docs, product requirements
│   ├── transcripts/                    ← meeting and interview recordings/notes
│   │   └── YYYY-MM-DD — topic.md
│   ├── decisions/                      ← decisions made in conversation before they become ADRs
│   └── [Feature Name]/                 ← feature-specific subfolder, created when design ticket opens
│       ├── _background/
│       └── transcripts/
│           └── YYYY-MM-DD — topic.md
│
├── [Linear Project Area B]/
│   └── ...
```

## Naming conventions

| Type | Format | Example |
|---|---|---|
| Project area folder | Match Linear project name exactly | `Payments Platform` |
| Feature subfolder | Match Linear ticket title (slugified) | `checkout-redesign` |
| Transcript | `YYYY-MM-DD — topic` | `2026-06-12 — checkout flow whiteboard` |
| Background doc | Descriptive noun phrase | `stripe-api-reference.md` |
| Decision record (pre-ADR) | `YYYY-MM-DD — decision` | `2026-06-10 — auth middleware approach` |

## Evergreen documents

The `_evergreen/` folder contains cross-project reference material that is relevant to almost any feature: architecture overviews, tech stack decisions, API contracts, coding standards. These are always pulled into Pass 1 context gathering alongside the feature-specific folder.

An evergreen document must be actively maintained. If it becomes stale, remove it from `_evergreen/` rather than leaving outdated information in the path of every future context pass.

## How this connects to the workflow

**Design ticket (Sources field):** link to the feature subfolder in Drive (or the project area folder if no feature subfolder exists yet). Claude Code's Pass 1 context gather reads the linked folder plus `_evergreen/`.

**Transcripts before context.md:** if a Slack conversation contains relevant decisions, capture it as a transcript in the appropriate Drive folder before starting the design phase. Once it's in Drive it becomes a valid context source. Slack itself is never referenced in `context.md`.

**Creating the feature subfolder:** the human engineer creates it when they open the design ticket, before running `/grill-with-docs`. Transcripts and background material collected during the design session go here.

## What does not belong in Drive

- Finished design documents → GitHub (`designs/<feature>/spec.md`)
- Tickets, status, and work breakdown → Linear
- Code → GitHub
- Slack conversation threads → never stored as-is; summarise and promote to a transcript if the content matters
