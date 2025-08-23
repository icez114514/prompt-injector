# Prompt Injector（從 PNG metadata 注入 Prompt）

> **簡介**

`prompt_injector.py` 是一個針對 Stable Diffusion WebUI 的插件（scripts 格式），可以從上傳的 PNG 圖片檔案中擷取 `parameters` / `Prompt` 等 metadata，並在生成時自動將該圖片內的正向與負向提示詞注入到輸入參數中，方便你重現或混合其他作品的提示詞。

<img width="768" height="1186" alt="image" src="https://github.com/user-attachments/assets/42ac26ac-015f-4c29-b911-5ffa581e75fb" />

---

## 主要功能

- 支援最多 6 張圖片（每張在獨立的 Tab 中設定）
- 可選是否啟用某張圖片、是否注入正向提示詞、是否注入負向提示詞
- 可選注入位置（前面 / 後面）以便把新提示詞串接到原提示詞的前端或尾端

---

## 安裝（手動）

1. 進入你的 Stable Diffusion WebUI 的 `extensions` 或 `scripts` 目錄。
2. 把 `prompt_injector.py` 放到 `scripts/` 資料夾內（或放入你的 plugin repository），例如：

```
stable-diffusion-webui/
└─ extensions/ (選用)
└─ scripts/
   └─ prompt_injector.py
```

3. 重新啟動 WebUI。插件會被 `modules.scripts` 自動發現並載入。

---

## 使用方式（在 WebUI）

1. 開啟 WebUI 的 `txt2img` 或 `img2img` 頁面。

2. 在負向提示詞元件（negative prompt）之後會出現一個收合式的區塊：**“Prompt Injector（從 PNG metadata 注入 prompt）”**。

3. 展開後會看到 **6 個 Tab**（Image 1 \~ Image 6），每個 Tab 有以下選項：

   - `啟用 Image N`：是否啟用該張圖片作為來源
   - `Image N`：上傳含 提示詞 metadata 的 PNG（建議輸出自 Stable Diffusion 的 PNG）
   - `附加正向 提示詞`：是否注入圖片內的正向提示詞
   - `附加負向 提示詞`：是否注入圖片內的負向提示詞
   - `附加位置`：選擇 `前面` 或 `後面`（決定把圖片提示詞加在原提示詞的前面或後面）

4. 設定完成後按下生成，插件會自動讀取每張啟用圖片的 metadata，並把擷取出的提示詞注入到生成參數中。

---

## 範例

假設你上傳的一張 PNG metadata 內容如下：

```
A beautiful magical forest, sunlight beams, high detail
negative prompt: lowres, bad anatomy, watermark
Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 7.0
```

插件會擷取正向 `A beautiful magical forest, sunlight beams, high detail`，負向 `lowres, bad anatomy, watermark`，並分別注入到生成參數中（依你在該 Tab 的勾選設定和附加位置）。

---
