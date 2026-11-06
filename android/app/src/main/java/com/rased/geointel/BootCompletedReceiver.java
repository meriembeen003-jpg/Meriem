package com.rased.geointel;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import androidx.core.content.ContextCompat;

public class BootCompletedReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || !Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            return;
        }
        SharedPreferences prefs = context.getSharedPreferences(
            SentinelForegroundService.PREFS_NAME,
            Context.MODE_PRIVATE
        );
        String savedUrl = prefs.getString(SentinelForegroundService.KEY_SERVER_URL, "");
        if (savedUrl != null && !savedUrl.isEmpty()) {
            Intent svcIntent = new Intent(context, SentinelForegroundService.class);
            svcIntent.putExtra("serverUrl", savedUrl);
            svcIntent.putExtra("pollSeconds", 30);
            ContextCompat.startForegroundService(context, svcIntent);
        }
    }
}
