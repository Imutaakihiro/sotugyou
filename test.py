import MeCab

# MeCab Taggerオブジェクトを作成
mecab = MeCab.Tagger()

# 簡単な日本語の文を分析
text = "私は日本語を勉強しています。"
result = mecab.parse(text)

print(result)
