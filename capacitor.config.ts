import type { CapacitorConfig } from "@capacitor/cli";

const cloudServerUrl = process.env.CAPACITOR_CLOUD_SERVER_URL?.trim();

const config: CapacitorConfig = {
  appId: "com.rased.geointel",
  appName: "راصد الجيوسياسي",
  webDir: "mobile-shell",
  ...(cloudServerUrl
    ? {
        server: {
          url: cloudServerUrl,
          cleartext: cloudServerUrl.startsWith("http://"),
        },
      }
    : {}),
  plugins: {
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"],
    },
    LocalNotifications: {
      smallIcon: "ic_stat_icon_config_sample",
      iconColor: "#10B981",
    },
  },
};

export default config;
