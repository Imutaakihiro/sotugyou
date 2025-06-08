# 単語感情極値対応表を用いた感情分析
from sudachipy import tokenizer
from sudachipy import dictionary
from collections import defaultdict
import pandas as pd
import os
import glob
import re
from datetime import datetime

# Sudachiの初期化
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C

# 感情値辞書の読み込み
def load_pn_table():
    try:
        pndic = pd.read_csv("http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic",
                           encoding="shift-jis",
                           names=['word_type_score'])
        
        # 辞書の初期化
        pn_dict = defaultdict(float)
        
        # データフレームを辞書に変換
        for _, row in pndic.iterrows():
            parts = row['word_type_score'].split(':')
            if len(parts) >= 2:
                word = parts[0]
                score = float(parts[3]) if len(parts) > 3 and parts[3] != "0" else 0.0
                pn_dict[word] = score
        
        print(f"感情辞書の読み込み完了: {len(pn_dict)}語")
        return pn_dict
    except Exception as e:
        print(f"感情辞書の読み込みに失敗: {e}")
        return None

def analyze_sentiment(text, pn_dict):
    # 形態素解析
    tokens = tokenizer_obj.tokenize(text, mode)
    
    # 感情スコアの計算
    total_score = 0
    found_words = defaultdict(list)
    
    for token in tokens:
        word = token.surface()
        if word in pn_dict:
            score = pn_dict[word]
            total_score += score
            if score > 0:
                found_words["positive"].append(f"{word}({score:.2f})")
            elif score < 0:
                found_words["negative"].append(f"{word}({score:.2f})")
    
    # スコアの正規化（-1から1の範囲に）
    if len(tokens) > 0:
        total_score = total_score / len(tokens)
    
    return total_score, found_words

def extract_text(text):
    # 日付情報を除外（YYYY/MM/DD（曜日）のパターン）
    date_pattern = r'\d{4}/\d{2}/\d{2}（[月火水木金土日]）'
    text = re.sub(date_pattern, '', text)
    
    # 日付範囲のパターン（～で区切られた日付）
    date_range_pattern = r'～\s*\d{4}/\d{2}/\d{2}（[月火水木金土日]）'
    text = re.sub(date_range_pattern, '', text)
    
    # 余分な空白を削除
    text = text.strip()
    
    # スラッシュで区切られた部分を取得（最後の部分が自由記述）
    parts = text.split('/')
    if len(parts) > 1:
        return parts[-1].strip()
    return text

def process_csv_file(file_path, pn_dict):
    try:
        # CSVファイルから文章を読み込み
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # ファイル名を取得
        file_name = os.path.basename(file_path)
        print(f"\n=== ファイル: {file_name} の分析 ===")
        
        # 分析結果を格納するリスト
        results = []
        
        # 各文章を分析
        for i, row in df.iterrows():
            text = row['自由記述']
            # 日付情報を除外して純粋なテキストを取得
            clean_text = extract_text(text)
            
            if clean_text:  # 空でない場合のみ分析
                print(f"\nテスト{i+1}:")
                print(f"文章: {clean_text}")
                score, found_words = analyze_sentiment(clean_text, pn_dict)
                print(f"感情スコア: {score:.2f}")
                print("検出された感情表現:")
                for sentiment, words in found_words.items():
                    if words:
                        print(f"- {sentiment}: {', '.join(words)}")
                print("-" * 50)
                
                # 結果をリストに追加
                results.append({
                    '講義名': row['講義名'],
                    '平均評価ポイント': row['平均評価ポイント'],
                    '自由記述': clean_text,
                    '感情スコア': score,
                    'ポジティブ表現': ', '.join(found_words['positive']),
                    'ネガティブ表現': ', '.join(found_words['negative'])
                })
        
        # 結果をDataFrameに変換
        results_df = pd.DataFrame(results)
        
        # 出力ディレクトリの作成
        output_dir = os.path.join(os.path.dirname(file_path), 'analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        # 出力ファイル名を生成
        output_file = os.path.join(output_dir, os.path.splitext(file_name)[0] + '_analysis.csv')
        
        # CSVファイルに出力
        results_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n分析結果を {output_file} に保存しました。")
            
    except Exception as e:
        print(f"ファイル {file_path} の処理中にエラーが発生: {e}")

# メイン処理
if __name__ == "__main__":
    # 感情辞書の読み込み
    pn_dict = load_pn_table()
    
    if pn_dict:
        # 指定されたディレクトリ内のCSVファイルを処理
        target_dir = r"C:\Users\takahashi.DESKTOP-U0T5SUB\Downloads\藺牟田＿卒論\data\raw\2025"
        csv_files = glob.glob(os.path.join(target_dir, "*.csv"))
        
        if not csv_files:
            print("CSVファイルが見つかりません。")
        else:
            print(f"処理対象のCSVファイル: {len(csv_files)}個")
            for csv_file in csv_files:
                process_csv_file(csv_file, pn_dict)