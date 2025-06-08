# 形態素解析アプリ
import streamlit as st
import pandas as pd
import os
from 形態素解析.morphological_analyzer import MorphologicalAnalyzer # 作成したクラスをインポート

# --- 定数設定 ---
TARGET_DIR = "2025 講義名" # CSVファイルが格納されているディレクトリ
DEFAULT_COLUMN_NAME = "自由記述欄" # デフォルトで解析対象とする列名

@st.cache_resource # MeCabの初期化はリソース消費が大きいのでキャッシュする
def get_analyzer(dictionary_path=""):
    """MorphologicalAnalyzerのインスタンスを返す関数。"""
    try:
        return MorphologicalAnalyzer(dictionary_path=dictionary_path)
    except RuntimeError as e:
        st.error(f"MeCabの初期化に失敗しました。MeCabが正しくインストールされ、設定されているか確認してください。エラー: {e}")
        return None

@st.cache_data # ファイルリストの取得はキャッシュ可能
def get_csv_files(directory):
    """指定されたディレクトリ内のCSVファイルのリストを返す関数。"""
    if not os.path.isdir(directory):
        st.error(f"指定されたディレクトリが見つかりません: {directory}")
        return []
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.csv') and os.path.isfile(os.path.join(directory, f))]
        return files
    except Exception as e:
        st.error(f"ファイルリストの取得中にエラーが発生しました: {e}")
        return []

# --- Streamlit アプリケーション --- 
st.title("CSV形態素解析アプリ")

# 0. MeCab辞書パスの指定 (オプション)
st.sidebar.header("MeCab設定")
mecab_dic_path = st.sidebar.text_input("MeCab辞書パス (オプション)", "", help="例: -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd 指定しない場合はシステムデフォルト")

# MorphologicalAnalyzerの準備
analyzer = get_analyzer(mecab_dic_path)

if analyzer:
    st.sidebar.success("MeCab解析器の準備完了")
else:
    st.stop() # 解析器が準備できなければアプリを停止

# 1. 解析対象ディレクトリの確認とファイル選択
st.header("1. ファイル選択")
csv_files = get_csv_files(TARGET_DIR)

if not csv_files:
    st.warning(f"'{TARGET_DIR}' ディレクトリ内にCSVファイルが見つかりませんでした。")
    st.stop()

selected_file = st.selectbox("解析するCSVファイルを選択してください:", csv_files, index=None, placeholder="ファイルを選択")

