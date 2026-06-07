# C 編譯指南 - map_generator.c

## 📋 需求

在 Windows 上編譯 map_generator.c 為 DLL

### 選項 1：使用 Visual Studio (推薦)

#### 步驟 1: 開啟 Visual Studio Command Prompt

按 Windows + X，搜尋 "x64 Native Tools Command Prompt for VS"

#### 步驟 2: 切換到專案目錄

```batch
cd C:\Barbie\computerprogramming\project\-life_or_death
```

#### 步驟 3: 編譯

```batch
cl /LD map_generator.c /Fe:map_generator.dll
```

- `/LD` = 編譯為 DLL
- `/Fe:` = 指定輸出檔名

✅ 成功後會產生 `map_generator.dll`

---

### 選項 2：使用 MinGW (如果已安裝)

```bash
gcc -shared -o map_generator.dll map_generator.c -fPIC
```

---

### 選項 3：使用線上編譯器（快速驗證）

1. 上傳 map_generator.c 到 [compile.run](https://compile.run) 或 [TutorialsPoint C Compiler](https://www.tutorialspoint.com/compile_c_online.php)
2. 改為 Linux 平台，編譯為 `.so`
3. 使用 Python 的 `ctypes` 搭配 `.so` 檔

---

## ✅ 驗證編譯

編譯完成後，在 Python 中測試：

```python
from map_generator_wrapper import generate_strict_path

dungeon_map, start_pos, end_pos, full_path = generate_strict_path()
print("✓ C 版本成功運作！")
```

---

## ⚠️ 如果編譯失敗

此時 wrapper 會自動降級到 Python 實現，遊戲仍能正常運作。

```python
# map_generator_wrapper.py 會自動檢測：
if HAS_C_LIB:
    return _generate_from_c()
else:
    return _generate_from_python()  # 自動降級
```

---

## 📝 檔案結構

```
-life_or_death/
├── main.py                      # ✅ 合併版（整合兩人功能）
├── map_generator.c              # ✅ C 版本迷宮生成
├── map_generator.dll            # 需編譯產生
├── map_generator_wrapper.py     # Python wrapper
├── map_generator.py             # 舊版（保留備用）
├── main_vicky.py                # 舊版（保留備用）
├── systems/
│   └── room.py
├── assets/
│   └── room/
└── ...
```

---

## 🎮 執行遊戲

```bash
python main.py
```

### 控制鍵

- **LEFT/RIGHT** - 轉向左/右
- **UP** - 前進/開門
- **ESC** - 退出

---

## 📚 技術細節

### map_generator.c

- 用 C 實現迷宮生成算法
- 導出 `generate_map()` 函數
- 回傳 `int*` 陣列（MAP_SIZE × MAP_SIZE）

### map_generator_wrapper.py

- 用 `ctypes` 動態載入 DLL
- 自動 fallback 到 Python 版本
- 保持相同的 API 介面

### main.py

整合功能：
- ✅ Vicky 的房間系統、動畫、計時器
- ✅ 用戶的終端上帝視角顯示
- ✅ C 版本的迷宮生成器
- ✅ 統一的遊戲流程

---

## 🚀 下一步

1. 按照上面的步驟編譯 `map_generator.c`
2. 執行 `python main.py` 測試
3. 提交到 GitHub

