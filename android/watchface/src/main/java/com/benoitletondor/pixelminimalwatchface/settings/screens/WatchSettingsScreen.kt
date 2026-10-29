/*
 *   Copyright 2022 Benoit LETONDOR
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */
package com.benoitletondor.pixelminimalwatchface.settings.screens

import com.benoitletondor.pixelminimalwatchface.common.settings.SettingsScreen

class WatchSettingsScreen : SettingsScreen {
    override val includeHeader: Boolean = true
    override val includeFooter: Boolean = true
    override val weatherTempScaleDisclaimer: String = "Temperature scale (°F or °C) is controlled by the Weather app."
}
