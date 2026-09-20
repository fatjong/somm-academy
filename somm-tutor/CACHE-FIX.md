# 改版後聽到舊版？先做這一步

## 為什麼會這樣

`somm-academy` 是 PWA，根目錄有 `sw.js`（Service Worker）。它的作用範圍是
`/somm-academy/` **整個目錄，包含所有子目錄**，所以 `somm-tutor/` 也會被它
攔截並用快取回應。你更新了檔案，瀏覽器卻仍播放舊版。

## 兩個解法

### 解法一：換個位置部署（建議）

把 somm-tutor 放到**獨立的 repo**，不要放在 somm-academy 底下。這樣完全
不受那支 Service Worker 影響，也不會互相干擾。

    https://<帳號>.github.io/somm-tutor/

### 解法二：留在原處，但要手動清

每次改版後，在 somm-tutor 頁面上按 F12 開開發者工具：

1. Application 分頁 → Service Workers → 對 somm-academy 那項按 Unregister
2. Application 分頁 → Storage → Clear site data
3. 關掉開發者工具，按 Ctrl+Shift+R 強制重新整理

或是直接在網址後面加個變動參數，避開快取：

    https://.../somm-tutor/?v=2&voice

## 確認是不是真的更新了

用 `?voice` 開啟，畫面左下角會顯示實際選用的語音名稱。上方也會出現語音
排查列，可以手動切換語音並試聽。

如果左下角完全沒東西，代表你看到的還是舊版，快取沒清掉。
