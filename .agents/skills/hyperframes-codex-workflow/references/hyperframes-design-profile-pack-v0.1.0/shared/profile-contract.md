# Shared Profile Contract

Every Profile must define the following fields. Missing fields must be resolved during profile maintenance, not improvised per video.

## 1. Identity

- stable profile ID;
- public name;
- one-sentence visual thesis;
- emotional target;
- intended content classes;
- explicit anti-references.

## 2. Tokens

- canvas and surfaces;
- primary, secondary and accent colors;
- text hierarchy;
- border/rule/shadow values;
- radius and spacing system;
- motion timing and easing;
- typography stacks and fallbacks.

No arbitrary color, radius, font, or easing may be introduced during implementation unless the Animation Plan declares the deviation and the user approves it.

## 3. Composition

A Profile must define:

- how a focal point is established;
- how supporting evidence is grouped;
- how relationships and sequence are shown;
- default information density;
- how negative space functions;
- how 16:9 and 9:16 differ without changing identity.

## 4. Material

Material describes what visual objects appear to be made from—glass, paper, ink, light, rules, photographic surfaces—not a list of CSS effects.

Material rules must state:

- where the material may appear;
- how many material surfaces may coexist;
- what creates depth;
- what is forbidden;
- how the material behaves in motion.

## 5. Typography

Typography must define roles instead of only naming fonts:

- display/claim;
- explanatory body;
- label/metadata;
- numeric/data;
- English product names;
- CJK fallback behavior.

Do not package or redistribute font files. Only reference legally available system/open fonts, and document any licensing constraints.

## 6. Motion grammar

Each Profile must define 4–6 motion verbs. Every scene animation must map to one of them.

The motion grammar must specify:

- semantic purpose;
- timing range at 60fps;
- easing or spring behavior;
- acceptable distance/scale/blur change;
- entrance, hold, resolution and exit behavior;
- reduced-motion equivalent.

## 7. Two-mode mapping

The Profile must explain how the same identity maps to:

- `talking_head`: source footage/person remains primary;
- `pure_hyperframes`: typography, graphics and media form the complete visual field.

## 8. Anti-patterns

Anti-patterns are hard bans unless explicitly approved. They should be concrete and testable, such as:

- number of simultaneous focal points;
- maximum accent coverage;
- forbidden gradients/material combinations;
- forbidden motion curves;
- forbidden card nesting;
- face/caption overlap rules.

## 9. QA

Every Profile must provide a short scene-level checklist that can be answered from rendered frames and source code.
