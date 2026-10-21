# 雅思小說閱讀 IELTS Novel Reader
網頁版：https://wuya0307-creator.github.io/IELTS_NOVEL/

- `index.html`：成品（GitHub Pages 使用） / `config.js`：雲端同步設定 / `src/`：原始碼與小說稿
- 新增小說：放進 `src/content/*.md`，在 `src` 執行 `python build.py`，把 `src/dist/index.html` 覆蓋根目錄 `index.html`

## 開啟跨裝置同步（Firebase，免費、免登入）
1. https://console.firebase.google.com → 建立專案（可關閉 Analytics）
2. 左側 Build → Firestore Database → 建立資料庫（Standard，位置選 asia-east1，先選「測試模式」）
3. 進入「規則」分頁，貼上下列規則後發布：
```
rules_version = '2';
service cloud.firestore {
  match /databases/{db}/documents {
    match /users/{id} { allow read, write: if true; }
  }
}
```
4. 專案設定（齒輪）→ 一般 → 你的應用程式 → 新增網頁應用程式（`</>`），複製 `projectId` 與 `apiKey`
5. 填進 `config.js` 後 push，重新整理網頁即生效
