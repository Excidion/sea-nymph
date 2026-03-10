def resolve_palette(palette, levels, color) -> list:
    if palette is None:
        return [color] * len(levels)
    if isinstance(palette, dict):
        return [palette.get(level) for level in levels]
    return list(palette)
