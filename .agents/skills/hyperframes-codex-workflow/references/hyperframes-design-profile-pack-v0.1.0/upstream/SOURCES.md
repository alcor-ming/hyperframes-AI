# Upstream Sources

Snapshot date: 2026-08-07. Star counts are a time-specific signal, not a quality guarantee.

## Profile 1 source

### emilkowalski/skills

- Repository: https://github.com/emilkowalski/skills
- Snapshot stars: approximately 26.6k
- License: MIT
- Relevant skills: `apple-design`, `emil-design-eng`, `review-animations`
- Used for: purposeful motion, spatial consistency, current-value continuity, translucent material restraint, timing and easing discipline.
- Not copied literally: gesture recognition, pointer events, interaction frequency rules and user-controlled interruptibility.

Why selected over a generic glassmorphism skill:

- It defines why and how movement should feel, not only how glass should look.
- It has explicit material, typography, performance and reduced-motion reasoning.
- It prevents Profile 1 from degenerating into neon HUD decoration.

## Profile 2 source

### tw93/Kami

- Repository: https://github.com/tw93/Kami
- Snapshot stars: approximately 10.4k
- License: MIT for code/templates
- Relevant materials: `SKILL.md`, `references/design.md`, anti-pattern and production references
- Used for: parchment/ink palette, warm neutrals, type-led hierarchy, 4-unit spacing, restrained surfaces, composed-page logic.
- Not copied literally: PDF templates, WeasyPrint pipeline, document schemas, build scripts and font download behavior.

Important font note:

- Kami states TsangerJinKai02 is personal-use-only unless commercially licensed.
- This pack does not include it and defaults to Source Han/Noto/PingFang-style fallbacks.

## Profile 3 source

### pbakaus/impeccable

- Repository: https://github.com/pbakaus/impeccable
- Snapshot stars: approximately 56.5k
- License: Apache-2.0
- Relevant commands: `distill`, `quieter`, `typeset`, `layout`, plus anti-pattern guidance
- Used for: four-gate design governance, removal of redundant elements, restrained color/motion, typography roles, squint test, proximity and rhythm.
- Not inherited: Impeccable project's own current Neo Kinpaku brand identity, frontend CLI/hook behavior and broad product redesign routing.

Why selected for Profile 3:

- Monochrome luxury fails when it is treated as a palette preset.
- Impeccable supplies an editing process that makes restraint testable.
- The four gates produce a consistent reason for every retained element.

## Supplemental source considered

### ibelick/ui-skills

- Repository: https://github.com/ibelick/ui-skills
- Snapshot stars: approximately 7.0k
- License: MIT
- Useful references: `baseline-ui`, `fixing-motion-performance`
- Role in this pack: supplemental performance and anti-slop reference, not a primary Profile identity.

Not selected as Profile 1's main source because it is primarily a baseline/audit layer and does not define a sufficiently distinct optical visual world on its own.
