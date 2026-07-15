"""Deterministic stitch-symbol SVGs used by the technique library.

Simple stitches follow common Craft Yarn Council chart conventions. Composite
techniques use an explicitly labeled teaching diagram rather than pretending to
have a single universal chart symbol.
"""

from html import escape


_SHAPES = {
    "chain": '<ellipse cx="50" cy="50" rx="27" ry="12"/>',
    "slip_stitch": '<circle cx="50" cy="50" r="7" fill="currentColor"/>',
    "single_crochet": '<path d="M31 31L69 69M69 31L31 69"/>',
    "half_double_crochet": '<path d="M50 72V30M31 30H69"/>',
    "double_crochet": '<path d="M50 75V25M31 25H69M39 52L61 43"/>',
    "magic_ring": '<circle cx="50" cy="50" r="25"/><path d="M68 30l8 2-2 8"/><path d="M72 34a31 31 0 0 1 3 26"/>',
    "round_crochet": '<circle cx="50" cy="50" r="27"/><circle cx="50" cy="50" r="7"/><path d="M50 16v12M84 50H72M50 84V72M16 50h12"/>',
    "cast_on": '<path d="M18 64c12-29 20-29 32 0s20 29 32 0"/><path d="M15 72H85"/>',
    "knit": '<rect x="27" y="27" width="46" height="46"/><path d="M50 35v30"/>',
    "purl": '<rect x="27" y="27" width="46" height="46"/><circle cx="50" cy="50" r="6" fill="currentColor"/>',
    "ribbing": '<rect x="14" y="31" width="18" height="38"/><rect x="32" y="31" width="18" height="38"/><rect x="50" y="31" width="18" height="38"/><rect x="68" y="31" width="18" height="38"/><circle cx="41" cy="50" r="4" fill="currentColor"/><circle cx="77" cy="50" r="4" fill="currentColor"/><path d="M23 39v22M59 39v22"/>',
    "slip_knot": '<path d="M22 65c18-48 45-48 56 0M50 50c-9 9-9 20 0 30M50 50c9 9 9 20 0 30"/>',
    "treble_crochet": '<path d="M50 78V20M31 20H69M38 55L62 46M38 46L62 37"/>',
    "sc_increase": '<path d="M50 72V54M50 54L28 30M50 54L72 30M20 22L36 38M36 22L20 38M64 22L80 38M80 22L64 38"/>',
    "sc2tog": '<path d="M28 30L44 46M44 30L28 46M72 30L56 46M56 30L72 46M36 46L50 70M64 46L50 70"/>',
    "dc2tog": '<path d="M32 24V48M68 24V48M20 24H44M56 24H80M26 38L38 34M62 38L74 34M32 48L50 72M68 48L50 72"/>',
    "front_loop": '<ellipse cx="50" cy="50" rx="29" ry="13"/><path d="M21 50c12-15 46-15 58 0" stroke-width="7"/>',
    "back_loop": '<ellipse cx="50" cy="50" rx="29" ry="13"/><path d="M21 50c12 15 46 15 58 0" stroke-width="7"/>',
    "front_post_dc": '<path d="M50 78V22M30 22H70M39 53L61 44M22 66c12-10 44-10 56 0"/>',
    "back_post_dc": '<path d="M50 78V22M30 22H70M39 53L61 44M22 66c12 10 44 10 56 0" stroke-dasharray="6 5"/>',
    "dc3_cluster": '<path d="M24 24V47M50 20V47M76 24V47M14 24H34M40 20H60M66 24H86M24 47L50 75M50 47V75M76 47L50 75"/>',
    "puff_stitch": '<path d="M50 75V57M50 57C16 45 22 20 50 43M50 57C84 45 78 20 50 43M50 43V22"/>',
    "popcorn_stitch": '<circle cx="50" cy="48" r="25"/><path d="M32 31L68 65M68 31L32 65M50 73V84"/>',
    "shell_stitch": '<path d="M50 76L20 28M50 76L35 22M50 76V18M50 76L65 22M50 76L80 28"/><path d="M13 28H27M28 22H42M43 18H57M58 22H72M73 28H87"/>',
    "bind_off": '<path d="M14 58c10-22 20-22 30 0s20 22 30 0 12-16 18-5"/><path d="M14 68H88"/>',
    "stockinette": '<path d="M24 20L38 80L50 48L62 80L76 20"/>',
    "garter": '<path d="M18 28H82M18 50H82M18 72H82"/><path d="M25 21v14M45 43v14M65 65v14"/>',
    "seed_stitch": '<circle cx="30" cy="30" r="5" fill="currentColor"/><circle cx="70" cy="30" r="5" fill="currentColor"/><circle cx="50" cy="50" r="5" fill="currentColor"/><circle cx="30" cy="70" r="5" fill="currentColor"/><circle cx="70" cy="70" r="5" fill="currentColor"/>',
    "yarn_over": '<circle cx="50" cy="50" r="22"/>',
    "kfb": '<path d="M18 74L40 24M40 24L58 74M58 74L82 24M28 49H70"/>',
    "m1l": '<path d="M70 20L32 50L70 80M32 50H82"/>',
    "m1r": '<path d="M30 20L68 50L30 80M18 50H68"/>',
    "k2tog": '<path d="M25 22L72 78M52 22L72 78M18 22H60"/>',
    "ssk": '<path d="M75 22L28 78M48 22L28 78M40 22H82"/>',
    "p2tog": '<path d="M25 22L72 78M52 22L72 78M18 22H60"/><circle cx="50" cy="50" r="5" fill="currentColor"/>',
    "slip_knit": '<path d="M24 24V76M76 24V76" stroke-dasharray="8 6"/><path d="M24 50H76"/>',
    "pick_up": '<path d="M18 70H82M28 70V38M50 70V30M72 70V38"/><path d="M22 38h12M44 30h12M66 38h12"/>',
    "join_round": '<circle cx="50" cy="50" r="29"/><path d="M74 30l8 2-2 8"/><circle cx="50" cy="21" r="4" fill="currentColor"/>',
    "cable_right": '<path d="M25 18C25 48 75 52 75 82M75 18C75 48 25 52 25 82"/><path d="M66 70L75 82L84 70"/>',
    "cable_left": '<path d="M25 18C25 48 75 52 75 82M75 18C75 48 25 52 25 82"/><path d="M16 70L25 82L34 70"/>',
}


def technique_symbol_svg(symbol_key: str, abbreviation: str, *, compact: bool = False) -> str:
    """Return a static inline SVG plus an accessible abbreviation label."""
    shape = _SHAPES.get(symbol_key, '<circle cx="50" cy="50" r="24"/>')
    size_class = " compact" if compact else ""
    return (
        f'<div class="tech-symbol{size_class}" role="img" aria-label="{escape(abbreviation)} 기호">'
        '<svg viewBox="0 0 100 100" aria-hidden="true" fill="none" '
        'stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">'
        f'{shape}</svg><span>{escape(abbreviation)}</span></div>'
    )
