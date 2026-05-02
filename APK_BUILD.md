# APK 构建指南 v2.1

## 前提
- 安装 [Android Studio](https://developer.android.com/studio) (免费，含 Java 21 + Android SDK 34+)

## 构建步骤

0. 先构建 Web 并同步到 Android 项目：
```bash
cd frontend
npm install
npm run build
npx cap sync android
```

1. 打开 Android Studio → **Open** → 选择项目中的 `frontend/android` 目录
2. 等待 Gradle 自动同步（首次约 3-5 分钟，自动下载 Android SDK）
3. 菜单 **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
4. 等待构建完成（约 2 分钟）
5. 右下角弹窗 → 点 **locate** → 找到 `app-debug.apk`

## 命令行构建 (需 Java 21 + Android SDK)
```bash
export JAVA_HOME=/path/to/jdk-21
export ANDROID_HOME=$HOME/AppData/Local/Android/Sdk
cd frontend
npm run build && npx cap sync android
cd android
echo "sdk.dir=$ANDROID_HOME" > local.properties
./gradlew assembleDebug
```

## APK 位置
`frontend/android/app/build/outputs/apk/debug/app-debug.apk`

## APK 特性
- 教师登录 → 自动进入教师端
- 学生登录 → 自动进入学生端
- 所有功能与网页版一致
- API 自动连接公网服务器

## 注意
- 首次安装需要允许「未知来源」应用安装
- APK 为 Debug 版本，正式发布可用 Android Studio 生成签名 Release 版
