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
package com.benoitletondor.pixelminimalwatchface.model

import android.content.ComponentName
import android.content.Intent
import android.support.wearable.complications.ComplicationHelperActivity
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.navigation.NavController
import com.benoitletondor.pixelminimalwatchface.BuildConfig
import com.benoitletondor.pixelminimalwatchface.Device
import com.benoitletondor.pixelminimalwatchface.PixelMinimalWatchFace
import com.benoitletondor.pixelminimalwatchface.common.settings.model.ComplicationColor
import com.benoitletondor.pixelminimalwatchface.common.settings.model.ComplicationLocation
import com.benoitletondor.pixelminimalwatchface.common.settings.model.Platform
import com.benoitletondor.pixelminimalwatchface.common.settings.model.WeatherProvider
import com.benoitletondor.pixelminimalwatchface.common.settings.navigateToColorSelectionScreen
import com.benoitletondor.pixelminimalwatchface.common.settings.navigateToWidgetSelectionScreen
import com.benoitletondor.pixelminimalwatchface.getWeatherProviderInfo
import com.benoitletondor.pixelminimalwatchface.helper.isScreenRound
import com.benoitletondor.pixelminimalwatchface.rating.FeedbackActivity
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.yield

class WatchPlatform(
    private val activity: ComponentActivity,
    storage: Storage,
    private val permissionRequestActivityLauncher: ActivityResultLauncher<Intent>
) : Platform, Storage by storage {
    override val isScreenRound: Boolean = activity.isScreenRound()
    override val isWearOS3: Boolean = Device.isWearOS3
    override val appVersionName: String = BuildConfig.VERSION_NAME
    override val weatherProvider: WeatherProvider = activity.getWeatherProviderInfo()
        ?.let { WeatherProvider(
            hasWeatherSupport = true,
            weatherProviderInfo = it,
        ) } ?: WeatherProvider(
            hasWeatherSupport = false,
            weatherProviderInfo = null,
        )

    private val watchFaceComponentName = ComponentName(activity, PixelMinimalWatchFace::class.java)

    private val permissionRequestResultMutableFlow = MutableSharedFlow<Boolean>()

    suspend fun onPermissionResult(granted: Boolean) {
        permissionRequestResultMutableFlow.emit(granted)
    }

    override suspend fun requestComplicationsPermission(activity: ComponentActivity): Boolean {
        permissionRequestActivityLauncher.launch(
            ComplicationHelperActivity.createPermissionRequestHelperIntent(
                this.activity,
                watchFaceComponentName,
            )
        )

        yield()

        return permissionRequestResultMutableFlow.first()
    }

    override fun startFeedbackScreen(navController: NavController, activity: ComponentActivity) {
        activity.startActivity(Intent(activity, FeedbackActivity::class.java))
    }

    override suspend fun startColorSelectionScreen(navController: NavController, defaultColor: Int): ComplicationColor? {
        return navController.navigateToColorSelectionScreen(defaultColor)
    }

    override fun startWidgetConfigurationScreen(navController: NavController, complicationLocation: ComplicationLocation) {
        return navController.navigateToWidgetSelectionScreen(complicationLocation)
    }
}
