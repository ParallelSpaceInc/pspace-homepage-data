#!/usr/bin/env python3
"""index.html 파일을 생성하는 스크립트"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))


def create_index_html():
    """nginx 스타일의 간단한 파일 리스트를 생성합니다."""
    
    # data 폴더의 JSON 파일들 스캔
    data_path = Path("data")
    json_files = []
    
    if data_path.exists():
        json_files = [f.name for f in data_path.glob("*.json")]
        json_files.sort()
    
    # 파일 크기 정보 가져오기
    file_info = []
    for filename in json_files:
        file_path = data_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            if size > 1024:
                size_str = f"{size//1024}K"
            else:
                size_str = f"{size}B"
            
            modified = datetime.fromtimestamp(file_path.stat().st_mtime, KST)
            file_info.append({
                'name': filename,
                'size': size_str,
                'modified': modified.strftime("%Y-%m-%d %H:%M")
            })
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Index of /</title>
    <style>
        body {{
            font-family: monospace;
            margin: 2rem;
            background: #fafafa;
        }}
        h1 {{
            font-size: 1.2rem;
            margin-bottom: 1rem;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background: white;
        }}
        th, td {{
            text-align: left;
            padding: 0.5rem 1rem;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f5f5f5;
            font-weight: bold;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .size {{
            text-align: right;
            width: 80px;
        }}
        .date {{
            width: 150px;
        }}
        .footer {{
            margin-top: 2rem;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>Index of /</h1>
    
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th class="size">Size</th>
                <th class="date">Last Modified</th>
            </tr>
        </thead>
        <tbody>"""
    
    # 파일 목록 추가
    for file in file_info:
        html_content += f"""
            <tr>
                <td><a href="{file['name']}">{file['name']}</a></td>
                <td class="size">{file['size']}</td>
                <td class="date">{file['modified']}</td>
            </tr>"""
    
    html_content += f"""
        </tbody>
    </table>
    
    <div class="footer">
        Generated at {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}
    </div>
</body>
</html>"""

    # data 폴더에 index.html 저장
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)

    with open(data_path / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("index.html created successfully")


if __name__ == "__main__":
    create_index_html()