if selected_file:
    file_path = os.path.join(TARGET_DIR, selected_file)
    st.write(f"選択されたファイル: `{file_path}`")

    try:
        # 2. CSVファイルの読み込みと列選択
        st.header("2. 解析対象の列を選択")
        df = analyzer.load_csv(file_path)
        st.dataframe(df.head(), use_container_width=True)

        df_columns = df.columns.tolist()
        # デフォルト列名が候補にあればそれを初期選択、なければ最初の列
        default_index = df_columns.index(DEFAULT_COLUMN_NAME) if DEFAULT_COLUMN_NAME in df_columns else 0
        column_to_analyze = st.selectbox(
            "形態素解析を行う列を選択してください:", 
            df_columns, 
            index=default_index
        )

        if column_to_analyze:
            st.write(f"解析対象列: `{column_to_analyze}`")

            # 3. 形態素解析の実行と結果表示
            if st.button(f"'{column_to_analyze}' 列の形態素解析を実行", type="primary"):
                st.header("3. 形態素解析結果")
                with st.spinner("形態素解析を実行中..."):
                    try:
                        analysis_results = analyzer.analyze_column(df, column_to_analyze)
                        
                        # 解析結果の表示（最初の数件のテキストと解析結果を表示）
                        num_preview_rows = st.slider("表示する先頭行数", 1, min(len(df), 50), min(len(df), 5))

                        for i in range(min(num_preview_rows, len(df))):
                            original_text = df[column_to_analyze].iloc[i]
                            result_list = analysis_results[i]

                            with st.expander(f"テキスト {i+1}: 「{str(original_text)[:50]}{'...' if len(str(original_text)) > 50 else ''}」の解析結果", expanded=False):
                                if pd.isna(original_text) or not str(original_text).strip():
                                    st.write("(元のテキストが空または欠損値です)")
                                elif not result_list:
                                    st.write("(解析結果が空です。前処理後、テキストが空白になった可能性があります。)")
                                else:
                                    # (表層形, 品詞, 品詞細分類1, 品詞細分類2, 品詞細分類3, 活用型, 活用形, 原形, 読み, 発音)
                                    result_df_data = []
                                    for token in result_list:
                                        result_df_data.append({
                                            "表層形": token[0],
                                            "品詞": token[1],
                                            "品詞細分類1": token[2],
                                            "品詞細分類2": token[3],
                                            "品詞細分類3": token[4],
                                            "活用型": token[5],
                                            "活用形": token[6],
                                            "原形": token[7],
                                            "読み": token[8],
                                            "発音": token[9],
                                        })
                                    st.dataframe(pd.DataFrame(result_df_data), use_container_width=True)
                        
                        st.success("形態素解析が完了しました。")

                        # 全解析結果をダウンロード可能にする (オプション)
                        # 全テキストと全解析結果を結合したDataFrameを作成
                        # これは非常に大きなデータになる可能性があるので注意
                        # ここでは、表示されている件数分だけのダウンロードにするか、全件にするかなどを検討できる
                        # 簡単な例として、全解析結果のリストをCSVでダウンロードする案
                        
                        # 全解析結果を一つのDataFrameにまとめる (より詳細な出力のため)
                        # 各トークンを独立した行として出力する場合
                        all_tokens_list = []
                        for doc_idx, doc_results in enumerate(analysis_results):
                            original_text_for_doc = str(df[column_to_analyze].iloc[doc_idx])
                            if pd.isna(original_text_for_doc) or not original_text_for_doc.strip():
                                all_tokens_list.append({
                                    "ドキュメントID": doc_idx + 1,
                                    "元のテキスト": original_text_for_doc,
                                    "表層形": "(空テキスト)", "品詞": "-", "品詞細分類1": "-", "品詞細分類2": "-", "品詞細分類3": "-", 
                                    "活用型": "-", "活用形": "-", "原形": "-", "読み": "-", "発音": "-"
                                })
                                continue
                            if not doc_results:
                                all_tokens_list.append({
                                    "ドキュメントID": doc_idx + 1,
                                    "元のテキスト": original_text_for_doc,
                                    "表層形": "(解析結果なし)", "品詞": "-", "品詞細分類1": "-", "品詞細分類2": "-", "品詞細分類3": "-", 
                                    "活用型": "-", "活用形": "-", "原形": "-", "読み": "-", "発音": "-"
                                })
                                continue
                            for token in doc_results:
                                all_tokens_list.append({
                                    "ドキュメントID": doc_idx + 1,
                                    "元のテキスト": original_text_for_doc, # 各トークン行に元のテキストも追加
                                    "表層形": token[0],
                                    "品詞": token[1],
                                    "品詞細分類1": token[2],
                                    "品詞細分類2": token[3],
                                    "品詞細分類3": token[4],
                                    "活用型": token[5],
                                    "活用形": token[6],
                                    "原形": token[7],
                                    "読み": token[8],
                                    "発音": token[9],
                                })
                        
                        if all_tokens_list:
                            full_analysis_df = pd.DataFrame(all_tokens_list)
                            csv_export = full_analysis_df.to_csv(index=False).encode('utf-8-sig') # BOM付きUTF-8
                            st.download_button(
                                label="全解析結果をCSVでダウンロード",
                                data=csv_export,
                                file_name=f"{selected_file.replace('.csv', '')}_{column_to_analyze}_analyzed.csv",
                                mime='text/csv',
                            )
                        else:
                            st.info("ダウンロードする解析結果がありませんでした。")

                    except ValueError as e:
                        st.error(f"形態素解析中にエラーが発生しました: {e}")
                    except Exception as e:
                        st.error(f"予期せぬエラーが発生しました: {e}")

    except FileNotFoundError as e:
        st.error(f"ファイル読み込みエラー: {e}")
    except ValueError as e: # analyze_columnで発生する可能性のあるValueError
        st.error(f"エラー: {e}")
    except Exception as e:
        st.error(f"CSVファイルの処理中に予期せぬエラーが発生しました: {e}")

else:
    st.info("ファイルを選択すると、解析オプションが表示されます。")

# --- フッター情報など (オプション) ---
st.sidebar.markdown("---")
st.sidebar.info("これはCSVファイル内のテキストを形態素解析するStreamlitアプリケーションです。") 