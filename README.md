# pyradio_stations
pyradio stations in China

## 简介

`pyradio_stations` 是一个 Python 脚本，用于从指定的 API 获取在线电台信息，并将这些信息保存到 CSV 文件中。该脚本旨在从 `https://cn.tingfm.com` 获取电台数据，并支持缓存、批处理和重试机制，以提高效率和稳定性。

## 功能

*   从指定的 API 获取电台信息。
*   将获取到的电台信息保存到 CSV 文件中。
*   使用缓存来避免重复请求。
*   实现批处理，减少文件 I/O 操作。
*   提供重试机制，增强程序的健壮性。
*   可选的进度条，方便用户了解程序运行状态。

## 依赖

*   Python 3.x
*   `requests`:  用于发送 HTTP 请求
*   `csv`:  用于读写 CSV 文件 (Python 内置)
*   `time`:  用于添加延时和重试 (Python 内置)
*   `json`:  用于处理 JSON 数据 (Python 内置)
*   `os`:  用于文件操作 (Python 内置)
*   `tqdm`:  可选的，用于显示进度条

## 安装

### Python 安装

如果您尚未安装 Python，请根据您的操作系统，按照以下步骤安装：

*   **Windows**: 访问 [Python 官网](https://www.python.org/downloads/windows/) 下载 Python 安装程序，并确保在安装过程中勾选 "Add Python to PATH" 选项。
*   **macOS**:  macOS 通常预装了 Python 2.7，但建议安装 Python 3.x。  您可以从 [Python 官网](https://www.python.org/downloads/macos/) 下载 Python 安装程序。 另外，可以使用 Homebrew: `brew install python3`
*   **Linux**: 大多数 Linux 发行版都预装了 Python。如果未安装，可以使用包管理器进行安装。例如，在 Ubuntu 上：`sudo apt update && sudo apt install python3`

### 依赖安装 (使用 `requirements.txt` 和 venv)

1.  **创建虚拟环境 (推荐)**:  创建一个虚拟环境以隔离项目依赖项。在项目根目录下打开终端，并运行以下命令：

    ```bash
    python -m venv venv  # 在项目目录下创建一个名为 "venv" 的虚拟环境
    ```

2.  **激活虚拟环境**:
    *   **Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS / Linux**:
        ```bash
        source venv/bin/activate
        ```
    您应该会在终端提示符前面看到 `(venv)`，表示虚拟环境已激活。

3.  **安装依赖**: 使用 `requirements.txt` 文件安装所有依赖项。确保您已经在项目根目录下，并且虚拟环境已激活。

    ```bash
    pip install -r requirements.txt
    ```

    `requirements.txt` 文件内容如下：

    ```text
    requests
    tqdm
    ```

## 使用方法

1.  **确保已安装 Python 和所有依赖项** (通过上述步骤)。
2.  **运行脚本**: 在项目根目录下打开终端，并确保虚拟环境已激活。然后运行:

    ```bash
    python fetch_stations.py
    ```

    脚本将在运行时从 API 获取电台信息，并将结果保存到 `OUTPUT_CSV_FILE` 中。同时，它会使用 `CACHE_FILE` 来缓存已经获取的数据，以提高效率。

3.  **直接使用下载的 stations.csv**:
    *   脚本运行后，会在当前目录下生成 `stations.csv` 文件，其中包含了获取到的电台信息。
    *   **可以直接将该 CSV 文件用于 [PyRadio](https://github.com/coderholic/pyradio.git) 项目**:  PyRadio 是一个 Python 编写的命令行电台播放器。 你只需要将生成的 `stations.csv` 文件复制到 PyRadio 的配置文件目录中，或者在 PyRadio 中配置 CSV 文件的路径，就可以直接播放这些电台。  具体配置方法，请参考 PyRadio 的官方文档。

4.  **自定义配置**:
    你可以通过修改脚本中的配置变量来调整程序的行为，例如，更改 `START_ID` 和 `END_ID` 来指定要获取的电台范围。

## 代码结构

*   `load_cache()`: 从文件加载缓存。
*   `save_cache(cache)`: 将缓存保存到文件。
*   `append_to_csv(stations_batch)`: 将一批电台信息追加到 CSV 文件。
*   `flush_batch(batch, cache, count)`: 执行批处理，写入 CSV、保存缓存、清空批次。
*   `main()`: 主函数，循环获取电台数据并分批写入。
*   `if __name__ == "__main__":`: 程序入口，调用 `main()` 函数。

## TODO

*   **错误处理**: 增加更具体的错误处理，例如，针对不同的 HTTP 状态码采取不同的处理方式。
*   **配置**: 将配置信息提取到单独的配置文件中，以提高配置的灵活性。
*   **日志**: 添加日志记录，方便调试和监控程序的运行情况。
*   **并发**: 考虑使用多线程或异步操作来并发地获取电台信息，以提高效率。

##  许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
