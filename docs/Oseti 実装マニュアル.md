# Oseti 実装マニュアル

## 目次

1. [はじめに](#はじめに)
2. [Osetiの概要と特徴](#osetiの概要と特徴)
   - [基本情報](#基本情報)
   - [特徴](#特徴)
   - [主な機能](#主な機能)
   - [使用されている辞書](#使用されている辞書)
   - [応用事例](#応用事例)
   - [制限事項](#制限事項)
3. [インストールとセットアップ](#インストールとセットアップ)
   - [依存関係](#依存関係)
   - [基本的なインストール方法](#基本的なインストール方法)
   - [OS別インストール手順](#os別インストール手順)
   - [トラブルシューティング](#インストール時のトラブルシューティング)
   - [動作確認](#動作確認)
4. [基本的な使用方法](#基本的な使用方法)
   - [Analyzerクラスの初期化](#analyzerクラスの初期化)
   - [基本的な感情分析（analyze）](#基本的な感情分析)
   - [極性単語のカウント（count_polarity）](#極性単語のカウント)
   - [詳細な感情分析（analyze_detail）](#詳細な感情分析)
   - [実践的なコード例](#実践的なコード例)
   - [結果の解釈](#結果の解釈)
5. [高度な使用方法とカスタマイズ](#高度な使用方法とカスタマイズ)
   - [カスタム辞書の適用](#カスタム辞書の適用)
   - [辞書とコンバータのチューニング](#辞書とコンバータのチューニング)
   - [否定表現と複雑なパターンへの対応](#否定表現と複雑なパターンへの対応)
   - [大規模テキスト処理の最適化](#大規模テキスト処理の最適化)
   - [実践的な応用例](#実践的な応用例)
   - [トラブルシューティングと解決策](#トラブルシューティングと解決策)
6. [まとめと参考資料](#まとめと参考資料)
   - [まとめ](#まとめ)
   - [参考資料](#参考資料)

## はじめに

このマニュアルは、日本語テキストの感情分析を行うPythonライブラリ「Oseti（おせち）」の実装方法を詳細に解説するものです。基本的な使い方から高度なカスタマイズまで、段階的に説明していきます。

Osetiは辞書ベースのアプローチを採用しており、機械学習を必要とせずに日本語テキストのポジティブ/ネガティブ判定を行うことができます。このマニュアルを通じて、Osetiを効果的に活用するための知識と技術を習得していただければ幸いです。

## Osetiの概要と特徴

### 基本情報

- **開発者**: IKEGAMI Yukino (GitHub: ikegami-yukino)
- **ライセンス**: MIT
- **GitHub**: https://github.com/ikegami-yukino/oseti
- **最新バージョン**: v0.4.2（2023年時点）
- **Python対応**: Python 3.11までサポート

### 特徴

1. **辞書ベースのアプローチ**:
   - 東北大学 乾・岡崎研究室の「日本語評価極性辞書」を利用
   - 用言編と名詞編の両方を活用
   - 機械学習を必要としないため、学習データや大量のリソースが不要

2. **シンプルなAPI**:
   - 数行のコードで感情分析が可能
   - 基本的な極性スコア計算から詳細な分析まで対応

3. **文単位の分析**:
   - 入力テキストを文単位で分割して分析
   - 各文ごとに感情極性スコアを算出

4. **否定表現への対応**:
   - 「〜ない」などの否定表現を検出し、極性を反転
   - 「〜ないわけではない」のような二重否定も適切に処理

5. **カスタマイズ可能**:
   - ユーザー独自の辞書を追加可能
   - 単語辞書と複合語辞書の両方をカスタマイズ可能

### 主な機能

1. **基本的な感情分析** (`analyze`):
   - テキストを文単位で分割し、各文の感情極性スコアを算出
   - 結果は-1.0（完全なネガティブ）から1.0（完全なポジティブ）の範囲で返される

2. **極性単語のカウント** (`count_polarity`):
   - 各文に含まれるポジティブ/ネガティブ単語の数をカウント
   - 文単位で結果を返す

3. **詳細分析** (`analyze_detail`):
   - 各文に含まれるポジティブ/ネガティブ単語のリストと極性スコアを返す
   - どの単語がどのように感情極性に寄与しているかを確認可能

4. **カスタム辞書の適用**:
   - ユーザー独自の単語辞書と複合語辞書を指定可能
   - ドメイン固有の表現に対応するためのカスタマイズが可能

### 使用されている辞書

Osetiは以下の辞書を基盤としています：

1. **日本語評価極性辞書（用言編）ver.1.0**:
   - 小林のぞみ，乾健太郎，松本裕治，立石健二，福島俊一による研究成果
   - 動詞や形容詞などの用言の極性を収録

2. **日本語評価極性辞書（名詞編）ver.1.0**:
   - 東山昌彦, 乾健太郎, 松本裕治による研究成果
   - 名詞の極性を収録

### 応用事例

Osetiは以下のような研究や応用で利用されています：

1. テレビ字幕データを用いた感情分析による「ある日の日本の気分」推定
2. TikTokの流行曲予測システム
3. 個人の特性を反映した文章の類似度判定による小説推薦
4. 新型コロナウイルスに関する新聞社説の分析
5. ツイッターでのラトビアとラトビア人のイメージ分析
6. 大規模災害後の科学的情報の拡散分析
7. 就職面接シナリオにおけるコミュニケーションスキルと自己効力感レベルの推定
8. 日本におけるCOVID-19に関する議論の分析

### 制限事項

1. 辞書に登録されていない単語や表現には対応できない
2. 皮肉や比喩などの間接的な表現の分析が苦手
3. 文脈全体を考慮した分析には限界がある
4. 辞書の更新が必要な場合は手動で行う必要がある

## インストールとセットアップ

### 依存関係

Osetiは以下のパッケージに依存しています：

- **MeCab**: 日本語形態素解析エンジン
- **mecab-python3**: MeCabのPythonバインディング
- **ipadic**: MeCabで使用する辞書
- **sengiri**: 日本語の文分割ライブラリ

### 基本的なインストール方法

#### 方法1: pipを使用した直接インストール

最も簡単な方法は、pipを使用して直接インストールする方法です：

```bash
pip install oseti
```

ただし、この方法では依存関係のMeCabなどを別途インストールする必要があります。

#### 方法2: GitHubからクローンしてインストール

より柔軟にカスタマイズしたい場合は、GitHubからリポジトリをクローンする方法があります：

```bash
# リポジトリをクローン
git clone https://github.com/ikegami-yukino/oseti.git

# 依存関係をインストール
pip install mecab-python3 ipadic sengiri

# osetiディレクトリに移動してインストール
cd oseti
pip install -e .
```

### OS別インストール手順

#### Ubuntuなどのデビアン系Linux

```bash
# MeCabと開発ツールのインストール
sudo apt-get update
sudo apt-get install -y mecab libmecab-dev mecab-ipadic-utf8 swig

# Pythonパッケージのインストール
pip install mecab-python3 ipadic sengiri
pip install oseti
```

#### macOS (Homebrew使用)

```bash
# Homebrewを使用してMeCabをインストール
brew install mecab mecab-ipadic swig

# Pythonパッケージのインストール
pip install mecab-python3 ipadic sengiri
pip install oseti
```

#### Windows

Windowsでは、MeCabのインストールが少し複雑です：

1. [MeCab-0.996-64.exe](https://github.com/ikegami-yukino/mecab/releases/tag/v0.996)をダウンロードしてインストール
2. インストール時に「システム環境変数へのパス設定」にチェックを入れる
3. Pythonパッケージをインストール：

```bash
pip install mecab-python3 ipadic sengiri
pip install oseti
```

#### Google Colab

Google Colabでは以下のコマンドでインストールできます：

```python
!apt-get -q -y install mecab libmecab-dev mecab-ipadic-utf8 swig
!pip install mecab-python3 ipadic sengiri
!pip install oseti
```

### インストール時のトラブルシューティング

#### 1. MeCabのインストールエラー

エラーメッセージ: `command 'gcc' failed with exit status 1`

**解決策**:
```bash
# Ubuntuの場合
sudo apt-get install build-essential python3-dev

# macOSの場合
brew install gcc
xcode-select --install
```

#### 2. NEologd辞書との互換性問題

NEologd辞書を使用すると、一部の単語が正しく判定されない場合があります。

**解決策**:
標準のipadicを使用するか、osetiのコードを修正して対応します：

```python
# oseti/oseti.pyを編集
self.tagger = MeCab.Tagger(ipadic.MECAB_ARGS)
# sengiri.tokenizeの呼び出し時にもipadic.MECAB_ARGSを指定
```

#### 3. Dockerでの実行時の問題

Dockerコンテナ内でosetiを実行する場合、MeCabの設定に注意が必要です。

**解決策**:
Dockerfileに以下を追加：

```dockerfile
RUN apt-get update && apt-get install -y mecab libmecab-dev mecab-ipadic-utf8 swig
RUN pip install mecab-python3 ipadic sengiri oseti
```

### 動作確認

インストールが完了したら、以下のコードで動作確認を行います：

```python
import oseti

# Analyzerのインスタンス化
analyzer = oseti.Analyzer()

# 簡単なテスト
result = analyzer.analyze("素晴らしい体験でした。")
print(result)  # [1.0] のように出力されれば成功
```

## 基本的な使用方法

### Analyzerクラスの初期化

Osetiを使用するには、まず`Analyzer`クラスのインスタンスを作成します。

```python
import oseti

# 基本的な初期化
analyzer = oseti.Analyzer()
```

### 基本的な感情分析

`analyze`メソッドは、テキストを文単位で分割し、各文の感情極性スコアを計算します。

#### 基本的な使い方

```python
import oseti

analyzer = oseti.Analyzer()

# 単一の文を分析
result = analyzer.analyze("素晴らしい体験でした。")
print(result)  # [1.0]

# 複数の文を含むテキストを分析
result = analyzer.analyze("今日は天気が良かった。しかし、電車が遅れて困った。")
print(result)  # [1.0, -1.0]
```

#### 返り値の形式

`analyze`メソッドは、文ごとの感情極性スコアをリストで返します：

- 各要素は-1.0から1.0の範囲の浮動小数点数
- -1.0に近いほどネガティブ、1.0に近いほどポジティブ
- 0.0は中立を表す

#### コード例：様々なテキストの分析

```python
import oseti

analyzer = oseti.Analyzer()

# ポジティブな例
positive_text = "とても美味しい料理でした。最高のサービスに感謝します。"
positive_result = analyzer.analyze(positive_text)
print(f"ポジティブテキスト: {positive_result}")  # [1.0, 1.0]

# ネガティブな例
negative_text = "料金が高すぎる。対応も悪かった。"
negative_result = analyzer.analyze(negative_text)
print(f"ネガティブテキスト: {negative_result}")  # [-1.0, -1.0]

# 混合した例
mixed_text = "商品は良かったが、配送が遅れて困った。それでも満足している。"
mixed_result = analyzer.analyze(mixed_text)
print(f"混合テキスト: {mixed_result}")  # [0.0, -1.0, 1.0]
```

### 極性単語のカウント

`count_polarity`メソッドは、各文に含まれるポジティブ/ネガティブ単語の数をカウントします。

#### 基本的な使い方

```python
import oseti

analyzer = oseti.Analyzer()

# 極性単語のカウント
result = analyzer.count_polarity("素晴らしい景色だったが、天気は悪かった。")
print(result)  # [{'positive': 1, 'negative': 1}]
```

#### 返り値の形式

`count_polarity`メソッドは、文ごとの極性単語カウントを辞書のリストで返します：

- 各辞書は`'positive'`と`'negative'`をキーとし、それぞれの単語数を値として持つ
- リストの各要素は入力テキストの各文に対応

#### コード例：極性単語カウントの活用

```python
import oseti

analyzer = oseti.Analyzer()

# 複数の文を含むテキスト
text = "料理は美味しかった。しかし、接客は最悪だった。それでも、また行きたいと思う。"
result = analyzer.count_polarity(text)

# 結果の表示
for i, sentence_count in enumerate(result):
    print(f"文 {i+1}: ポジティブ単語 {sentence_count['positive']}個, ネガティブ単語 {sentence_count['negative']}個")
```

出力例：
```
文 1: ポジティブ単語 1個, ネガティブ単語 0個
文 2: ポジティブ単語 0個, ネガティブ単語 1個
文 3: ポジティブ単語 1個, ネガティブ単語 0個
```

### 詳細な感情分析

`analyze_detail`メソッドは、各文に含まれるポジティブ/ネガティブ単語のリストと極性スコアを返します。

#### 基本的な使い方

```python
import oseti

analyzer = oseti.Analyzer()

# 詳細な感情分析
result = analyzer.analyze_detail("素晴らしい景色だったが、天気は悪かった。")
print(result)  # [{'positive': ['素晴らしい'], 'negative': ['悪い'], 'score': 0.0}]
```

#### 返り値の形式

`analyze_detail`メソッドは、文ごとの詳細情報を辞書のリストで返します：

- 各辞書は以下のキーを持つ：
  - `'positive'`: ポジティブ単語のリスト
  - `'negative'`: ネガティブ単語のリスト
  - `'score'`: 感情極性スコア（-1.0から1.0）
- リストの各要素は入力テキストの各文に対応

#### コード例：詳細分析の活用

```python
import oseti

analyzer = oseti.Analyzer()

# 否定表現を含むテキスト
text = "この料理は美味しくない。でも、雰囲気は悪くなかった。"
result = analyzer.analyze_detail(text)

# 結果の表示
for i, detail in enumerate(result):
    print(f"文 {i+1}:")
    print(f"  ポジティブ単語: {detail['positive']}")
    print(f"  ネガティブ単語: {detail['negative']}")
    print(f"  スコア: {detail['score']}")
```

出力例：
```
文 1:
  ポジティブ単語: []
  ネガティブ単語: ['美味しい-NEGATION']
  スコア: -1.0
文 2:
  ポジティブ単語: ['悪い-NEGATION']
  ネガティブ単語: []
  スコア: 1.0
```

### 実践的なコード例

#### 例1: 対話型感情分析ツール

```python
import oseti

def analyze_sentiment_interactive():
    analyzer = oseti.Analyzer()
    
    print("日本語感情分析ツール（終了するには 'exit' と入力）")
    print("-" * 50)
    
    while True:
        text = input("\n分析するテキストを入力してください: ")
        
        if text.lower() == 'exit':
            print("プログラムを終了します。")
            break
        
        if not text.strip():
            print("テキストが入力されていません。")
            continue
        
        # 基本分析
        scores = analyzer.analyze(text)
        
        # 詳細分析
        details = analyzer.analyze_detail(text)
        
        # 結果表示
        print("\n【分析結果】")
        print(f"文の数: {len(scores)}")
        
        overall_score = sum(scores) / len(scores) if scores else 0
        print(f"全体の感情スコア: {overall_score:.2f}")
        
        sentiment = "ポジティブ" if overall_score > 0.3 else "ネガティブ" if overall_score < -0.3 else "中立"
        print(f"全体の感情: {sentiment}")
        
        print("\n【文ごとの詳細】")
        for i, (score, detail) in enumerate(zip(scores, details)):
            print(f"文 {i+1}:")
            print(f"  スコア: {score}")
            print(f"  ポジティブ単語: {', '.join(detail['positive']) if detail['positive'] else 'なし'}")
            print(f"  ネガティブ単語: {', '.join(detail['negative']) if detail['negative'] else 'なし'}")

if __name__ == "__main__":
    analyze_sentiment_interactive()
```

#### 例2: CSVファイルの感情分析

```python
import oseti
import pandas as pd
import csv
from datetime import datetime

def analyze_csv_file(input_file, output_file=None):
    # Analyzerの初期化
    analyzer = oseti.Analyzer()
    
    # CSVファイルの読み込み
    df = pd.read_csv(input_file)
    
    # テキスト列の名前を確認（例：'text'という列名を想定）
    text_column = 'text'  # 実際のCSVファイルに合わせて変更
    
    if text_column not in df.columns:
        print(f"エラー: '{text_column}'列がCSVファイルに見つかりません。")
        return
    
    # 結果を格納する新しい列を追加
    df['sentiment_score'] = None
    df['sentiment'] = None
    df['positive_words'] = None
    df['negative_words'] = None
    
    # 各行を処理
    for index, row in df.iterrows():
        text = row[text_column]
        
        # テキストが空でないことを確認
        if isinstance(text, str) and text.strip():
            # 感情分析を実行
            scores = analyzer.analyze(text)
            details = analyzer.analyze_detail(text)
            
            # 平均スコアを計算
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # 感情ラベルを決定
            sentiment = "ポジティブ" if avg_score > 0.3 else "ネガティブ" if avg_score < -0.3 else "中立"
            
            # ポジティブ/ネガティブ単語を抽出
            positive_words = []
            negative_words = []
            for detail in details:
                positive_words.extend(detail['positive'])
                negative_words.extend(detail['negative'])
            
            # 結果をデータフレームに格納
            df.at[index, 'sentiment_score'] = avg_score
            df.at[index, 'sentiment'] = sentiment
            df.at[index, 'positive_words'] = ', '.join(positive_words) if positive_words else ''
            df.at[index, 'negative_words'] = ', '.join(negative_words) if negative_words else ''
    
    # 出力ファイル名が指定されていない場合、デフォルト名を生成
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"sentiment_analysis_{timestamp}.csv"
    
    # 結果をCSVファイルに保存
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"分析結果を {output_file} に保存しました。")
    
    return df

# 使用例
# analyze_csv_file('input.csv', 'output.csv')
```

### 結果の解釈

#### スコアの意味

- **1.0**: 完全にポジティブ
- **0.5**: やや強いポジティブ
- **0.0**: 中立、またはポジティブとネガティブが均衡
- **-0.5**: やや強いネガティブ
- **-1.0**: 完全にネガティブ

#### 否定表現の処理

Osetiは否定表現を適切に処理します：

- 「美味しい」→ ポジティブ
- 「美味しくない」→ ネガティブ（「美味しい-NEGATION」として表示）
- 「美味しくないわけではない」→ ポジティブ（二重否定を検出）

#### 注意点

- 辞書に登録されていない単語は感情分析に影響しません
- 皮肉や比喩などの間接的な表現は正確に分析できない場合があります
- 文脈によって意味が変わる表現は、単純な辞書ベースの手法では限界があります

## 高度な使用方法とカスタマイズ

### カスタム辞書の適用

Osetiでは、独自の単語辞書や複合語辞書を適用することができます。これにより、特定のドメインや用途に合わせた感情分析が可能になります。

#### 単語辞書のカスタマイズ

単語辞書は、単語とその極性（ポジティブ/ネガティブ）のマッピングを定義します。

```python
import oseti

# カスタム単語辞書を定義
custom_word_dict = {
    'カワイイ': 'p',  # ポジティブ
    'ブサイク': 'n',  # ネガティブ
    'イケてる': 'p',  # ポジティブ
    'ダサい': 'n'     # ネガティブ
}

# カスタム辞書を適用してAnalyzerを初期化
analyzer = oseti.Analyzer(word_dict=custom_word_dict)

# 分析実行
result = analyzer.analyze_detail("このデザインはカワイイけど、あのデザインはダサい")
print(result)
```

出力例：
```
[{'positive': ['カワイイ'], 'negative': ['ダサい'], 'score': 0.0}]
```

#### 複合語辞書のカスタマイズ

複合語辞書は、複数の単語からなる表現とその極性を定義します。

```python
import oseti

# カスタム複合語辞書を定義
custom_wago_dict = {
    'イカ する': 'ポジ',     # ポジティブ
    'まがまがしい': 'ネガ',   # ネガティブ
    '期待 を 裏切る': 'ネガ', # ネガティブ
    '目 を 見張る': 'ポジ'    # ポジティブ
}

# カスタム辞書を適用してAnalyzerを初期化
analyzer = oseti.Analyzer(wago_dict=custom_wago_dict)

# 分析実行
result = analyzer.analyze_detail("彼のプレゼンは目を見張るものがあった")
print(result)
```

出力例：
```
[{'positive': ['目 を 見張る'], 'negative': [], 'score': 1.0}]
```

#### 両方の辞書を同時にカスタマイズ

単語辞書と複合語辞書を同時にカスタマイズすることも可能です。

```python
import oseti

# 両方のカスタム辞書を定義
custom_word_dict = {'最高': 'p', '最悪': 'n'}
custom_wago_dict = {'期待 を 裏切る': 'ネガ', '期待 に 応える': 'ポジ'}

# 両方のカスタム辞書を適用
analyzer = oseti.Analyzer(
    word_dict=custom_word_dict,
    wago_dict=custom_wago_dict
)

# 分析実行
result = analyzer.analyze_detail("彼は最高のパフォーマンスで期待に応えた")
print(result)
```

### 辞書とコンバータのチューニング

より高度なカスタマイズとして、Osetiの辞書生成プロセス自体を修正することができます。これには、GitHubからリポジトリをクローンし、辞書コンバータをカスタマイズする必要があります。

#### 辞書コンバータの取得と配置

```bash
# リポジトリをクローン
git clone https://github.com/ikegami-yukino/oseti.git

# 辞書コンバータをdic直下にコピー
cp oseti/etc/make_noun_json.py oseti/oseti/dic/
cp oseti/etc/make_wago_json.py oseti/oseti/dic/
```

#### 元の辞書ファイルの取得

東北大学 乾・岡崎研究室の「日本語評価極性辞書」を取得し、`oseti/oseti/dic/`に配置します。

- `pn.csv.m3.120408.trim`: 名詞のネガポジ辞書
- `wago.121808.pn`: 動詞・形容詞のネガポジ辞書

#### 辞書コンバータのカスタマイズ例

##### 例1: 「ある・ない」の処理を修正

`make_wago_json.py`を編集して、「ある・ない」の処理を変更します。

```python
# 修正前
word = word.replace(' ある', '')

# 修正後
if word.endswith(' ある') or word.endswith(' ない'):
    continue
```

この修正により、「ある・ない」を含む表現が辞書から除外され、名詞のみで感情分析が行われるようになります。

##### 例2: 曖昧な極性の処理を変更

`make_noun_json.py`を編集して、「?p?n」のような曖昧な極性をニュートラルとして扱うようにします。

```python
# 修正前
if polarity == 'e':
    continue

# 修正後
if polarity == 'e' or polarity == '?p?n':
    continue
```

#### 辞書の再生成

辞書コンバータを修正した後、以下のコマンドで辞書を再生成します。

```bash
cd oseti/oseti/dic/
python make_noun_json.py
python make_wago_json.py
```

これにより、`pn_noun.json`と`pn_wago.json`が更新されます。

### 否定表現と複雑なパターンへの対応

Osetiは基本的な否定表現を処理できますが、より複雑なパターンに対応するためのテクニックを紹介します。

#### 否定表現の処理の仕組み

Osetiは以下のような否定表現を検出し、極性を反転させます：

- 「〜ない」「〜ず」などの否定助動詞
- 「〜ないわけではない」のような二重否定

#### 複雑なパターンへの対応例

特定の複雑なパターンに対応するためのカスタム処理関数を作成できます。

```python
import oseti
import re

class CustomAnalyzer:
    def __init__(self):
        self.analyzer = oseti.Analyzer()
        
    def analyze(self, text):
        # 前処理: 特定のパターンを変換
        text = self._preprocess(text)
        
        # Osetiで分析
        return self.analyzer.analyze(text)
    
    def analyze_detail(self, text):
        # 前処理: 特定のパターンを変換
        text = self._preprocess(text)
        
        # Osetiで詳細分析
        return self.analyzer.analyze_detail(text)
    
    def _preprocess(self, text):
        # 例: 「AだけどB」パターンの処理（逆接の処理）
        text = re.sub(r'(.+?)だけど(.+)', r'\1。\2', text)
        
        # 例: 「Aにもかかわらず」パターンの処理
        text = re.sub(r'(.+?)にもかかわらず(.+)', r'\1。\2', text)
        
        # 例: 特定の強調表現の処理
        text = re.sub(r'とても|非常に|すごく', r'', text)
        
        return text

# 使用例
custom_analyzer = CustomAnalyzer()
result = custom_analyzer.analyze("料理は美味しかったけど、サービスは最悪だった")
print(result)  # [1.0, -1.0]
```

### 大規模テキスト処理の最適化

大量のテキストを処理する場合の最適化テクニックを紹介します。

#### バッチ処理

大量のテキストを一度に処理する代わりに、バッチに分割して処理することで、メモリ使用量を抑えることができます。

```python
import oseti
import pandas as pd
from tqdm import tqdm

def batch_sentiment_analysis(texts, batch_size=1000):
    analyzer = oseti.Analyzer()
    results = []
    
    # バッチに分割して処理
    for i in tqdm(range(0, len(texts), batch_size)):
        batch = texts[i:i+batch_size]
        batch_results = [analyzer.analyze(text) for text in batch]
        results.extend(batch_results)
    
    return results

# 使用例
# df = pd.read_csv('large_dataset.csv')
# sentiment_scores = batch_sentiment_analysis(df['text'].tolist())
```

#### マルチプロセッシング

複数のプロセスを使用して並列処理を行うことで、処理速度を向上させることができます。

```python
import oseti
import multiprocessing
from functools import partial

def analyze_text(text, use_detail=False):
    analyzer = oseti.Analyzer()
    if use_detail:
        return analyzer.analyze_detail(text)
    else:
        return analyzer.analyze(text)

def parallel_sentiment_analysis(texts, n_processes=None, use_detail=False):
    if n_processes is None:
        n_processes = multiprocessing.cpu_count() - 1 or 1
    
    with multiprocessing.Pool(processes=n_processes) as pool:
        func = partial(analyze_text, use_detail=use_detail)
        results = pool.map(func, texts)
    
    return results

# 使用例
# texts = ["テキスト1", "テキスト2", ..., "テキストN"]
# results = parallel_sentiment_analysis(texts)
```

### 実践的な応用例

#### 例1: 時系列感情分析

SNSの投稿などを時系列で分析し、感情の変化を可視化します。

```python
import oseti
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def analyze_sentiment_over_time(df, text_column, date_column):
    analyzer = oseti.Analyzer()
    
    # 日付でソート
    df = df.sort_values(by=date_column)
    
    # 感情スコアを計算
    df['sentiment_scores'] = df[text_column].apply(analyzer.analyze)
    df['avg_sentiment'] = df['sentiment_scores'].apply(
        lambda scores: sum(scores) / len(scores) if scores else 0
    )
    
    # 日付ごとに平均感情スコアを集計
    daily_sentiment = df.groupby(df[date_column].dt.date)['avg_sentiment'].mean()
    
    # 可視化
    plt.figure(figsize=(12, 6))
    plt.plot(daily_sentiment.index, daily_sentiment.values)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gcf().autofmt_xdate()
    plt.title('感情スコアの時系列変化')
    plt.ylabel('平均感情スコア')
    plt.xlabel('日付')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    return plt, daily_sentiment

# 使用例
# df = pd.read_csv('tweets.csv')
# df['date'] = pd.to_datetime(df['date'])
# plt, daily_sentiment = analyze_sentiment_over_time(df, 'text', 'date')
# plt.savefig('sentiment_trend.png')
```

#### 例2: 製品レビューの感情分析ダッシュボード

製品レビューの感情分析結果をダッシュボード形式で表示します。

```python
import oseti
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import japanize_matplotlib  # 日本語フォント対応

def analyze_product_reviews(reviews):
    analyzer = oseti.Analyzer()
    
    # 感情分析
    results = []
    for review in reviews:
        scores = analyzer.analyze(review)
        details = analyzer.analyze_detail(review)
        
        # 平均スコア
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # 感情ラベル
        sentiment = "ポジティブ" if avg_score > 0.3 else "ネガティブ" if avg_score < -0.3 else "中立"
        
        # ポジティブ/ネガティブ単語を抽出
        positive_words = []
        negative_words = []
        for detail in details:
            positive_words.extend(detail['positive'])
            negative_words.extend(detail['negative'])
        
        results.append({
            'review': review,
            'avg_score': avg_score,
            'sentiment': sentiment,
            'positive_words': positive_words,
            'negative_words': negative_words
        })
    
    df = pd.DataFrame(results)
    
    # 感情分布の可視化
    plt.figure(figsize=(10, 6))
    sns.countplot(x='sentiment', data=df, palette={'ポジティブ': 'green', '中立': 'gray', 'ネガティブ': 'red'})
    plt.title('レビューの感情分布')
    plt.xlabel('感情')
    plt.ylabel('レビュー数')
    
    # 頻出ポジティブ/ネガティブ単語の抽出
    all_positive_words = [word for words in df['positive_words'] for word in words]
    all_negative_words = [word for words in df['negative_words'] for word in words]
    
    positive_counter = Counter(all_positive_words)
    negative_counter = Counter(all_negative_words)
    
    # 頻出単語の可視化
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # ポジティブ単語
    if positive_counter:
        pos_words, pos_counts = zip(*positive_counter.most_common(10))
        ax1.barh(pos_words, pos_counts, color='green')
        ax1.set_title('頻出ポジティブ単語')
        ax1.set_xlabel('出現回数')
    else:
        ax1.text(0.5, 0.5, 'ポジティブ単語なし', ha='center', va='center')
    
    # ネガティブ単語
    if negative_counter:
        neg_words, neg_counts = zip(*negative_counter.most_common(10))
        ax2.barh(neg_words, neg_counts, color='red')
        ax2.set_title('頻出ネガティブ単語')
        ax2.set_xlabel('出現回数')
    else:
        ax2.text(0.5, 0.5, 'ネガティブ単語なし', ha='center', va='center')
    
    plt.tight_layout()
    
    return df, plt

# 使用例
# reviews = ["商品の品質は良かったが、配送が遅かった。", "とても使いやすくて満足しています。", ...]
# df, plt = analyze_product_reviews(reviews)
# plt.savefig('review_analysis.png')
```

### トラブルシューティングと解決策

#### 問題1: 特定の単語が正しく判定されない

**症状**: 特定の単語や表現が、直感と異なる極性で判定される。

**解決策**:
1. カスタム辞書を使用して、問題のある単語の極性を明示的に定義する。
2. 辞書コンバータをカスタマイズして、特定のパターンの処理方法を変更する。

```python
# カスタム辞書で極性を上書き
custom_dict = {'問題の単語': 'p'}  # または 'n'
analyzer = oseti.Analyzer(word_dict=custom_dict)
```

#### 問題2: 否定表現が正しく処理されない

**症状**: 「〜ない」などの否定表現が正しく処理されない。

**解決策**:
1. テキストの前処理で、否定表現を標準化する。
2. 複雑な否定パターンを検出するカスタム関数を作成する。

```python
def preprocess_negation(text):
    # 否定表現の標準化
    text = re.sub(r'ありません', 'ない', text)
    text = re.sub(r'ではない', 'ない', text)
    return text

# 前処理を適用してから分析
text = preprocess_negation("この商品は良くありません")
result = analyzer.analyze(text)
```

#### 問題3: 複合語が認識されない

**症状**: 「期待を裏切る」のような複合表現が正しく認識されない。

**解決策**:
カスタム複合語辞書を定義して、特定の複合表現を登録する。

```python
custom_wago_dict = {'期待 を 裏切る': 'ネガ'}
analyzer = oseti.Analyzer(wago_dict=custom_wago_dict)
```

#### 問題4: メモリエラーが発生する

**症状**: 大量のテキストを処理する際にメモリエラーが発生する。

**解決策**:
1. バッチ処理を実装して、一度に処理するテキスト量を制限する。
2. 不要なオブジェクトを明示的に削除して、メモリを解放する。

```python
import gc

def process_large_dataset(texts, batch_size=500):
    results = []
    analyzer = oseti.Analyzer()
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = [analyzer.analyze(text) for text in batch]
        results.extend(batch_results)
        
        # メモリ解放
        del batch
        del batch_results
        gc.collect()
    
    return results
```

#### 問題5: MeCab関連のエラー

**症状**: MeCabに関連するエラーが発生する。

**解決策**:
1. MeCabとその辞書が正しくインストールされていることを確認する。
2. ipadic.MECAB_ARGSを明示的に指定する。

```python
import MeCab
import ipadic

# MeCabの動作確認
tagger = MeCab.Tagger(ipadic.MECAB_ARGS)
print(tagger.parse("テスト"))

# osetiのソースコードを修正する場合
# self.tagger = MeCab.Tagger()
# ↓
# self.tagger = MeCab.Tagger(ipadic.MECAB_ARGS)
```

## まとめと参考資料

### まとめ

Osetiは、日本語テキストの感情分析を行うための辞書ベースのPythonライブラリです。東北大学の「日本語評価極性辞書」を基盤とし、シンプルなAPIで感情分析を実現します。

基本的な使い方から高度なカスタマイズまで、様々なレベルでの活用が可能です：

1. **基本的な使い方**:
   - `analyze`: 文ごとの感情極性スコアを取得
   - `count_polarity`: 文ごとのポジティブ/ネガティブ単語数をカウント
   - `analyze_detail`: 文ごとのポジティブ/ネガティブ単語リストとスコアを取得

2. **カスタマイズ**:
   - カスタム辞書の適用
   - 辞書コンバータのチューニング
   - 複雑なパターンへの対応

3. **応用例**:
   - 時系列感情分析
   - 製品レビュー分析
   - 大規模テキスト処理

Osetiは、機械学習を必要とせずに感情分析を行えるため、リソースが限られた環境や、結果の解釈可能性が重要な場面で特に有用です。

### 参考資料

1. [Oseti公式GitHub](https://github.com/ikegami-yukino/oseti)
2. [日本語評価極性辞書（東北大学 乾・岡崎研究室）](http://www.cl.ecei.tohoku.ac.jp/Open_Resources/Japanese_Sentiment_Polarity_Dictionary.html)
3. [単語感情極性対応表（東京工業大学 高村研究室）](http://www.lr.pi.titech.ac.jp/~takamura/pndic_ja.html)
4. [osetiによる日本語の感情分析（npaka）](https://note.com/npaka/n/n3c7722d2e4bc)
5. [Python で日本語文章の感情分析を簡単に試す](http://jupyterbook.hnishi.com/language-models/easy_try_sentiment_analysis.html)
6. [ネガポジ判定ライブラリ"oseti"について](https://book.st-hakky.com/data-science/negaposi-oseti/)
7. [日本語 Sentiment Analyzer を作ってパッケージ化した話](https://qiita.com/Hironsan/items/5c5a0f56f6a7e8b1efa1)
