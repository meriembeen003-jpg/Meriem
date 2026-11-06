package com.rased.geointel;

import android.content.Context;
import android.content.Intent;
import androidx.core.content.ContextCompat;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "SentinelNative")
public class SentinelNativePlugin extends Plugin {

    @PluginMethod
    public void startForegroundVigilance(PluginCall call) {
        String serverUrl = call.getString("serverUrl", "");
        int pollSeconds = call.getInt("pollSeconds", 30);
        Context ctx = getContext();

        Intent svcIntent = new Intent(ctx, SentinelForegroundService.class);
        svcIntent.putExtra("serverUrl", serverUrl);
        svcIntent.putExtra("pollSeconds", pollSeconds);
        ContextCompat.startForegroundService(ctx, svcIntent);

        JSObject ret = new JSObject();
        ret.put("started", true);
        call.resolve(ret);
    }

    @PluginMethod
    public void stopForegroundVigilance(PluginCall call) {
        Context ctx = getContext();
        Intent svcIntent = new Intent(ctx, SentinelForegroundService.class);
        ctx.stopService(svcIntent);

        JSObject ret = new JSObject();
        ret.put("stopped", true);
        call.resolve(ret);
    }
}
