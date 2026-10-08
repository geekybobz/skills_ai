# Education Add-on

Use this add-on when the Markdown is meant to help a reader learn, revise, or
understand unfamiliar material. The model analyzes the topic, audience,
project, and existing notes; the user does not have to choose learning devices
or design the presentation.

## Outcome

Create the smallest learning structure that makes the topic easier to
understand and revisit. Keep the document useful as ordinary Markdown. Learning
blocks are optional aids, not a second document system.

## Add-on declaration

| field | declaration |
|---|---|
| Trigger | Learning, revision, or explanation of unfamiliar material; not ordinary reference prose that needs no teaching treatment |
| Blocks | Review cards, intuition/precision split, confusions, examples, contrasts, formulas, evidence status, connections, and further reading |
| Layout variants | Adaptive reading flow inside one file or routed topics/deep notes |
| Generated views | Optional review deck or learning path only when declared by the project |
| Checks | Factual ownership, source verification, portable meaning, restrained tone, and selected-block usefulness |
| Composition | The subject or evidence skill owns domain correctness and source discovery |
| Boundaries | No quiz quota, invented citation, mandatory plugin, or hidden prerequisite |

## Analyze before proposing

Determine what the reader needs to understand, what knowledge can be assumed,
which distinctions are easy to confuse, and where an example, comparison,
formula, visual, or source would materially help. Then include the selected
learning treatment in the normal Markdown Protocol proposal.

Do not ask the user to choose from a catalogue unless a missing audience or
learning objective would materially change the result. Do not add every
available block merely because it exists.

## Details

## Adaptive reading flow

Use this conceptual order when it fits:

```text
topic orientation
    -> short core explanation
    -> selected learning blocks
    -> deeper explanation or example
    -> connections and optional reading
```

This is not a required file layout or heading sequence. A short topic may need
only a paragraph and one review card. A large topic may route to deeper notes.

## Learning blocks

Choose the minimum useful combination.

| block | use when |
|---|---|
| Quick Review / Fact Card | a compact fact, rule, or distinction is worth revisiting |
| Intuition and Precise Meaning | an accessible explanation and formal meaning should remain distinct |
| Common Confusion | two interpretations are likely to be mixed |
| Micro-example | one small example clarifies the core idea |
| Concept Contrast | repeated fields distinguish several related ideas |
| Formula Card | symbols, conditions, meaning, or limitations need a compact map |
| Derivation Landmarks | a long derivation needs a purpose-level route |
| Evidence Status | exact, numerical, proposed, and unknown claims must remain separate |
| Connections | prerequisites, related ideas, uses, or next topics help navigation |
| Further Reading | a verified paper, review, or tutorial adds useful optional depth |

The block names are descriptive, not mandatory labels. Adapt them to the
project's existing language.

## Compact card form

Prefer a portable blockquote and include only fields that carry information:

```markdown
### Quick review — Topic

> **Core idea:** One compact statement.
>
> **Remember:** The decisive distinction or limitation.
>
> **Applies when:** The relevant context, if it prevents ambiguity.
```

Do not force question-and-answer wording. Keep prerequisites, conclusions,
safety constraints, and important limitations outside collapsed content.

## Optional recall card

Use a recall card only when active retrieval is genuinely useful. Keep the
question visible and the answer optional:

```markdown
### Recall — Stable short name

**Question:** What is the decisive distinction?

<details>
<summary>Show answer</summary>

The compact answer, including its important limitation.

</details>
```

The answer must repeat no hidden prerequisite or safety condition. Prefer the
Quick Review / Fact Card when a direct summary is more natural than a question.
Do not turn every heading, definition, or paragraph into a recall card.

## Glossary block

Use a glossary only when several unavoidable terms recur:

```markdown
### Glossary

| term | plain meaning | precise meaning or owner |
|---|---|---|
| Example term | Short accessible meaning | Formal distinction or link |
```

