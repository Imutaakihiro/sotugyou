# Sudachiを使用した感情分析システム実装マニュアル

## 目次
1. [はじめに](#はじめに)
2. [環境構築](#環境構築)
3. [システムの構成](#システムの構成)
4. [実装手順](#実装手順)
5. [使用方法](#使用方法)
6. [トラブルシューティング](#トラブルシューティング)

## はじめに

このマニュアルでは、Sudachiを使用した日本語テキストの感情分析システムの実装方法について説明します。
このシステムは、講義評価の自由記述文から感情を分析し、ポジティブ/ネガティブな表現を抽出します。

### 主な機能
- 日本語テキストの形態素解析
- 感情スコアの計算
- ポジティブ/ネガティブ表現の抽出
- CSVファイルの一括処理

## 環境構築

### 必要なパッケージ
以下のパッケージをインストールします：

```bash
pip install sudachipy==0.6.7
pip install sudachidict_core==20230927
pip install pandas
```

### 感情辞書の準備
高村大也氏の日本語評価極性辞書（PN Table）を使用します。
URL: http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic

## システムの構成

### 主要なコンポーネント
1. **感情辞書読み込みモジュール**
   - PN Tableの読み込みと辞書形式への変換
   - エンコーディング処理

2. **形態素解析モジュール**
   - Sudachiによる日本語テキストの解析
   - トークン化処理

3. **感情分析モジュール**
   - 感情スコアの計算
   - ポジティブ/ネガティブ表現の抽出

4. **ファイル処理モジュール**
   - CSVファイルの読み込み
   - 分析結果の出力

## 実装手順

### 1. 感情辞書の読み込み関数
```python
def load_pn_table():
    try:
        # 感情辞書の読み込み
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
        
        return pn_dict
    except Exception as e:
        print(f"感情辞書の読み込みに失敗: {e}")
        return None
```

### 2. 感情分析関数
```python
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
    
    # スコアの正規化
    if len(tokens) > 0:
        total_score = total_score / len(tokens)
    
    return total_score, found_words
```

### 3. テキストクリーニング関数
```python
def extract_text(text):
    # 日付情報を除外
    date_pattern = r'\d{4}/\d{2}/\d{2}（[月火水木金土日]）'
    text = re.sub(date_pattern, '', text)
    
    # 日付範囲のパターンを除外
    date_range_pattern = r'～\s*\d{4}/\d{2}/\d{2}（[月火水木金土日]）'
    text = re.sub(date_range_pattern, '', text)
    
    # 余分な空白を削除
    text = text.strip()
    
    # スラッシュで区切られた部分を取得
    parts = text.split('/')
    if len(parts) > 1:
        return parts[-1].strip()
    return text
```

### 4. CSVファイル処理関数
```python
def process_csv_file(file_path, pn_dict):
    try:
        # CSVファイルから文章を読み込み
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # 分析結果を格納するリスト
        results = []
        
        # 各文章を分析
        for i, row in df.iterrows():
            text = row['自由記述']
            clean_text = extract_text(text)
            
            if clean_text:
                score, found_words = analyze_sentiment(clean_text, pn_dict)
                
                # 結果をリストに追加
                results.append({
                    '講義名': row['講義名'],
                    '平均評価ポイント': row['平均評価ポイント'],
                    '自由記述': clean_text,
                    '感情スコア': score,
                    'ポジティブ表現': ', '.join(found_words['positive']),
                    'ネガティブ表現': ', '.join(found_words['negative'])
                })
        
        # 結果をCSVファイルに出力
        results_df = pd.DataFrame(results)
        output_dir = os.path.join(os.path.dirname(file_path), 'analysis')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + '_analysis.csv')
        results_df.to_csv(output_file, index=False, encoding='utf-8')
            
    except Exception as e:
        print(f"ファイル {file_path} の処理中にエラーが発生: {e}")
```

## 使用方法

1. **スクリプトの実行**
```bash
python test2.py
```

2. **入力ファイルの準備**
- CSVファイルを `data/raw/2025` ディレクトリに配置
- 必要な列: '講義名', '平均評価ポイント', '自由記述'

3. **出力の確認**
- 分析結果は `data/raw/2025/analysis` ディレクトリに保存
- 各ファイルに対して `_analysis.csv` という名前で出力

## トラブルシューティング

### よくある問題と解決方法

1. **感情辞書の読み込みエラー**
   - インターネット接続を確認
   - エンコーディングを確認（shift-jis）

2. **CSVファイルの読み込みエラー**
   - ファイルのエンコーディングを確認（utf-8）
   - 必要な列が存在するか確認

3. **メモリエラー**
   - ファイルサイズが大きい場合は、バッチ処理を検討
   - メモリ使用量を監視

### デバッグのヒント
- 各関数にprint文を追加して処理の流れを確認
- エラーメッセージを詳細に確認
- 小さいデータセットでテスト

## 注意事項
- 感情スコアは -1 から 1 の範囲で正規化
- 長い文章は感情スコアが低くなる傾向
- 感情辞書に含まれない単語は無視

## 今後の改善点
1. 文脈を考慮した感情分析
2. 否定表現の適切な処理
3. 修飾語の影響を考慮
4. 機械学習ベースの感情分析の導入 