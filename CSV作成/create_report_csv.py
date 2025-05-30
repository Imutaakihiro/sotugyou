# 講義の要約CSVの作成
import csv
import re
from collections import OrderedDict
import os
import glob

# 2025フォルダ内のすべてのCSVファイルを取得
csv_files = glob.glob("2025/*.csv")

for input_file in csv_files:
    # ファイル名から出力ファイル名を生成
    base_name = os.path.basename(input_file)
    output_csv = f"lecture_summary_{base_name}"
    lectures = OrderedDict()

    print(f"\n{input_file} を処理中...")

    with open(input_file, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        for row in reader:
            if len(row) < 4:
                continue
            first_col, _, name, avg, *_ = row
            name = name.strip()
            if not name or "該当授業はありません" in name:
                continue
            # 回答人数の抽出（例: "47人" → 47）
            n = None
            m_n = re.match(r'(\d+)人', first_col.strip())
            if m_n:
                n = int(m_n.group(1))
            # 履修者数の抽出（例: "履修者：　52人" → 52）
            enrolled = None
            m_enrolled = re.search(r'履修者：\s*([\d]+)人', first_col)
            if m_enrolled:
                enrolled = int(m_enrolled.group(1))
            # 平均評価ポイントの抽出
            m_avg = re.search(r'([0-9]+\.[0-9]+)', avg)
            avg_point = float(m_avg.group(1)) if m_avg else None
            
            # コメントの有無を確認（空でないコメントがあるか）
            has_comment = any(cell.strip() for cell in row[4:] if cell.strip())
            
            # まだ登録されていなければ記録
            if name not in lectures:
                lectures[name] = {
                    "人数": n, 
                    "履修者": enrolled, 
                    "平均評価": avg_point,
                    "コメント数": 1 if has_comment else 0
                }
            else:
                # 既に登録されている場合はコメント数を加算
                if has_comment:
                    lectures[name]["コメント数"] += 1

    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["講義名", "回答人数", "履修者数", "平均評価", "コメント数"])
        for name, info in lectures.items():
            writer.writerow([
                name,
                info['人数'] if info['人数'] is not None else '',
                info['履修者'] if info['履修者'] is not None else '',
                info['平均評価'] if info['平均評価'] is not None else '',
                info['コメント数']
            ])

    print(f"{output_csv} に出力しました。")

print("\nすべてのファイルの処理が完了しました！") 