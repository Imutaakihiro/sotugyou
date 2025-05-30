# 講義名，平均評価ポイント，自由記述の抽出
import csv
import os
import glob

# 2025フォルダ内のすべてのCSVファイルを取得
csv_files = glob.glob("2025 raw/*.csv")

for input_file in csv_files:
    base_name = os.path.basename(input_file)
    output_csv = f"extracted_{base_name}"

    print(f"\n{input_file} を処理中...")

    with open(input_file, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)  # ヘッダーをスキップ

        extracted_rows = []
        for row in reader:
            if len(row) < 4:
                continue
            name = row[2].strip()
            avg = row[3].strip()
            # 5列目以降をすべて連結（空欄は除外）
            comments = [cell.strip() for cell in row[4:] if cell.strip()]
            comment_text = " / ".join(comments)
            # 講義名が空、または「該当授業はありません」は除外
            if not name or "該当授業はありません" in name:
                continueS
            extracted_rows.append([name, avg, comment_text])

    # 新しいCSVに書き出し
    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["講義名", "平均評価ポイント", "自由記述"])
        writer.writerows(extracted_rows)

    print(f"{output_csv} に出力しました。")

print("\nすべてのファイルの処理が完了しました！") 