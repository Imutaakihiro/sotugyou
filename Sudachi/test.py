from sudachipy import tokenizer
from sudachipy import dictionary
from collections import defaultdict
import pandas as pd

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

# 感情辞書の読み込み
pn_dict = load_pn_table()

if pn_dict:
    # テストケース
    test_texts = [
        "嬉しいです",
        "悲しいです",
        "楽しいです",
        "辛いです",
        "カレーが最高で、絶品でした！また来たいです",
        "この料理は本当に美味しくて感動しました",
        "今日は疲れたけど、楽しかったです"
    ]

    # 各文章を分析
    for i, text in enumerate(test_texts, 1):
        print(f"\nテスト{i}:")
        print(f"文章: {text}")
        score, found_words = analyze_sentiment(text, pn_dict)
        print(f"感情スコア: {score:.2f}")
        print("検出された感情表現:")
        for sentiment, words in found_words.items():
            if words:
                print(f"- {sentiment}: {', '.join(words)}")
        print("-" * 50)