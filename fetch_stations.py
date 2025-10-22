import requests
import csv
import time
import json
import os

# 尝试导入 tqdm
try:
    from tqdm import tqdm
except ImportError:
    print("提示：安装 'tqdm' 库可以显示进度条 (pip install tqdm)")
    def tqdm(iterable, **kwargs):
        return iterable

# --- 配置 ---
BASE_URL = "https://cn.tingfm.com/wp-json/query/wndt_streams"
OUTPUT_CSV_FILE = "stations.csv"
CACHE_FILE = "cache.json"
START_ID = 1
END_ID = 1292

# --- 流量控制配置 ---
REQUEST_DELAY_SECONDS = 0.5
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3

# --- 批处理配置 ---
# 每积累多少条新数据后，就写入一次文件和缓存
BATCH_SIZE = 50

def load_cache():
    """从文件加载缓存"""
    if os.path.exists(CACHE_FILE):
        print(f"正在从 {CACHE_FILE} 加载缓存...")
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告：加载缓存文件失败 ({e})，将从头开始。")
            return {}
    print("未找到缓存文件，将从头开始。")
    return {}

def save_cache(cache):
    """将缓存字典保存到文件"""
    # 这个函数现在只负责保存，不再打印太多信息，由调用者控制
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"错误：保存缓存文件失败 ({e}")

def append_to_csv(stations_batch):
    """
    将一批数据追加到CSV文件中。
    如果文件不存在，会先创建并写入表头。
    """
    if not stations_batch:
        return

    file_exists = os.path.isfile(OUTPUT_CSV_FILE)
    try:
        # 使用 'a' 模式进行追加
        with open(OUTPUT_CSV_FILE, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                # 如果文件不存在，先写入表头
                writer.writerow(['# PyRadio Playlist File - Format:,,,,,,,,,'])
                writer.writerow(['# name,url,encoding,icon,profile,buffering,force-http,volume,referer,player'])
            writer.writerows(stations_batch)
        print(f"  [批处理] 已将 {len(stations_batch)} 条新记录追加到 {OUTPUT_CSV_FILE}")
    except IOError as e:
        print(f"错误：追加写入文件 {OUTPUT_CSV_FILE} 失败: {e}")

def flush_batch(batch, cache, count):
    """
    执行批处理：写入CSV、保存缓存、清空批次。
    """
    print(f"\n[批处理] 已积累 {count} 条新数据，开始写入文件和更新缓存...")
    append_to_csv(batch)
    save_cache(cache)
    print("[批处理] 批处理完成。")
    # 返回清空后的批次和计数器
    return [], 0

def main():
    """主函数，循环获取电台数据并分批写入。"""
    cache = load_cache()

    # 用于暂存本批次要写入的数据
    current_batch = []
    new_entries_count = 0

    print(f"--- 流量控制配置 ---")
    print(f"请求延迟: {REQUEST_DELAY_SECONDS} 秒/次")
    print(f"最大重试次数: {MAX_RETRIES}")
    print(f"--- 批处理配置 ---")
    print(f"批处理大小: {BATCH_SIZE} 条/次")
    print(f"----------------------")
    print(f"开始获取数据，post_id 范围：{START_ID} 到 {END_ID}...")

    post_ids_to_process = range(START_ID, END_ID + 1)
    for post_id in tqdm(post_ids_to_process, desc="获取进度"):
        station_info = None
        # 1. 检查缓存
        if str(post_id) in cache:
            data = cache[str(post_id)]
            if data.get('status') == 1 and not data.get('msg'):
                payload = data.get('data', {})
                title = payload.get('title')
                streams = payload.get('streams', [])
                if isinstance(streams, list):
                    for stream in streams:
                        if stream.get('type') == 'm3u8' and stream.get('url'):
                            station_info = (title, stream.get('url'))
                            break # 找到后即可跳出

        else:
            # 2. 带重试机制的网络请求
            for attempt in range(MAX_RETRIES):
                try:
                    params = {'post_id': post_id}
                    response = requests.get(BASE_URL, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    cache[str(post_id)] = data # 立即更新缓存

                    if data.get('status') == 1 and not data.get('msg'):
                        payload = data.get('data', {})
                        title = payload.get('title')
                        streams = payload.get('streams', [])
                        if isinstance(streams, list):
                            for stream in streams:
                                if stream.get('type') == 'm3u8' and stream.get('url'):
                                    station_info = (title, stream.get('url'))
                                    print(f"\n[成功] post_id: {post_id}, 找到电台: {title}")
                                    break
                    break # 成功后跳出重试循环

                except requests.exceptions.RequestException as e:
                    print(f"\n[错误] 请求 post_id {post_id} 失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY_SECONDS)
                    else:
                        print(f"  [放弃] post_id {post_id} 在多次重试后仍然失败。")

        # 3. 如果找到了有效电台信息，则加入当前批次
        if station_info:
            current_batch.append(station_info)
            new_entries_count += 1

        # 4. 检查是否达到批处理阈值
        if new_entries_count >= BATCH_SIZE:
            current_batch, new_entries_count = flush_batch(current_batch, cache, new_entries_count)

        # 5. 在每次循环后都进行延迟
        time.sleep(REQUEST_DELAY_SECONDS)

    # --- 所有循环结束后，处理剩余数据 ---
    if current_batch:
        print(f"\n[最终处理] 循环结束，但仍有 {len(current_batch)} 条数据待写入...")
        flush_batch(current_batch, cache, len(current_batch))
    else:
        print("\n[最终处理] 没有剩余数据需要写入。")
        # 即使没有新数据，也保存一次最终的缓存状态
        save_cache(cache)

    print("\n所有任务完成！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断。")
    except Exception as e:
        print(f"\n发生未知错误: {e}")
