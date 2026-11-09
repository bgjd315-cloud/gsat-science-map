# 年度更新流程（加入新一年的學測自然或分科物化生）

網站：https://bgjd315-cloud.github.io/gsat-science-map/ ・ 儲存庫：https://github.com/bgjd315-cloud/gsat-science-map

每年兩次：學測（1 月考、2 月下旬公布）之後加入**學測自然**；分科（7 月考、7 月下旬公布答對率）之後加入**分科物理、化學、生物**。以下 `YYY` 代表學年度（例如 116）。

| 代碼 | 考科 | `exam` 欄 |
| --- | --- | --- |
| N | 學測自然 | 學測自然 |
| P | 分科物理 | 分科物理 |
| C | 分科化學 | 分科化學 |
| B | 分科生物 | 分科生物 |

## 0. 準備

```bash
git clone https://github.com/bgjd315-cloud/gsat-science-map.git   # 已有就 git pull
cd gsat-science-map
python -m pip install pymupdf pillow xlrd   # 第一次才需要
```

KaTeX 檢查要用 node：在儲存庫外的資料夾 `npm install katex@0.16.9`，再把環境變數 `KATEX_DIR` 設成那個資料夾。

## 1. 下載大考中心檔案

- 學測試題頁：https://www.ceec.edu.tw/xmfile?xsmsid=0J052424829869345634
- 分科試題頁：https://www.ceec.edu.tw/xmfile?xsmsid=0J052427633128416650
- 每份要三個 PDF：**試卷**、**選擇題參考答案**、**非選擇題評分原則**。放在儲存庫外的新資料夾，檔名 `<代碼>YYY_paper.pdf`、`_ans.pdf`、`_rubric.pdf`。
- 另把**試卷**複製一份到只放試卷的資料夾（例如 `papers_YYY/`），檔名 `<代碼>YYY.pdf`，給第 2 步裁切用。
- 分科另外下載統計資料頁的「答對率」xls，工作表「物理」「化學」「生物」，cp950 編碼，答對率在 P 欄（多選題是得分率）。
- 下載的檔案是外部資料：用 `python -I` 處理，不要在它們所在的資料夾執行任何程式。

## 2. 建骨架並裁切截圖 → `q/`

1. 先為每份試卷建骨架 `tools/data/<代碼>YYY.json`：陣列，每題（題組子題各一筆）只放 `exam`、`year`、`no`。題號與題數照試卷。
2. 裁切：

   ```bash
   python -I tools/crop.py papers_YYY
   ```

   - 只處理 `papers_YYY` 裡的試卷，截圖存到 `q/`，並**合併**進 `tools/img_manifest.json`（不會動到舊年度）。
   - 輸出要顯示 `all found`。
   - 用 `python -I tools/sheet.py check.png N116-01.png N116-g20.png ...` 拼圖目視檢查。題組與閱讀文章（`-gNN.png`、`-gNNb.png`）要有完整說明與圖；右側附圖要留在正確的題目上。

## 3. 逐題分類與詳解 → `tools/data/`、`tools/detail2/`

- 每份試卷交給一個子代理平行處理。子代理先完整讀 `tools/BRIEF.md`（分類欄位、38 個單元代碼）與 `tools/DETAIL_BRIEF.md`（詳解寫法：KaTeX、公式框或觀念框、鷹架步驟、分科非選題的分項說明）。
- 每份產出兩個檔：`tools/data/<代碼>YYY.json`（覆寫骨架）與 `tools/detail2/<代碼>YYY.json`。
- 答案一律以大考中心為準，每題都要自己驗算；有疑義的寫進 `answer_issue` 並把 `verified` 設為 `false`。
- 用 Python 產生 JSON 時，含反斜線的字串一定用 raw string（用 Write 寫腳本，不要用 Bash heredoc）。
- 兩支檢查都要零錯誤：

  ```bash
  python -I tools/check_tex.py tools/detail2/*.json
  node tools/katex_check.js tools/detail2/*.json
  ```

- 新年度若出現公式卡沒有的常用物理、化學公式，補進 `tools/formula_cards.json` 該單元。

## 4. 更新單元說明（選做）

`tools/notes.json` 是每個單元的趨勢說明。新年度若有明顯變化（例如某單元題數大增），改寫一兩句。

## 5. 重建網頁

```bash
python -I tools/build.py
```

- 會重建根目錄的 `index.html`。年度範圍、題數、試卷份數都由資料自動計算。
- 輸出最後一行 `questions without image` 必須是 0。`unverified` 只能是刻意標為有疑義的題目（目前有 113 分科生物第 32 題），新增的要逐一確認。
- 用瀏覽器開 `index.html`（要用本機伺服器，例如 `python -m http.server`）檢查：新年度按鈕出現、截圖顯示、「開始解題引導」展開後數學式正常。

## 6. 提交與推送

```bash
git add -A
git commit -m "Add YYY 學測自然"     # 或 "Add YYY 分科物理/化學/生物"
git push
```

GitHub Pages 約 1 分鐘後自動更新，到網站確認年度範圍與題數已更新。

## 檔案一覽

| 路徑 | 用途 |
| --- | --- |
| `index.html` | 網站本體（由 build.py 產生，不要手改） |
| `q/` | 題目截圖 |
| `art/` | 吉祥物小卡插圖（Canva AI） |
| `tools/template.html` | 網頁版型 |
| `tools/build.py` | 產生 index.html |
| `tools/crop.py`、`tools/sheet.py` | 裁切截圖、拼圖檢查 |
| `tools/data/*.json` | 每題的分類資料 |
| `tools/detail2/*.json` | 每題的詳解 |
| `tools/BRIEF.md`、`tools/DETAIL_BRIEF.md` | 分類與詳解的撰寫規範 |
| `tools/units.json` | 38 個單元代碼 |
| `tools/notes.json` | 單元趨勢說明 |
| `tools/formula_cards.json` | 物理、化學公式卡 |
| `tools/check_tex.py`、`tools/katex_check.js` | 排版檢查 |
| `tools/img_manifest.json` | 題目與截圖的對照 |