Define a term once and link to its owning topic. Do not copy a full explanation
into the glossary.

## Learning path from prerequisites

When topics use typed `Prerequisite` connections, derive the learning path from
that graph rather than manually maintaining a second order. The path is valid
only when prerequisites are acyclic. Use the package tool to inspect it:

```bash
mdp graph <collection-root> --topic topics/example.md
```

The graph supplies required-before relationships. The author still decides
whether optional Related or Deeper material belongs in a suggested route.

## Optional generated review deck

`REVIEW_DECK.md` may be generated when a collection has enough stable recall
cards to justify one. Its canonical sources are the local cards beside their
owning topics. The generated deck:

- identifies its sources and regeneration command;
- links every card back to its owning topic;
- copies only the question and collapsible answer;
- preserves source order or a declared prerequisite-derived order;
- is replaced as a whole and checked for freshness;
- remains optional and non-authoritative.

Do not create or hand-maintain a deck for a small collection. This design does
not itself authorize or provide a generator.

## Further reading

Add a source only when it materially extends the exact concept. Prefer an
accessible review or tutorial for orientation and a primary paper when it is
the natural source of the result.

```markdown
**Further reading:** [Title](stable-link) — one sentence explaining its exact
relevance. *(Review, tutorial, or primary paper.)*
```

Before adding it, verify the title, authorship, year, source type, link target,
and relevance using supplied evidence or source discovery authorized for the
task. Prefer a DOI, publisher page, arXiv record, or another stable first-party
record. Do not invent a citation, recommend from an uncertain memory, imply
that a link was read when it was not, or fill every card with a paper.

Another research or evidence skill may own source discovery and scientific
judgment. This add-on then owns only the concise, accurate presentation and
link placement. Skill selection alone grants no network or acquisition
authority.

## Visual treatment

- Use headings and whitespace before decorative devices.
- Use blockquotes for compact cards and tables only for real comparisons.
- Use collapsible details only for optional depth and keep a visible fallback.
- Use a small Mermaid diagram only for a relationship, sequence, hierarchy, or
  state change that is harder to understand in prose.
- Split or simplify a large graph instead of shrinking it into an unreadable
  overview.
- Give every important visual a short textual explanation.
- Avoid decorative icons, repeated callouts, dramatic labels, and plugin-only
  presentation unless the project requests them and portable meaning remains.

## Tone and editing

Write short, compact, straightforward sentences. Prefer plain language; define
an unavoidable technical term briefly and use it consistently. Avoid hype,
dramatic transitions, promotional claims, unnecessary academic phrasing, and
false certainty.

When editing existing material, preserve the reader's established tone,
deliberate terminology, and later manual edits. Improve ambiguity locally
rather than rewriting the collection into a uniform model voice. If a style
change would be broad, include it in the reviewed proposal.

## Ownership and maintenance

Keep each card beside the topic that owns its fact. Detailed prose expands the
compact statement rather than competing with it. A consolidated review page
should link to the owning topics or be generated from a declared source; do not
manually copy the same cards into a second collection.

When a fact changes, update its owning topic and its local learning block in the
same change. Remove a block when it becomes redundant, misleading, or harder to
maintain than the explanation it supports.

## Validation

- The selected blocks address actual learning difficulties in this topic.
- The structure remains smaller than the material it explains.
- Facts, formulas, examples, and limitations agree with their authoritative
  owners.
- Further-reading metadata and destinations were verified, or the suggestion
  was omitted.
- Visual meaning remains available in portable text.
- The result is direct, restrained, and consistent with the user's tone.
- No project-specific content, fixed paper list, quiz requirement, plugin, or
  card quota has been introduced by this protocol.
- Recall answers hide no prerequisite, safety condition, or main conclusion.
- A generated review deck names its sources, links to owners, and is current.
- A generated learning path agrees with acyclic Prerequisite connections.

---

[⌂ Home](../../INDEX.md)
