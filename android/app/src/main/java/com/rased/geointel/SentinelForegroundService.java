package com.rased.geointel;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.json.JSONArray;
import org.json.JSONObject;

public class SentinelForegroundService extends Service {

    public static final String CHANNEL_DAEMON = "rased_vigilance_daemon";
    public static final String CHANNEL_CRITICAL = "rased_critical_war_alerts";
    public static final String PREFS_NAME = "rased_prefs";
    public static final String KEY_SERVER_URL = "server_url";
    public static final String KEY_LAST_SINCE = "last_since_utc";
    private static final int DAEMON_NOTIFICATION_ID = 9001;

    private ScheduledExecutorService scheduler;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannels();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        if (intent != null && intent.hasExtra("serverUrl")) {
            String url = intent.getStringExtra("serverUrl");
            if (url != null && !url.trim().isEmpty()) {
                prefs.edit().putString(KEY_SERVER_URL, url.trim()).apply();
            }
        }

        int pollSeconds = intent != null ? intent.getIntExtra("pollSeconds", 30) : 30;
        if (pollSeconds < 15) pollSeconds = 15;

        Intent openIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingOpen = PendingIntent.getActivity(
            this,
            0,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Notification daemonNotification = new NotificationCompat.Builder(this, CHANNEL_DAEMON)
            .setContentTitle("راصد الجيوسياسي — حالة تأهب دائم 24/7")
            .setContentText("متصل ببوابة المصادر الأم لالتقاط الإنذارات الجيوسياسية فورًا")
            .setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentIntent(pendingOpen)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build();

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                DAEMON_NOTIFICATION_ID,
                daemonNotification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            );
        } else {
            startForeground(DAEMON_NOTIFICATION_ID, daemonNotification);
        }

        restartPollingLoop(pollSeconds);
        return START_STICKY;
    }

    private void restartPollingLoop(int pollSeconds) {
        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.shutdownNow();
        }
        scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleWithFixedDelay(this::pollCloudSentinelOnce, 3, pollSeconds, TimeUnit.SECONDS);
    }

    private void pollCloudSentinelOnce() {
        HttpURLConnection conn = null;
        try {
            SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            String baseUrl = prefs.getString(KEY_SERVER_URL, "");
            if (baseUrl == null || baseUrl.isEmpty()) return;

            String cleanBase = baseUrl.replaceAll("/+$", "");
            String since = prefs.getString(KEY_LAST_SINCE, "");
            String endpoint = cleanBase + "/api/mobile/poll";
            if (since != null && !since.isEmpty()) {
                endpoint += "?since=" + URLEncoder.encode(since, "UTF-8");
            }

            URL url = new URL(endpoint);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(7000);
            conn.setReadTimeout(7000);
            conn.setRequestProperty("Accept", "application/json");
            conn.setRequestProperty("X-Rased-Client", "Android-APK-Foreground-v1");

            if (conn.getResponseCode() != 200) return;

            StringBuilder sb = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8)
            )) {
                String line;
                while ((line = reader.readLine()) != null) {
                    sb.append(line);
                }
            }

            JSONObject json = new JSONObject(sb.toString());
            if (!json.optBoolean("ok", false)) return;

            String serverTime = json.optString("serverTimeUtc", "");
            if (!serverTime.isEmpty()) {
                prefs.edit().putString(KEY_LAST_SINCE, serverTime).apply();
            }

            JSONArray alerts = json.optJSONArray("alerts");
            if (alerts != null) {
                for (int i = 0; i < alerts.length(); i++) {
                    JSONObject alert = alerts.getJSONObject(i);
                    postHighPriorityArabicAlert(
                        alert.optString("id", String.valueOf(System.currentTimeMillis())),
                        alert.optString("titleAr", "راصد — إنذار جيوسياسي"),
                        alert.optString("bodyAr", "")
                    );
                }
            }
        } catch (Exception ignored) {
            // Network transient issue; will automatically retry on next cycle
        } finally {
            if (conn != null) conn.disconnect();
        }
    }

    private void postHighPriorityArabicAlert(String id, String titleAr, String bodyAr) {
        Intent openIntent = new Intent(this, MainActivity.class);
        openIntent.putExtra("dispatchId", id);
        PendingIntent pendingOpen = PendingIntent.getActivity(
            this,
            id.hashCode(),
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Notification alertNotif = new NotificationCompat.Builder(this, CHANNEL_CRITICAL)
            .setSmallIcon(android.R.drawable.stat_notify_error)
            .setContentTitle(titleAr)
            .setContentText(bodyAr)
            .setStyle(new NotificationCompat.BigTextStyle().bigText(bodyAr))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .setContentIntent(pendingOpen)
            .build();

        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            nm.notify(Math.abs(id.hashCode()), alertNotif);
        }
    }

    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm == null) return;

            NotificationChannel daemonChan = new NotificationChannel(
                CHANNEL_DAEMON,
                "خدمة التأهب السحابي المستمر (24/7)",
                NotificationManager.IMPORTANCE_LOW
            );
            daemonChan.setDescription("تحافظ على ارتباط التطبيق الدائم ببوابة المصادر الأم");
            nm.createNotificationChannel(daemonChan);

            NotificationChannel critChan = new NotificationChannel(
                CHANNEL_CRITICAL,
                "إنذارات الحروب والأحداث الجيوسياسية العاجلة",
                NotificationManager.IMPORTANCE_HIGH
            );
            critChan.setDescription("إشعارات فورية بالعربية للبرقيات المؤكدة من المصادر الأم");
            critChan.enableVibration(true);
            nm.createNotificationChannel(critChan);
        }
    }

    @Override
    public void onDestroy() {
        if (scheduler != null) {
            scheduler.shutdownNow();
        }
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
