import ctypes
import os

MAP_SIZE = 5

# 載入你剛才編譯好的 dll
dll_path = os.path.join(os.path.dirname(__file__), "map_generator.dll")
lib = ctypes.CDLL(dll_path)

# 設定 C 函式的參數類型 (全部都是整數指針)
lib.generate_map_data.argtypes = [
    ctypes.POINTER(ctypes.c_int), # out_map
    ctypes.POINTER(ctypes.c_int), # out_start
    ctypes.POINTER(ctypes.c_int), # out_end
    ctypes.POINTER(ctypes.c_int), # out_path_x
    ctypes.POINTER(ctypes.c_int), # out_path_y
    ctypes.POINTER(ctypes.c_int)  # out_path_count
]

def generate_strict_path():
    """封裝 C 語言的導出，讓 main.py 呼叫時感覺跟純 Python 版完全一模一樣"""
    # 建立 ctypes 專用的記憶體緩衝區
    c_map = (ctypes.c_int * (MAP_SIZE * MAP_SIZE))()
    c_start = (ctypes.c_int * 2)()
    c_end = (ctypes.c_int * 2)()
    c_path_x = (ctypes.c_int * 100)()
    c_path_y = (ctypes.c_int * 100)()
    c_count = ctypes.c_int(0)
    
    # 呼叫 C 語言高速生成地圖，直接寫入緩衝區
    lib.generate_map_data(c_map, c_start, c_end, c_path_x, c_path_y, ctypes.byref(c_count))
    
    # 將 ctypes 的資料轉換回 Python 原生的資料格式
    dungeon_map = [[c_map[y * MAP_SIZE + x] for x in range(MAP_SIZE)] for y in range(MAP_SIZE)]
    start_pos = (c_start[0], c_start[1])
    end_pos = (c_end[0], c_end[1])
    
    full_path = []
    for i in range(c_count.value):
        full_path.append((c_path_x[i], c_path_y[i]))
        
    return dungeon_map, start_pos, end_pos, full_path