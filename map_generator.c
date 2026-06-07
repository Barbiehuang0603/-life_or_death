#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAP_SIZE 5

typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    int count;
    Point* points;
} Path;

// 計算路徑中的轉彎次數
int count_turns(Path* path) {
    if (path->count < 3) return 0;
    
    int turns = 0;
    for (int i = 1; i < path->count - 1; i++) {
        int dir1_x = path->points[i].x - path->points[i-1].x;
        int dir1_y = path->points[i].y - path->points[i-1].y;
        int dir2_x = path->points[i+1].x - path->points[i].x;
        int dir2_y = path->points[i+1].y - path->points[i].y;
        
        if (dir1_x != dir2_x || dir1_y != dir2_y) {
            turns++;
        }
    }
    return turns;
}

// 核心演算法：生成絕對無捷徑、唯一通路的單向軌道
Path* generate_strict_path() {
    static int seeded = 0;
    if (!seeded) {
        srand((unsigned int)time(NULL));
        seeded = 1;
    }
    
    while (1) {
        int start_x, start_y;
        int border_idx = rand() % 16; 
        if (border_idx < 5) {          
            start_x = border_idx; start_y = 0;
        } else if (border_idx < 10) {   
            start_x = border_idx - 5; start_y = MAP_SIZE - 1;
        } else if (border_idx < 13) {   
            start_x = 0; start_y = border_idx - 9;
        } else {                        
            start_x = MAP_SIZE - 1; start_y = border_idx - 12;
        }
        
        Path* path = (Path*)malloc(sizeof(Path));
        path->points = (Point*)malloc(sizeof(Point) * 100);
        path->count = 0;
        
        int* visited = (int*)malloc(sizeof(int) * MAP_SIZE * MAP_SIZE);
        memset(visited, 0, sizeof(int) * MAP_SIZE * MAP_SIZE);
        
        path->points[0].x = start_x;
        path->points[0].y = start_y;
        path->count = 1;
        visited[start_y * MAP_SIZE + start_x] = 1;
        
        int curr_x = start_x;
        int curr_y = start_y;
        int stuck = 0;
        
        int target_length = 7 + rand() % 4; 
        
        // 🌟 ✅ 修正 1：將條件改為 step <= target_length，確保走滿完整的總步數，與 Python 完美對齊！
        for (int step = 1; step <= target_length; step++) {
            Point possible_moves[4];
            int move_count = 0;
            
            int dx_list[] = {-1, 1, 0, 0};
            int dy_list[] = {0, 0, -1, 1};
            
            for (int d = 0; d < 4; d++) {
                int nx = curr_x + dx_list[d];
                int ny = curr_y + dy_list[d];
                
                if (nx >= 0 && nx < MAP_SIZE && ny >= 0 && ny < MAP_SIZE && !visited[ny * MAP_SIZE + nx]) {
                    int adjacent_path_count = 0;
                    for (int a = 0; a < 4; a++) {
                        int ax = nx + dx_list[a];
                        int ay = ny + dy_list[a];
                        if (ax >= 0 && ax < MAP_SIZE && ay >= 0 && ay < MAP_SIZE) {
                            if (visited[ay * MAP_SIZE + ax]) {
                                adjacent_path_count++;
                            }
                        }
                    }
                    
                    if (adjacent_path_count <= 1) {
                        possible_moves[move_count].x = nx;
                        possible_moves[move_count].y = ny;
                        move_count++;
                    }
                }
            }
            
            if (move_count == 0) {
                stuck = 1;
                free(visited);
                free(path->points);
                free(path);
                break;
            }
            
            int chosen = rand() % move_count;
            curr_x = possible_moves[chosen].x;
            curr_y = possible_moves[chosen].y;
            path->points[path->count].x = curr_x;
            path->points[path->count].y = curr_y;
            path->count++;
            visited[curr_y * MAP_SIZE + curr_x] = 1;
        }
        
        if (stuck) continue; 
        
        free(visited);

        if (count_turns(path) < 3) {
            free(path->points);
            free(path);
            continue; 
        }

        return path; 
    }
}

// 🌟 ✅ 修正 2：重構 Python 呼叫接口，改用指針安全寫入，保證起終點路徑 100% 同步
__declspec(dllexport) void generate_map_data(int* out_map, int* out_start, int* out_end, int* out_path_x, int* out_path_y, int* out_path_count) {
    Path* path = generate_strict_path();
    
    // 1. 清空傳進來的地圖陣列
    memset(out_map, 0, sizeof(int) * MAP_SIZE * MAP_SIZE);
    
    // 2. 填入起點與終點座標
    out_start[0] = path->points[0].x;
    out_start[1] = path->points[0].y;
    out_end[0] = path->points[path->count - 1].x;
    out_end[1] = path->points[path->count - 1].y;
    
    // 3. 填入整條 full_path 的點與長度，並渲染二維地圖
    *out_path_count = path->count;
    for (int i = 0; i < path->count; i++) {
        int x = path->points[i].x;
        int y = path->points[i].y;
        
        out_map[y * MAP_SIZE + x] = 1; // 畫二維通路
        out_path_x[i] = x;             // 紀錄路徑順序
        out_path_y[i] = y;
    }
    
    // 4. 安全釋放 C 內部暫存
    free(path->points);
    free(path);
}