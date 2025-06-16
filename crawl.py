import os
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
import random


def extract_urls(file_path):
    """从文本文件中提取所有URL"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则表达式提取URL
    url_pattern = r'https?://[^\s)"]+'
    urls = re.findall(url_pattern, content)

    # 过滤掉非docs.temporal.io的链接，因为我们主要关注文档链接
    filtered_urls = [url for url in urls if 'docs.temporal.io' in url]

    return filtered_urls


def parse_url(url):
    """解析URL，提取路径和锚点"""
    parsed = urlparse(url)
    path = parsed.path
    fragment = parsed.fragment

    # 如果路径以/结尾，去掉它
    if path.endswith('/'):
        path = path[:-1]

    return path, fragment


def create_directory_structure(base_dir, path):
    """创建目录结构"""
    # 去掉开头的斜杠
    if path.startswith('/'):
        path = path[1:]

    # 创建完整路径
    full_path = os.path.join(base_dir, path)
    directory = os.path.dirname(full_path)

    # 确保目录存在
    os.makedirs(directory, exist_ok=True)

    return full_path


def download_page(url, output_path):
    """下载页面并保存到本地"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 添加随机延迟以避免被封
        time.sleep(random.uniform(1, 3))

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 保存HTML到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        print(f"成功下载: {url} -> {output_path}")
        return True
    except Exception as e:
        print(f"下载失败: {url}, 错误: {e}")
        return False


def process_urls(urls, base_dir):
    """处理所有URL，下载并保存到正确的目录结构中"""
    # 创建基础目录
    os.makedirs(base_dir, exist_ok=True)

    # 跟踪已处理的页面，避免重复下载
    processed_pages = set()

    for url in urls:
        path, fragment = parse_url(url)

        # 确定文件名
        if path.endswith('/'):
            path = path[:-1]

        # 从路径中提取文件名
        file_name = os.path.basename(path)

        # 如果文件名为空，使用index.html
        if not file_name:
            file_name = "index"

        # 创建目录结构
        directory_path = os.path.dirname(path)
        full_dir_path = os.path.join(base_dir, directory_path.lstrip('/'))
        os.makedirs(full_dir_path, exist_ok=True)

        # 完整的输出路径
        output_path = os.path.join(full_dir_path, f"{file_name}.html")

        # 如果页面已经处理过，跳过
        page_key = (path, file_name)
        if page_key in processed_pages:
            print(f"跳过已处理的页面: {url}")
            continue

        # 下载页面
        success = download_page(url.split('#')[0], output_path)
        if success:
            processed_pages.add(page_key)


def main():
    """主函数"""
    input_file = 'temporal/llms.txt'
    base_dir = 'temporal_docs'

    # 提取URL
    urls = extract_urls(input_file)
    print(f"从 {input_file} 中提取了 {len(urls)} 个URL")

    # 处理URL
    process_urls(urls, base_dir)

    print("完成！所有页面已下载到本地。")


if __name__ == "__main__":
    main()
