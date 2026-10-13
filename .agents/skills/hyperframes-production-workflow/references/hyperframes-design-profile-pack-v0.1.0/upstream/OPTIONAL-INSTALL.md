# Optional Upstream Installation

These installations are optional and intended for Profile maintenance, source comparison or one-off QA. They are not required for normal HyperFrames execution.

## Emil Kowalski skills

```bash
npx skills@latest add emilkowalski/skills
```

Useful maintenance targets:

- `apple-design`
- `emil-design-eng`
- `review-animations`

## Kami

For generic agents that read `~/.agents/`:

```bash
npx skills add tw93/kami/plugins/kami -a universal -g -y
```

Do not use the Kami document-generation workflow as the runtime for a HyperFrames video. Read its design references only when maintaining Profile 2.

## Impeccable

```bash
npx impeccable install
```

For Profile 3 maintenance, use only the relevant design reasoning:

```text
/impeccable distill
/impeccable quieter
/impeccable typeset
/impeccable layout
```

Do not allow Impeccable to replace the Profile's visual world during a normal video task.

## Recommended update workflow

1. Record the current Profile Pack version.
2. Read upstream release notes and changed design references.
3. Create a bounded diff: retained rule, rejected rule, adapted rule.
4. Update one Profile at a time.
5. Render a fixed three-scene regression sample in both 16:9 and 9:16.
6. Compare hierarchy, overflow, motion and identity drift.
7. Increment this pack's version only after the regression sample passes.
