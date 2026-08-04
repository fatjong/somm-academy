# 侍酒師學院 · 網頁版（PWA）

上傳這個資料夾的**內容**到任何 HTTPS 空間即可。iPhone 用 Safari 開啟後，
「分享 → 加入主畫面」就會變成全螢幕 App，可離線遊玩。

## 檔案

- `index.html` 主程式（教學、闖關、動畫、音效、排行榜）
- `manifest.webmanifest` App 名稱與圖示
- `sw.js` 離線快取（**改版時請把裡面的 VERSION 加一**）
- `icon-192.png` / `icon-512.png` 圖示
- `voice/` 預錄語音（可選，放入後音質最佳且完全離線）

## GitHub Pages 部署

1. 把本資料夾內容推到 repo 的 `main` 分支根目錄
2. Settings → Pages → Source 選 `Deploy from a branch` → `main` / `(root)`
3. 等一兩分鐘，網址為 `https://<帳號>.github.io/<repo>/`

## 更新版本

改好 `index.html` 後，記得同步把 `sw.js` 的 `VERSION` 加一再上傳，
否則使用者的裝置會沿用舊快取。
