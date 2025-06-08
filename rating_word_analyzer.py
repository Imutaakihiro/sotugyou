import os
import glob
import re
import pandas as pd
from morphological_analyzer import MorphologicalAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def load_dataset(raw_dir):
    data_frames = []
    for path in glob.glob(os.path.join(raw_dir, '*.csv')):
        try:
            df = pd.read_csv(path, encoding='utf-8-sig')
        except Exception:
            continue
        if '平均評価ポイント' not in df.columns or '自由記述' not in df.columns:
            continue
        tmp = df[['平均評価ポイント', '自由記述']].copy()
        tmp = tmp.dropna(subset=['自由記述'])
        def extract_rating(val):
            m = re.search(r'([0-9]+\.[0-9]+)', str(val))
            return float(m.group(1)) if m else None
        tmp['rating'] = tmp['平均評価ポイント'].apply(extract_rating)
        tmp = tmp.dropna(subset=['rating'])
        data_frames.append(tmp[['自由記述', 'rating']])
    if data_frames:
        return pd.concat(data_frames, ignore_index=True)
    return pd.DataFrame(columns=['自由記述', 'rating'])


def tokenize_text(analyzer):
    def tokenizer(text):
        tokens = []
        for token in analyzer.analyze_text(text):
            pos = token[1]
            base = token[7] if token[7] else token[0]
            if pos in ('名詞', '動詞', '形容詞', '形容動詞'):
                tokens.append(base)
        return tokens
    return tokenizer


def main():
    raw_dir = '(CSV)2025 raw'
    analyzer = MorphologicalAnalyzer()
    df = load_dataset(raw_dir)
    if df.empty:
        print('データが読み込めませんでした。')
        return

    median_rating = df['rating'].median()
    df['label'] = (df['rating'] >= median_rating).astype(int)

    vectorizer = TfidfVectorizer(tokenizer=tokenize_text(analyzer))
    X = vectorizer.fit_transform(df['自由記述'])
    y = df['label']

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    feature_names = vectorizer.get_feature_names_out()
    coef = model.coef_[0]

    n = 20
    top_positive = sorted(zip(coef, feature_names), reverse=True)[:n]
    top_negative = sorted(zip(coef, feature_names))[:n]

    print('--- 高評価に関連する単語 ---')
    for w, t in top_positive:
        print(f'{t}\t{w:.4f}')

    print('\n--- 低評価に関連する単語 ---')
    for w, t in top_negative:
        print(f'{t}\t{w:.4f}')


if __name__ == '__main__':
    main()
