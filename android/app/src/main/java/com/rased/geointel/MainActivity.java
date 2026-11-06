package com.rased.geointel;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SentinelNativePlugin.class);
        super.onCreate(savedInstanceState);
    }
}
