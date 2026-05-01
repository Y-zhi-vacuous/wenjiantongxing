# APK 构建指南

## 前提
- 安装 [Android Studio](https://developer.android.com/studio) (免费)

## 构建步骤

0. 先构建 Web 并同步到 Android 项目：
```bash
cd frontend
npm run build
npx cap sync android
```

1. 打开 Android Studio → **Open** → 选择项目中的 `frontend/android` 目录
2. 等待 Gradle 自动同步（首次约 3-5 分钟，自动下载 Android SDK）
3. 菜单 **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
4. 等待构建完成（约 2 分钟）
5. 右下角弹窗 → 点 **locate** → 找到 `app-debug.apk`

## APK 安装

将 `app-debug.apk` 发送到 Android 手机：
- 微信/QQ 文件传输
- USB 连接传输
- 或直接 `adb install app-debug.apk`

## APK 特性

- 教师登录 → 自动进入教师端
- 学生登录 → 自动进入学生端
- 所有功能与网页版一致
- API 自动连接公网服务器 `https://wppyqjhwlqso.usw-1.sealos.app`

## 注意

- 首次安装需要允许「未知来源」应用安装
- APK 为 Debug 版本，正式发布可用 Android Studio 生成签名 Release 版
