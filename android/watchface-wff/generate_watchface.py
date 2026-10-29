#!/usr/bin/env python3
#
#   Copyright 2026 The Pixel Minimal Watch Face contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""Generates the Watch Face Format (WFF) sources of the watch face.

The WFF XML is very repetitive (every widget slot needs a layout per complication type, plus copies for
ambient mode and each user setting), so it is generated from the layout description in this file instead
of being edited by hand.

Outputs:
  src/regular/res/raw/watchface.xml            Regular style (same layout as the legacy watch face)
  src/android12/res/raw/watchface.xml          Android 12 style
  src/main/res/values/strings.xml              Labels of the settings and widget slots
  src/<flavor>/res/drawable-nodpi/preview.png  Watch face picker previews (needs Pillow)

Usage: python3 generate_watchface.py
"""

import os
from xml.sax.saxutils import escape

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
RES_MAIN = os.path.join(MODULE_DIR, "src", "main", "res")

SIZE = 450
CENTER = SIZE / 2

FONT = "product_sans_regular"
FONT_THIN = "product_sans_thin"

# Colors used by the legacy watch face
SECONDARY_COLOR = "#FFAAAAAA"
AMBIENT_TIME_COLOR = "#FFDEDEDE"
AMBIENT_COLOR = "#FFDDDDDD"
RING_TRACK_COLOR = "#FF3C3C3C"

# Product Sans metrics, in em: digits are 0.7em high and text is vertically centered on its line box.
DIGIT_HEIGHT = 0.7


def attr(value):
    return escape(str(value), {'"': "&quot;"})


def px(value):
    """Positions and sizes of parts must be integers."""
    return str(int(round(value)))


def fmt(value):
    """Formats a number without useless decimals."""
    value = round(value, 1)
    return str(int(value)) if value == int(value) else str(value)


# --------------------------------------------------------------------------------------------------
# Colors
# --------------------------------------------------------------------------------------------------

WEAR_OS_COLORS = [
    ("WearOS blue", "#5484F8"),
    ("WearOS yellow", "#F2BD00"),
    ("WearOS red", "#DA482F"),
    ("WearOS green", "#54A74C"),
]

MATERIAL_COLORS = [
    ("White", "#FFFFFF"), ("Yellow", "#FFEB3B"), ("Amber", "#FFC107"), ("Orange", "#FF9800"),
    ("Deep orange", "#FF5722"), ("Red", "#F44336"), ("Pink", "#E91E63"), ("Purple", "#9C27B0"),
    ("Deep purple", "#673AB7"), ("Indigo", "#3F51B5"), ("Blue", "#2196F3"), ("Light blue", "#03A9F4"),
    ("Cyan", "#00BCD4"), ("Teal", "#009688"), ("Green", "#4CAF50"), ("Lime green", "#8BC34A"),
    ("Lime", "#CDDC39"), ("Blue grey", "#607D8B"), ("Grey", "#9E9E9E"), ("Brown", "#795548"),
]

PIXEL_COLORS = [
    ("Graphite", "#949494"), ("Cloud", "#E4E4E4"), ("Almond", "#FCF7EB"), ("Watermelon", "#FF7B78"),
    ("Coral", "#F99586"), ("Pomelo", "#FFA49F"), ("Guava", "#FFC1BD"), ("Peach", "#FDB78F"),
    ("Champagne", "#FFD4B6"), ("Chai", "#D8AB77"), ("Sand", "#C4B575"), ("Honey", "#F8C67C"),
    ("Melon", "#FFD88A"), ("Wheat", "#FFE9B9"), ("Dandelion", "#FFFA86"), ("Limoncello", "#FCFFB6"),
    ("Lemongrass", "#EBFFC3"), ("Lime", "#E6FF7B"), ("Pear", "#C7FF81"), ("Spearmint", "#ADF7B9"),
    ("Fern", "#77D9A4"), ("Forest", "#67887B"), ("Mint", "#ABFFDF"), ("Jade", "#BEECDB"),
    ("Sage", "#CCE4DF"), ("Stream", "#B0E4EC"), ("Aqua", "#99F3FF"), ("Sky", "#B6DAF1"),
    ("Ocean", "#A2C2F7"), ("Sapphire", "#81ACF4"), ("Amethyst", "#AEB4FF"), ("Lilac", "#D6C3FF"),
    ("Lavender", "#E4B0FD"), ("Flamingo", "#FABBFF"), ("Bubble Gum", "#FFCAED"), ("Milkshake", "#FFF6E2"),
    ("Salmon", "#FAE7D5"), ("Cantaloupe", "#F8EFCD"), ("Charcoal", "#616161"),
]


def palette():
    """White first, then the same colors as the legacy color picker, without duplicates."""
    seen = set()
    result = []
    for name, color in [MATERIAL_COLORS[0]] + WEAR_OS_COLORS + MATERIAL_COLORS[1:] + PIXEL_COLORS:
        if color in seen:
            continue
        seen.add(color)
        result.append((name, color))
    return result


def argb(color):
    return "#FF" + color[1:].upper()


def slug(name):
    return "".join(c if c.isalnum() else "_" for c in name.lower())


# The widget color setting holds 4 colors, one per widget position
WIDGET_DEFAULT_COLORS = [c for _, c in WEAR_OS_COLORS]  # blue, yellow, red, green
WIDGET_COLOR_COUNT = 4

# The legacy watch face dims colors in ambient mode to 80% of each channel, which on a black background
# is the same as drawing them with 80% opacity.
DIMMED_ALPHA = 204


def widget_color(index):
    return "[CONFIGURATION.widgetColor.%d]" % index


def config_color(config_id):
    return "[CONFIGURATION.%s.0]" % config_id


# --------------------------------------------------------------------------------------------------
# User settings
# --------------------------------------------------------------------------------------------------

STRINGS = {}


def string(key, value):
    STRINGS[key] = value
    return key


COLOR_SETTINGS = [
    ("widgetColor", "Widgets color"),
    ("timeColor", "Time color"),
    ("dateColor", "Date color"),
    ("batteryColor", "Battery indicator color"),
    ("ringColor", "Seconds ring color"),
]

# id, label, default
BOOLEAN_SETTINGS = [
    ("showWearOSLogo", "Show WearOS logo", True),
    ("showBattery", "Watch battery indicator", False),
    ("showWeather", "Show weather after date", False),
    ("shortDate", "Use short date format", False),
    ("secondsRing", "Show seconds ring", False),
    ("smoothRing", "Smooth seconds ring motion", False),
    ("thinTime", "Thin time style when watch is on", False),
    ("ambientNormalTime", "Ambient: normal instead of thin time", False),
    ("ambientDate", "Ambient: show date", True),
    ("ambientWidgets", "Ambient: show widgets", False),
    ("ambientColors", "Ambient: keep colors", False),
    ("ambientBattery", "Ambient: show battery indicator", True),
    ("ambientLogo", "Ambient: show WearOS logo", True),
]

TIME_SIZES = [("0", "Small", 0.9), ("1", "Normal", 1.0), ("2", "Large", 1.1)]
DEFAULT_TIME_SIZE = "1"
BOOLEAN_DEFAULTS = {config_id: default for config_id, _, default in BOOLEAN_SETTINGS}


def user_configurations():
    colors = palette()
    out = ["<UserConfigurations>"]
    for config_id, label in COLOR_SETTINGS:
        out.append('<ColorConfiguration id="%s" displayName="%s" defaultValue="0">' % (
            config_id, string("setting_" + slug(config_id), label)))
        options = []
        if config_id == "widgetColor":
            options.append(("Default", WIDGET_DEFAULT_COLORS))
        options += [(name, [color] * (WIDGET_COLOR_COUNT if config_id == "widgetColor" else 1)) for name, color in colors]
        for index, (name, option_colors) in enumerate(options):
            values = [argb(c) for c in option_colors]
            out.append('<ColorOption id="%d" displayName="%s" colors="%s"/>' % (
                index, string("color_" + slug(name), name), " ".join(values)))
        out.append("</ColorConfiguration>")
    out.append('<ListConfiguration id="timeSize" displayName="%s" defaultValue="%s">' % (
        string("setting_time_size", "Size of time"), DEFAULT_TIME_SIZE))
    for option_id, label, _ in TIME_SIZES:
        out.append('<ListOption id="%s" displayName="%s"/>' % (option_id, string("time_size_" + slug(label), label)))
    out.append("</ListConfiguration>")
    for config_id, label, default in BOOLEAN_SETTINGS:
        out.append('<BooleanConfiguration id="%s" displayName="%s" defaultValue="%s"/>' % (
            config_id, string("setting_" + slug(config_id), label), "TRUE" if default else "FALSE"))
    out.append("</UserConfigurations>")
    return "".join(out)


# --------------------------------------------------------------------------------------------------
# XML building blocks
# --------------------------------------------------------------------------------------------------

HIDE_IN_AMBIENT = '<Variant mode="AMBIENT" target="alpha" value="0"/>'
SHOW_IN_AMBIENT = '<Variant mode="AMBIENT" target="alpha" value="255"/>'
_group_count = [0]


def group(children, x=0, y=0, w=SIZE, h=SIZE, name=None, variants="", alpha=None):
    _group_count[0] += 1
    name = name or "g%d" % _group_count[0]
    alpha_attr = ' alpha="%s"' % alpha if alpha is not None else ""
    return '<Group name="%s" x="%s" y="%s" width="%s" height="%s"%s>%s%s</Group>' % (
        name, px(x), px(y), px(w), px(h), alpha_attr, variants, "".join(children))


def active_only(children, w=SIZE, h=SIZE):
    return group(children, w=w, h=h, variants=HIDE_IN_AMBIENT)


def ambient_only(children, w=SIZE, h=SIZE):
    return group(children, w=w, h=h, alpha=0, variants=SHOW_IN_AMBIENT)


# Settings are read in Condition expressions rather than with BooleanConfiguration / ListConfiguration
# elements in the Scene: those can't be nested ("configuration options cannot be nested in their use",
# https://developer.android.com/training/wearables/wff/personalization/user-configurations), and a nested
# one never reacts to the setting.

# A setting the user never changed may not be set on the running watch face (the editor preview still
# gets its default), so the expressions treat any value but the non default one as the default.

def setting_enabled(config_id):
    default = BOOLEAN_DEFAULTS[config_id]
    return '!([CONFIGURATION.%s] == "FALSE")' % config_id if default else '[CONFIGURATION.%s] == "TRUE"' % config_id


def setting_disabled(config_id):
    default = BOOLEAN_DEFAULTS[config_id]
    return '[CONFIGURATION.%s] == "FALSE"' % config_id if default else '!([CONFIGURATION.%s] == "TRUE")' % config_id


def boolean(config_id, if_true=None, if_false=None, w=SIZE, h=SIZE):
    if if_true:
        return condition([(setting_enabled(config_id), [group(if_true, w=w, h=h)])],
                         default=[group(if_false, w=w, h=h)] if if_false else None)
    return condition([(setting_disabled(config_id), [group(if_false, w=w, h=h)])])


def list_config(config_id, options, default_option, w=SIZE, h=SIZE):
    compares = [('[CONFIGURATION.%s] == "%s"' % (config_id, option_id), [group(children, w=w, h=h)])
                for option_id, children in options if option_id != default_option]
    default = [group(children, w=w, h=h) for option_id, children in options if option_id == default_option]
    return condition(compares, default=default)


_expression_count = [0]


def condition(compares, default=None):
    """compares: list of (expression, children), the first matching one is drawn."""
    names = []
    for _ in compares:
        _expression_count[0] += 1
        names.append("e%d" % _expression_count[0])
    out = ["<Condition><Expressions>"]
    for name, (expression, _) in zip(names, compares):
        out.append('<Expression name="%s">%s</Expression>' % (name, escape(expression)))
    out.append("</Expressions>")
    for name, (_, children) in zip(names, compares):
        out.append('<Compare expression="%s">%s</Compare>' % (name, "".join(children)))
    if default:
        out.append("<Default>%s</Default>" % "".join(default))
    out.append("</Condition>")
    return "".join(out)


def template(pattern, *expressions):
    return "<Template><![CDATA[%s]]>%s</Template>" % (
        pattern, "".join('<Parameter expression="%s"/>' % attr(e) for e in expressions))


def font(size, color, content, family=FONT, extra=""):
    return '<Font family="%s" size="%s" color="%s"%s>%s</Font>' % (family, fmt(size), attr(color), extra, content)


def part_text(x, y, w, h, font_xml, align="CENTER"):
    return '<PartText x="%s" y="%s" width="%s" height="%s"><Text align="%s" ellipsis="TRUE">%s</Text></PartText>' % (
        px(x), px(y), px(w), px(h), align, font_xml)


def centered_text(center_y, size, font_xml, x=0, w=SIZE, align="CENTER"):
    """Text whose digits are vertically centered on center_y."""
    h = round(size * 1.3)
    return part_text(x, center_y - h / 2, w, h, font_xml, align)


def part_image(x, y, w, h, resource, tint=None):
    tint_attr = ' tintColor="%s"' % attr(tint) if tint else ""
    return '<PartImage x="%s" y="%s" width="%s" height="%s"%s><Image resource="%s"/></PartImage>' % (
        px(x), px(y), px(w), px(h), tint_attr, attr(resource))


def inline_image(resource, size, color):
    return '<InlineImage resource="%s" width="%s" height="%s" color="%s"/>' % (resource, px(size), px(size), attr(color))


def arc(x, y, w, h, thickness, color, end_angle_expression=None, cap="ROUND"):
    transform = '<Transform target="endAngle" value="%s"/>' % attr(end_angle_expression) if end_angle_expression else ""
    end = 0 if end_angle_expression else 360
    return ('<PartDraw x="%s" y="%s" width="%s" height="%s"><Arc centerX="%s" centerY="%s" width="%s" height="%s" '
            'startAngle="0" endAngle="%s"><Stroke color="%s" thickness="%s" cap="%s"/>%s</Arc></PartDraw>') % (
        px(x), px(y), px(w), px(h), fmt(w / 2), fmt(h / 2), fmt(w - thickness), fmt(h - thickness), end,
        attr(color), fmt(thickness), cap, transform)


# --------------------------------------------------------------------------------------------------
# Watch face elements
# --------------------------------------------------------------------------------------------------

REGULAR_HOUR = "[IS_24_HOUR_MODE] ? [HOUR_0_23_Z] : [HOUR_1_12]"
ANDROID_12_HOUR = "[IS_24_HOUR_MODE] ? [HOUR_0_23_Z] : [HOUR_1_12_Z]"


def ambient_colored(build, color_config):
    """Ambient copy of an element: dimmed configured color if 'keep colors' is on, grey otherwise."""
    return boolean(
        "ambientColors",
        if_true=[group([build(config_color(color_config))], alpha=DIMMED_ALPHA)],
        if_false=[build(AMBIENT_COLOR if color_config != "timeColor" else AMBIENT_TIME_COLOR)],
    )


def time_text(center_y, size, pattern, hour_expression, thin, color, x=0, w=SIZE, letter_spacing=None, outline=False):
    spacing = ' letterSpacing="%s"' % letter_spacing if letter_spacing is not None else ""
    parts = template(pattern, hour_expression, "[MINUTE_Z]") if hour_expression and "%s:%s" in pattern \
        else template(pattern, hour_expression or "[MINUTE_Z]")
    if outline:
        # Thin style of the regular layout: the legacy watch face draws the time outline only
        # Same as the Flavors sample of Google: the outline wraps the text, filled with the background color
        content = font(size, "#FF000000", '<Outline color="%s" width="2">%s</Outline>' % (attr(color), parts), extra=spacing)
    else:
        content = font(size, color, parts, family=FONT_THIN if thin else FONT, extra=spacing)
    return centered_text(center_y, size, content, x=x, w=w)


def time_block(build):
    """build(scale, thin, color) -> list of elements. Handles size, active/ambient and thin styles."""
    options = []
    for option_id, _, scale in TIME_SIZES:
        active = boolean(
            "thinTime",
            if_true=build(scale, True, config_color("timeColor")),
            if_false=build(scale, False, config_color("timeColor")),
        )
        ambient = boolean(
            "ambientNormalTime",
            if_true=[ambient_colored(lambda c: group(build(scale, False, c)), "timeColor")],
            if_false=[ambient_colored(lambda c: group(build(scale, True, c)), "timeColor")],
        )
        options.append((option_id, [active_only([active]), ambient_only([ambient])]))
    return list_config("timeSize", options, DEFAULT_TIME_SIZE)


# Weather condition -> icon, see https://developer.android.com/training/wearables/wff/weather
WEATHER_ICONS = [
    ([1], "weather_clear", None), ([2], "weather_cloudy", None), ([3, 13], "weather_fog", None),
    ([4], "weather_heavy_rain", None), ([5], "weather_heavy_snow", None), ([6, 12], "weather_rain", None),
    ([7, 11], "weather_snow", None), ([8], "weather_sunny", None), ([9], "weather_thunderstorm", None),
    ([10], "weather_sleet", None), ([14], "weather_partly_cloudy_day", True),
    ([14], "weather_partly_cloudy_night", False), ([15], "weather_windy", None),
]

DATE_SKELETON = 'icuBestText("EEEMMMMd")'
SHORT_DATE_SKELETON = 'icuBestText("EEEMMMd")'
TEMPERATURE = 'round([WEATHER.TEMPERATURE])'
TEMPERATURE_UNIT = '[WEATHER.TEMPERATURE_UNIT] == 1 ? "C" : "F"'


def date_text(center_y, size, color, skeleton, weather_icon=None):
    content = template("%s", skeleton)
    if weather_icon:
        icon_size = round(size * 0.9)
        content = template("%s ", skeleton) + inline_image(weather_icon, icon_size, color) + \
            template(" %s°%s", TEMPERATURE, TEMPERATURE_UNIT)
    return centered_text(center_y, size, font(size, color, content), x=15, w=SIZE - 30)


def date_block(center_y, size):
    def build(color):
        def for_format(skeleton):
            compares = []
            for conditions, icon, is_day in WEATHER_ICONS:
                expression = "[WEATHER.IS_AVAILABLE] && (%s)" % " || ".join("[WEATHER.CONDITION] == %d" % c for c in conditions)
                if is_day is not None:
                    expression += " && %s[WEATHER.IS_DAY]" % ("" if is_day else "!")
                compares.append((expression, [date_text(center_y, size, color, skeleton, icon)]))
            compares.append(("[WEATHER.IS_AVAILABLE]", [date_text(center_y, size, color, skeleton, "weather_unknown")]))
            return boolean(
                "showWeather",
                if_true=[condition(compares, default=[date_text(center_y, size, color, skeleton)])],
                if_false=[date_text(center_y, size, color, skeleton)],
            )
        return group([boolean("shortDate", if_true=[for_format(SHORT_DATE_SKELETON)], if_false=[for_format(DATE_SKELETON)])])

    return group([
        active_only([build(config_color("dateColor"))]),
        boolean("ambientDate", if_true=[ambient_only([ambient_colored(build, "dateColor")])]),
    ])


# Battery level -> icon, same thresholds as the legacy watch face
BATTERY_ICONS = [(10, "battery_10"), (25, "battery_20"), (40, "battery_40"), (50, "battery_50"),
                 (70, "battery_60"), (90, "battery_80"), (100, "battery_100")]
BATTERY_TEXT_SIZE = 24
BATTERY_ICON_SIZE = 22


def battery_block(center_y):
    def build(color):
        def text(icon):
            content = inline_image(icon, BATTERY_ICON_SIZE, color) + template("%s%s", "[BATTERY_PERCENT]", '"%"')
            return centered_text(center_y, BATTERY_TEXT_SIZE, font(BATTERY_TEXT_SIZE, color, content))
        compares = [("[BATTERY_PERCENT] <= %d" % limit, [text(icon)]) for limit, icon in BATTERY_ICONS[:-1]]
        return group([condition(compares, default=[text(BATTERY_ICONS[-1][1])])])

    return [
        active_only([build(config_color("batteryColor"))]),
        boolean("ambientBattery", if_true=[ambient_only([ambient_colored(build, "batteryColor")])]),
    ]


def seconds_ring():
    def ring(expression):
        return [arc(0, 0, SIZE, SIZE, 10, config_color("ringColor"), expression, cap="BUTT")]
    return boolean("secondsRing", if_true=[active_only([boolean(
        "smoothRing",
        if_true=ring("[SECOND_MILLISECOND] * 6"),
        if_false=ring("[SECOND] * 6"),
    )])])


def wear_os_logo(x, y, w=56, h=40):
    return [
        active_only([part_image(x, y, w, h, "wear_os_logo")]),
        boolean("ambientLogo", if_true=[ambient_only([part_image(x, y, w, h, "wear_os_logo_ambient")])]),
    ]


# --------------------------------------------------------------------------------------------------
# Widgets (complications)
# --------------------------------------------------------------------------------------------------

IMAGE = "[COMPLICATION.MONOCHROMATIC_IMAGE] != null"
TITLE = "[COMPLICATION.TITLE] != null"


def text_part(x, y, w, h, size, color, source):
    return part_text(x, y, w, h, font(size, color, template("%s", source)))


def round_widget_texts(s, primary, secondary, scale=1.0):
    """Icon on top and text below, like the legacy short text layout."""
    def sz(value):
        return value * scale
    offset = s * (1 - scale) / 2
    icon_big = sz(34)
    icon_small = sz(28)
    return [condition([
        ("%s && %s" % (IMAGE, TITLE), [
            part_image((s - icon_small) / 2, offset + sz(12), icon_small, icon_small, "[COMPLICATION.MONOCHROMATIC_IMAGE]", primary),
            text_part(6, offset + sz(42), s - 12, sz(28), sz(24), secondary, "[COMPLICATION.TEXT]"),
            text_part(6, offset + sz(66), s - 12, sz(24), sz(19), secondary, "[COMPLICATION.TITLE]"),
        ]),
        (IMAGE, [
            part_image((s - icon_big) / 2, offset + sz(16), icon_big, icon_big, "[COMPLICATION.MONOCHROMATIC_IMAGE]", primary),
            text_part(6, offset + sz(54), s - 12, sz(32), sz(26), secondary, "[COMPLICATION.TEXT]"),
        ]),
        (TITLE, [
            text_part(6, offset + sz(20), s - 12, sz(36), sz(30), primary, "[COMPLICATION.TEXT]"),
            text_part(6, offset + sz(56), s - 12, sz(26), sz(21), secondary, "[COMPLICATION.TITLE]"),
        ]),
    ], default=[
        text_part(6, offset + sz(30), s - 12, sz(40), sz(32), primary, "[COMPLICATION.TEXT]"),
    ])]


def progress_widget(s, primary, secondary, fraction_expression):
    angle = "(%s) * 360" % fraction_expression
    return [
        arc(0, 0, s, s, 5, RING_TRACK_COLOR),
        arc(0, 0, s, s, 5, primary, angle),
    ] + round_widget_texts(s, primary, secondary, scale=0.8)


RANGED_FRACTION = ("(clamp([COMPLICATION.RANGED_VALUE_VALUE], [COMPLICATION.RANGED_VALUE_MIN], [COMPLICATION.RANGED_VALUE_MAX])"
                   " - [COMPLICATION.RANGED_VALUE_MIN]) / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN])")
GOAL_FRACTION = "clamp([COMPLICATION.GOAL_PROGRESS_VALUE], 0, [COMPLICATION.GOAL_PROGRESS_TARGET_VALUE]) / [COMPLICATION.GOAL_PROGRESS_TARGET_VALUE]"


def round_widget(s, primary, secondary):
    return {
        "SHORT_TEXT": round_widget_texts(s, primary, secondary),
        "RANGED_VALUE": progress_widget(s, primary, secondary, RANGED_FRACTION),
        "GOAL_PROGRESS": progress_widget(s, primary, secondary, GOAL_FRACTION),
        "MONOCHROMATIC_IMAGE": [part_image((s - 44) / 2, (s - 44) / 2, 44, 44, "[COMPLICATION.MONOCHROMATIC_IMAGE]", primary)],
        "SMALL_IMAGE": [part_image((s - 64) / 2, (s - 64) / 2, 64, 64, "[COMPLICATION.SMALL_IMAGE]")],
    }


def wide_widget(w, h, primary, secondary):
    """Bottom widget: icon on the left and text, like the legacy long text layout."""
    icon = 30
    text_x = icon + 14
    texts = [condition([
        ("%s && %s" % (IMAGE, TITLE), [
            part_image(6, (h - icon) / 2, icon, icon, "[COMPLICATION.MONOCHROMATIC_IMAGE]", primary),
            text_part(text_x, 4, w - text_x - 6, 30, 24, primary, "[COMPLICATION.TEXT]"),
            text_part(text_x, 32, w - text_x - 6, 26, 20, secondary, "[COMPLICATION.TITLE]"),
        ]),
        (IMAGE, [
            part_image(6, (h - icon) / 2, icon, icon, "[COMPLICATION.MONOCHROMATIC_IMAGE]", primary),
            text_part(text_x, (h - 36) / 2, w - text_x - 6, 36, 26, secondary, "[COMPLICATION.TEXT]"),
        ]),
        (TITLE, [
            text_part(6, 4, w - 12, 30, 24, primary, "[COMPLICATION.TEXT]"),
            text_part(6, 32, w - 12, 26, 20, secondary, "[COMPLICATION.TITLE]"),
        ]),
    ], default=[
        text_part(6, (h - 40) / 2, w - 12, 40, 28, primary, "[COMPLICATION.TEXT]"),
    ])]
    return {
        "LONG_TEXT": texts,
        "SHORT_TEXT": texts,
        "MONOCHROMATIC_IMAGE": [part_image((w - 40) / 2, (h - 40) / 2, 40, 40, "[COMPLICATION.MONOCHROMATIC_IMAGE]", primary)],
        "SMALL_IMAGE": [part_image((w - 50) / 2, (h - 50) / 2, 50, 50, "[COMPLICATION.SMALL_IMAGE]")],
    }


def complication_slot(slot_id, label, x, y, w, h, color_index, wide=False, hidden_when=None):
    """hidden_when: boolean setting that replaces the widget (WearOS logo, battery indicator).

    Complication slots can't be added or removed by a setting in WFF, so in that case the slot stays but
    draws nothing.
    """
    def layouts(primary, secondary):
        return wide_widget(w, h, primary, secondary) if wide else round_widget(w, primary, secondary)

    active = layouts(widget_color(color_index), SECONDARY_COLOR)
    ambient_colors = layouts(widget_color(color_index), SECONDARY_COLOR)
    ambient_grey = layouts(AMBIENT_COLOR, SECONDARY_COLOR)

    complications = []
    for complication_type in active:
        content = [
            active_only(active[complication_type], w, h),
            boolean("ambientWidgets", w=w, h=h, if_true=[ambient_only([boolean(
                "ambientColors", w=w, h=h,
                if_true=[group(ambient_colors[complication_type], w=w, h=h, alpha=DIMMED_ALPHA)],
                if_false=ambient_grey[complication_type],
            )], w, h)]),
        ]
        if hidden_when:
            content = [boolean(hidden_when, if_false=content, w=w, h=h)]
        complications.append('<Complication type="%s">%s</Complication>' % (complication_type, group(content, w=w, h=h)))

    bounding = '<BoundingRoundBox x="0" y="0" width="%s" height="%s" cornerRadius="%s"/>' % (px(w), px(h), fmt(h / 2)) if wide \
        else '<BoundingOval x="0" y="0" width="%s" height="%s"/>' % (px(w), px(h))
    return '<ComplicationSlot slotId="%d" displayName="%s" x="%s" y="%s" width="%s" height="%s" supportedTypes="%s">%s%s</ComplicationSlot>' % (
        slot_id, string("widget_" + slug(label), label), px(x), px(y), px(w), px(h),
        " ".join(list(active) + ["EMPTY"]), bounding, "".join(complications))


# --------------------------------------------------------------------------------------------------
# Layouts, converted from the legacy drawers for a 450px screen (1dp = 2px)
# --------------------------------------------------------------------------------------------------

REGULAR = {
    "time_center": 215, "time_size": 124,
    "date_center": 296, "date_size": 28,
    "widget_size": 100, "widget_y": 58, "widget_x": [69, 175, 281],
    "logo": (197, 88),
    # Unlike the legacy watch face, the battery indicator doesn't replace the bottom widget: the widget is
    # a bit higher and flatter and the battery indicator goes below it.
    "bottom_widget": (87, 322, 275, 58),
    "battery_center": 400,
}

ANDROID_12 = {
    "hour_center": 169.5, "minute_center": 260.5, "time_size": 104, "time_x": 121, "time_width": 200,
    "letter_spacing": -0.12,
    "date_center": 109, "date_size": 26,
    "widget_size": 100, "widget_x": [49, 302], "widget_y": [121, 222],
    "logo": (197, 312),
    "battery_center_with_logo": 393, "battery_center_without_logo": 322,
}


def regular_watch_face():
    l = REGULAR
    time = time_block(lambda scale, thin, color: [time_text(
        l["time_center"], l["time_size"] * scale, "%s:%s", REGULAR_HOUR, thin, color, outline=thin)])
    s = l["widget_size"]
    scene = [
        seconds_ring(),
        boolean("showWearOSLogo", if_true=wear_os_logo(*l["logo"])),
        time,
        date_block(l["date_center"], l["date_size"]),
        boolean("showBattery", if_true=battery_block(l["battery_center"])),
        complication_slot(0, "Left widget", l["widget_x"][0], l["widget_y"], s, s, 0),
        complication_slot(1, "Middle widget", l["widget_x"][1], l["widget_y"], s, s, 1, hidden_when="showWearOSLogo"),
        complication_slot(2, "Right widget", l["widget_x"][2], l["widget_y"], s, s, 2),
        complication_slot(3, "Bottom widget", *l["bottom_widget"], 3, wide=True),
    ]
    return scene


def android_12_watch_face():
    l = ANDROID_12

    def digits(center, expression):
        return lambda scale, thin, color: [time_text(
            center, l["time_size"] * scale, "%s", expression, thin, color,
            x=l["time_x"], w=l["time_width"], letter_spacing=l["letter_spacing"])]

    s = l["widget_size"]
    left, right = l["widget_x"]
    top, bottom = l["widget_y"]
    scene = [
        seconds_ring(),
        date_block(l["date_center"], l["date_size"]),
        time_block(lambda scale, thin, color: digits(l["hour_center"], ANDROID_12_HOUR)(scale, thin, color) +
                   digits(l["minute_center"], None)(scale, thin, color)),
        boolean("showWearOSLogo", if_true=wear_os_logo(*l["logo"])),
        boolean("showBattery", if_true=[boolean(
            "showWearOSLogo",
            if_true=battery_block(l["battery_center_with_logo"]),
            if_false=battery_block(l["battery_center_without_logo"]),
        )]),
        complication_slot(0, "Top left widget", left, top, s, s, 0),
        complication_slot(1, "Top right widget", right, top, s, s, 2),
        complication_slot(2, "Bottom left widget", left, bottom, s, s, 1),
        complication_slot(3, "Bottom right widget", right, bottom, s, s, 3),
    ]
    return scene


def watch_face(scene):
    return ('<WatchFace width="%d" height="%d">'
            '<Metadata key="CLOCK_TYPE" value="DIGITAL"/>'
            '<Metadata key="PREVIEW_TIME" value="10:08:32"/>'
            '%s<Scene backgroundColor="#FF000000">%s</Scene></WatchFace>') % (
        SIZE, SIZE, user_configurations(), "".join(scene))


# Elements with mixed content: whitespace inside them is rendered, so they are kept on a single line
INLINE_ELEMENTS = {"Text", "Expression"}


def pretty(content):
    """Indents the XML so diffs stay readable, without adding whitespace inside text content."""
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString(content.encode("utf-8"))
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<!-- Generated by generate_watchface.py, do not edit by hand. -->"]

    def inline(node):
        # Own serialization, as minidom's escaping changes between Python versions
        if node.nodeType == node.CDATA_SECTION_NODE:
            return "<![CDATA[%s]]>" % node.data
        if node.nodeType == node.TEXT_NODE:
            return escape(node.data)
        attributes = "".join(' %s="%s"' % (name, attr(value)) for name, value in node.attributes.items())
        content = "".join(inline(child) for child in node.childNodes)
        return "<%s%s>%s</%s>" % (node.tagName, attributes, content, node.tagName) if content \
            else "<%s%s/>" % (node.tagName, attributes)

    def emit(node, depth):
        indent = "  " * depth
        if node.tagName in INLINE_ELEMENTS:
            lines.append(indent + inline(node))
            return
        attributes = "".join(' %s="%s"' % (name, attr(value)) for name, value in node.attributes.items())
        children = [child for child in node.childNodes if child.nodeType == child.ELEMENT_NODE]
        if not children:
            lines.append("%s<%s%s/>" % (indent, node.tagName, attributes))
            return
        lines.append("%s<%s%s>" % (indent, node.tagName, attributes))
        for child in children:
            emit(child, depth + 1)
        lines.append("%s</%s>" % (indent, node.tagName))

    emit(dom.documentElement, 0)
    return "\n".join(lines) + "\n"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def strings_xml():
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           "<!-- Generated by generate_watchface.py, do not edit by hand. -->",
           "<resources>"]
    for key in sorted(STRINGS):
        out.append('    <string name="%s">%s</string>' % (key, escape(STRINGS[key]).replace("'", "\\'")))
    out.append("</resources>")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------------------
# Previews
# --------------------------------------------------------------------------------------------------

def render_preview(flavor, path, debug=False):
    """Draws the default look (WearOS logo, time and date) with the same layout constants."""
    from PIL import Image, ImageDraw, ImageFont

    scale = 2  # supersampling
    img = Image.new("RGBA", (SIZE * scale, SIZE * scale), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    font_path = os.path.join(RES_MAIN, "font", FONT + ".ttf")
    logo = Image.open(os.path.join(RES_MAIN, "drawable-nodpi", "wear_os_logo.png")).resize((56 * scale, 40 * scale), Image.LANCZOS)

    def text(center_y, size, value, center_x=CENTER, letter_spacing=0.0):
        f = ImageFont.truetype(font_path, int(size * scale))
        # Center on the digits: baseline = center + digit height / 2
        baseline = (center_y + size * DIGIT_HEIGHT / 2) * scale
        if letter_spacing:
            widths = [f.getlength(c) + letter_spacing * size * scale for c in value]
            x = center_x * scale - (sum(widths) - letter_spacing * size * scale) / 2
            for c, cw in zip(value, widths):
                draw.text((x, baseline), c, font=f, fill=(255, 255, 255, 255), anchor="ls")
                x += cw
        else:
            draw.text((center_x * scale, baseline), value, font=f, fill=(255, 255, 255, 255), anchor="ms")

    if flavor == "regular":
        l = REGULAR
        img.alpha_composite(logo, (l["logo"][0] * scale, l["logo"][1] * scale))
        text(l["time_center"], l["time_size"], "10:08")
        text(l["date_center"] - 4, l["date_size"], "Wed, January 29")
        rects = [(x, l["widget_y"], l["widget_size"], l["widget_size"]) for x in l["widget_x"]] + [l["bottom_widget"]]
    else:
        l = ANDROID_12
        center_x = l["time_x"] + l["time_width"] / 2
        text(l["date_center"] - 4, l["date_size"], "Wed, January 29")
        text(l["hour_center"], l["time_size"], "10", center_x, l["letter_spacing"])
        text(l["minute_center"], l["time_size"], "08", center_x, l["letter_spacing"])
        img.alpha_composite(logo, (l["logo"][0] * scale, l["logo"][1] * scale))
        rects = [(x, y, l["widget_size"], l["widget_size"]) for y in l["widget_y"] for x in l["widget_x"]]

    if debug:
        if flavor == "regular":
            text(REGULAR["battery_center"], BATTERY_TEXT_SIZE, "85%")
        for x, y, w, h in rects:
            draw.rectangle([x * scale, y * scale, (x + w) * scale, (y + h) * scale], outline=(255, 0, 0, 255), width=2)
        draw.ellipse([0, 0, SIZE * scale, SIZE * scale], outline=(80, 80, 80, 255), width=2)

    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.convert("RGB").save(path)


def main():
    flavors = {"regular": regular_watch_face, "android12": android_12_watch_face}
    for flavor, build in flavors.items():
        _group_count[0] = 0
        _expression_count[0] = 0
        content = pretty(watch_face(build()))
        write(os.path.join(MODULE_DIR, "src", flavor, "res", "raw", "watchface.xml"), content)
    write(os.path.join(RES_MAIN, "values", "strings.xml"), strings_xml())
    if os.environ.get("WFF_SKIP_PREVIEWS"):
        return
    try:
        for flavor in flavors:
            render_preview(flavor, os.path.join(MODULE_DIR, "src", flavor, "res", "drawable-nodpi", "preview.png"))
            debug_dir = os.environ.get("WFF_DEBUG_PREVIEW_DIR")
            if debug_dir:
                render_preview(flavor, os.path.join(debug_dir, flavor + "_debug.png"), debug=True)
    except ImportError:
        print("Pillow is not installed: previews were not regenerated")


if __name__ == "__main__":
    main()
