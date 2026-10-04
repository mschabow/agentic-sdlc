---
name: spec
description: Turn a short "what do you want to do" prompt into a structured spec draft. Explores the codebase for contact points and side effects, checks Linear and Drive for context, asks clarifying questions, and produces one or more SCRUM user stories with acceptance criteria. Run as the first step of the design phase, before context pass 1 and /grill-with-docs.
---

You are turning a rough idea into a structured first-draft spec. Be thorough in code exploration, concise in output.

## Step 1 — Capture the prompt

Ask: "What do you want to build or change?" Accept a short answer. Don't let the user write the spec — that's your job.

## Step 2 — Explore the codebase

Before asking any questions, explore the codebase:

- Find files, components, and interfaces likely to be touched
- Identify **contact points**: what calls what, what data flows where, what interfaces would change
- Surface **side effects**: what else depends on the changing code, what could break, what migrations or compatibility concerns exist
- Note existing patterns the implementation should follow

## Step 3 — Check connected sources

- **Linear:** search for related tickets, prior decisions, or a parent PRD for this area
- **Google Drive:** check the feature's Drive folder (if it exists) and `_evergreen/` for relevant background

## Step 4 — Ask clarifying questions

Ask only what you couldn't answer from the codebase and connected sources. One question at a time. Focus on:

- Who is the role this serves, and what is their observable outcome?
- What does production success look like — measurable if possible?
- Any constraints: performance, security, backwards compatibility?
- Anything ambiguous that has multiple valid interpretations

Stop when you have enough to write a tight user story and testable acceptance criteria.

## Step 5 — Output the spec draft

If the prompt covers more than one distinct capability, split into separate user stories — each becomes its own Linear sub-ticket created later via `/decompose`.

For each story:

---
**User story [N]:** As a [role], I want [capability], so that [benefit].

**Acceptance criteria:**
1. [observable, testable outcome]
2. ...

**Code contact points:**
- `[file or component]` — [what changes and why]

**Side effects and risks:**
- [what else may be affected, what could break, migration or compatibility concerns]

**Out of scope:**
- [explicitly excluded to keep this story bounded]

---

If multiple stories: note that each will become a sub-ticket in Linear via `/decompose` after the design PR is approved. The design ticket covers all stories in one spec.

## Step 6 — Hand off

Tell the user: this draft anchors the next broad context pass. After the context pass, run `/grill-with-docs` to stress-test and refine before writing `spec.md`.
