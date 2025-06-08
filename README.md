# CSVファイルビューアーアプリケーション

## 概要
このアプリケーションは、CSVファイルを効率的に閲覧・分析するためのWebアプリケーションです。
日本語テキストの処理機能を備え、データの可視化と分析をサポートします。

## 機能
- CSVファイルの読み込みと表示
- 日本語テキストの形態素解析
- データの可視化
- 基本的なデータ分析

## セットアップ方法
1. リポジトリのクローン
```bash
git clone [リポジトリURL]
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. アプリケーションの起動
```bash
streamlit run src/app.py
```

## プロジェクト構成
```
csv-viewer/
├── src/                    # ソースコード
├── data/                   # データファイル
├── tests/                  # テストコード
├── docs/                   # ドキュメント
└── requirements.txt        # 依存パッケージ
```

## ライセンス
[ライセンス情報を記載] 