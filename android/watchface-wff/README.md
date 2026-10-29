# Pixel Minimal Watch Face – Watch Face Format version

Version of the watch face in the [Watch Face Format][wff] (WFF), for Wear OS 5 and newer.

Since January 2026 Wear OS requires the Watch Face Format for watch faces, and some watches (for example the
OnePlus Watch 3) only offer WFF watch faces in their picker. The legacy watch face in `../watchface` is still
needed for Wear OS 2 and 3, which don't support WFF.

## Variants

Complication slots can't be moved by a setting in WFF, so each layout is its own watch face:

| Flavor      | Watch face name                        | Application ID                                           |
|-------------|----------------------------------------|----------------------------------------------------------|
| `regular`   | Pixel Minimal Watch Face               | `com.benoitletondor.pixelminimalwatchface.wff`           |
| `android12` | Pixel Minimal Watch Face (Android 12)  | `com.benoitletondor.pixelminimalwatchface.wff.android12` |

Both can be installed at the same time, and next to the legacy watch face.

```bash
./gradlew :watchface-wff:assembleDebug
adb install watchface-wff/build/outputs/apk/regular/debug/watchface-wff-regular-debug.apk
```

## Settings

Everything is configured from the watch face editor of the watch (long press on the watch face, then
"Customize"): widgets, widgets color, time/date/battery/seconds ring colors, size of time, WearOS logo, watch
battery indicator, weather, short date format, seconds ring and the ambient mode options.

Differences with the legacy watch face:

- 12/24h format follows the system setting.
- One color setting for all widgets (the default keeps the WearOS blue/yellow/red/green per widget).
- Size of date and widgets can't be changed.
- Weather comes from the system weather data of WFF instead of a weather app complication.
- When the WearOS logo or the battery indicator replaces a widget, its slot still shows in the editor but
  nothing is drawn.

## Editing

`src/<flavor>/res/raw/watchface.xml`, `src/main/res/values/strings.xml` and the previews are generated, edit
`generate_watchface.py` and run it:

```bash
pip install pillow xmlschema
python3 generate_watchface.py
git clone --depth 1 https://github.com/google/watchface.git /tmp/watchface
python3 validate_watchface.py /tmp/watchface/third_party/wff/specification/documents 2 src/*/res/raw/watchface.xml
```

## Credits

The `weather_*.png` icons come from the [Wear OS samples][samples] (Apache License 2.0).

[wff]: https://developer.android.com/training/wearables/wff
[samples]: https://github.com/android/wear-os-samples/tree/main/WatchFaceFormat/Weather
