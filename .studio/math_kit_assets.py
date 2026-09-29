"""Export mathematical modules through the existing immutable asset contract."""

from card_kit_assets import export_kit


def export_math_kit(runtime_root, target):
    return export_kit(runtime_root, target, 'math-kit',
                      'Plan-owned mathematical diagrams with frozen glyph coverage and split layers')
