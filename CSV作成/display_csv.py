import streamlit as st
import pandas as pd
import os
import re
import MeCab
import unicodedata
import neologdn
import demoji
import urllib.parse

st.set_page_config(page_title="CSVビューアー", layout="wide")

st.title("CSVファイルビューアー")

# ストップワードの定義
STOP_WORDS = {
    'それ', 'です', 'ある', 'いる', 'する', 'なる', 'ない', 'こと', 'もの', 'とき',
    'ため', 'ところ', 'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'も',
    'から', 'まで', 'や', 'か', 'な', 'へ', 'より', 'など', 'だけ', 'ばかり'
}

def preprocess_text(text, options):
    if not isinstance(text, str):
        return ""
    
    # Unicode正規化（NFKC）
    if options['normalize_unicode']:
        text = unicodedata.normalize('NFKC', text)
        text = neologdn.normalize(text)
    
    # URLの除去
    if options['remove_urls']:
        text = re.sub(r'https?://[\w/:%#\$&\?\(\)\[\]\.~=\+\-]+', '', text)
    
    # 絵文字の除去
    if options['remove_emojis']:
        text = demoji.replace(text, '')
        text = re.sub(r'[^\u0000-\uFFFF]', '', text)
    
    # 特殊記号の除去
    if options['remove_special_chars']:
        text = re.sub(r'[!！?？。、．,\.]', '', text)
        text = re.sub(r'（笑）|\(笑\)|\(笑\)|（笑）', '', text)
    
    # 改行と空白の正規化
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # 数値の置換
    if options['replace_numbers']:
        text = re.sub(r'\d+', '0', text)
    
    # # MeCabによる形態素解析とストップワード除去 # <--- このブロックをコメントアウト
    # if options['remove_stopwords']:
    #     try:
    #         mecab = MeCab.Tagger("-Owakati")
    #         words = mecab.parse(text).split()
    #         words = [word for word in words if word not in STOP_WORDS]
    #         text = ' '.join(words)
    #     except Exception as e:
    #         st.warning(f"MeCab処理中にエラー: {e}") # エラーを警告として表示
    
    # UTF-8でエンコードできない文字を置換・除去
    text = text.encode('utf-8', errors='replace').decode('utf-8', errors='ignore')
    return text

# ディレクトリ内のCSVファイルを検索
csv_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".csv"):
            csv_files.append(os.path.join(root, file))

if not csv_files:
    st.warning("CSVファイルが見つかりませんでした。")
else:
    # ファイル選択
    selected_file = st.selectbox("表示するCSVファイルを選択してください", csv_files)
    
    try:
        df = pd.read_csv(selected_file, encoding='utf-8')
        
        # テキスト列を選択
        text_columns = df.select_dtypes(include=['object']).columns
        if len(text_columns) > 0:
            selected_column = st.selectbox("MeCabで解析する列を選択してください", text_columns)
            
            # 前処理オプション
            st.subheader("前処理オプション")
            options = {
                'normalize_unicode': st.checkbox("Unicode正規化（NFKC）", value=True),
                'remove_urls': st.checkbox("URLの除去", value=True),
                'remove_emojis': st.checkbox("絵文字の除去", value=True),
                'remove_special_chars': st.checkbox("特殊記号の除去", value=True),
                'replace_numbers': st.checkbox("数値を0に置換", value=False),
                'remove_stopwords': st.checkbox("ストップワードの除去", value=True)
            }
            
            # 前処理の実行
            if st.button("テキストの前処理を実行"):
                df[f'{selected_column}_processed'] = df[selected_column].apply(
                    lambda x: preprocess_text(x, options)
                )
                st.success("前処理が完了しました！")

                # ★変更後のデータフレームを自動的にCSVファイルとして保存
                base, ext = os.path.splitext(os.path.basename(selected_file))
                auto_output_filename = f"{base}_preprocessed_auto{ext}"
                try:
                    df.to_csv(auto_output_filename, index=False, encoding='utf-8', errors='ignore')
                    st.success(f"変更後のファイルが自動保存されました: {auto_output_filename}")
                except Exception as e:
                    st.error(f"自動保存中にエラーが発生しました: {e}")
                
                # 前処理前後の比較表示
                st.subheader("前処理前後の比較")
                st.dataframe(df[[selected_column, f'{selected_column}_processed']], use_container_width=True)
        
        # 元のデータフレーム表示
        st.subheader("元のデータ")
        st.dataframe(df, use_container_width=True)
        
        # 基本統計情報の表示
        st.subheader("基本統計情報")
        st.write(df.describe())
        
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(selected_file, encoding='cp932')
        except Exception as e:
            st.error(f"ファイルの読み込み中にエラーが発生しました: {str(e)}")
    except Exception as e:
        st.error(f"ファイルの読み込み中にエラーが発生しました: {str(e)}") 