import pandas as pd
import MeCab
import neologdn
import demoji

class MorphologicalAnalyzer:
    def __init__(self, dictionary_path=""):
        """
        MeCabを初期化します。

        Args:
            dictionary_path (str, optional): MeCabの辞書パス。
                                            空の場合はデフォルトの辞書を使用します。
                                            例: "-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd"
        """
        try:
            self.tagger = MeCab.Tagger(dictionary_path)
            self.tagger.parse("") # MeCabのウォームアップと初期化確認
        except RuntimeError as e:
            # エラーメッセージに辞書パスの確認を促す情報を追加
            error_message = f"MeCabの初期化に失敗しました。mecabrcファイルや辞書パス（{dictionary_path if dictionary_path else 'デフォルト'}）が正しく設定されているか確認してください。エラー詳細: {e}"
            if "dictionary_path" in str(e).lower() or "mecabrc" in str(e).lower():
                 error_message += "\nシステムにMeCabと適切な辞書がインストールされているか、また環境変数 MECABRC が正しく設定されているか確認してください。"
            raise RuntimeError(error_message) from e

    def load_csv(self, file_path_or_buffer, encoding='utf-8'):
        """
        CSVファイルを読み込み、Pandas DataFrameとして返します。

        Args:
            file_path_or_buffer (str or file-like object): CSVファイルのパスまたはバッファ。
            encoding (str, optional): ファイルのエンコーディング。デフォルトは 'utf-8'。

        Returns:
            pd.DataFrame: 読み込まれたデータ。

        Raises:
            FileNotFoundError: ファイルが見つからない場合。
            Exception: CSVファイルの読み込み中にその他のエラーが発生した場合。
        """
        try:
            df = pd.read_csv(file_path_or_buffer, encoding=encoding)
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"指定されたファイルが見つかりません: {file_path_or_buffer}")
        except Exception as e:
            raise Exception(f"CSVファイルの読み込み中にエラーが発生しました: {e}")

    def _preprocess_text(self, text):
        """
        形態素解析の前にテキストを前処理します。
        - NEologdによる正規化
        - demojiによる絵文字の処理（説明文に置換）

        Args:
            text (str): 前処理対象のテキスト。

        Returns:
            str: 前処理後のテキスト。
        """
        if not isinstance(text, str):
            return "" # 文字列でない場合は空文字列を返す（NaNなどを考慮）
        
        text = str(text) # 明示的に文字列に変換
        text = neologdn.normalize(text)
        # text = demoji.replace_string(text, " ") # 絵文字をコロンで囲まれた名前に置換。見つからない場合は第二引数の文字列。
        return text

    def analyze_text(self, text):
        """
        単一のテキスト文字列を形態素解析し、結果をタプルのリストとして返します。
        各タプルは (表層形, 品詞, 品詞細分類1, 品詞細分類2, 品詞細分類3, 活用型, 活用形, 原形, 読み, 発音) の形式です。
        読みや発音がない場合はNoneとなります。

        Args:
            text (str): 解析対象のテキスト。

        Returns:
            list[tuple]: 形態素解析結果のリスト。
                         BOS/EOSノードは除外されます。
                         解析対象が空文字列や空白のみの場合は空リストを返します。
        """
        processed_text = self._preprocess_text(text)
        if not processed_text.strip(): # 前処理後、空または空白のみになった場合
            return []

        node = self.tagger.parseToNode(processed_text)
        results = []
        while node:
            if node.surface: # 表層形が存在するノードのみ (BOS/EOSノード対策)
                features = node.feature.split(',')
                surface = node.surface
                
                # featuresの要素数は9個と仮定するが、辞書によっては少ない場合があるため、安全にアクセス
                # (品詞, 品詞細分類1, 品詞細分類2, 品詞細分類3, 活用型, 活用形, 原形, 読み, 発音)
                # 読み(features[7])と発音(features[8])は存在しない場合 '*' になることがあるのでNoneに変換
                
                token_info = [surface] + features[:7] # 表層形 + 7つの素性
                
                # 読みと発音の処理
                if len(features) > 7 and features[7] != '*':
                    token_info.append(features[7])
                else:
                    token_info.append(None) # 読みがない場合
                
                if len(features) > 8 and features[8] != '*':
                    token_info.append(features[8])
                else:
                    token_info.append(None) # 発音がない場合
                
                # 不足している特徴量があればNoneで埋める (最大9個の特徴量 + 表層形 = 10要素)
                while len(token_info) < 10:
                    token_info.append(None)

                results.append(tuple(token_info))
            node = node.next
        return results

    def analyze_column(self, df, column_name):
        """
        DataFrameの指定された列に含まれる各テキストを形態素解析します。

        Args:
            df (pd.DataFrame): 対象のDataFrame。
            column_name (str): 形態素解析を行いたい列の名前。

        Returns:
            list[list[tuple]]: DataFrameの各行に対する形態素解析結果のリスト。
                               各内部リストは analyze_text の返り値と同じ形式です。

        Raises:
            ValueError: 指定された列名がDataFrameに存在しない場合。
        """
        if column_name not in df.columns:
            raise ValueError(f"指定された列名 '{column_name}' はDataFrameに存在しません。利用可能な列: {df.columns.tolist()}")

        all_analysis_results = []
        for text_content in df[column_name]:
            # Pandasの欠損値 (NaN) やその他の非文字列型を安全に処理
            analysis_result = self.analyze_text(str(text_content) if pd.notna(text_content) else "")
            all_analysis_results.append(analysis_result)
        return all_analysis_results

if __name__ == '__main__':
    # --- このクラスの簡単な使用例 ---
    print("MorphologicalAnalyzerクラスのテスト実行...")

    # MeCabの辞書パス (例: NEologd)
    # ご自身の環境に合わせて設定してください。空文字列の場合、デフォルト辞書が試みられます。
    # 例: dictionary_arg = "-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd"
    dictionary_arg = "" # ここを編集して特定の辞書を指定できます

    try:
        analyzer = MorphologicalAnalyzer(dictionary_path=dictionary_arg)
        print(f"MeCabの初期化成功。辞書: {'デフォルト' if not dictionary_arg else dictionary_arg}")
    except RuntimeError as e:
        print(f"エラー: MeCabの初期化に失敗しました。")
        print(e)
        print("テストを中断します。MeCabのインストール状況と辞書パスを確認してください。")
        exit()

    # 1. ダミーのCSVデータでテスト
    data = {
        'ID': [1, 2, 3, 4],
        'Tweet': [
            "すもももももももものうち🍑。美味しいよね。",
            "Python🐍を使ってデータ分析をするのは楽しいです！ #プログラミング",
            "今日はいい天気ですね☀お散歩に行こうかな？",
            None # 欠損データのテスト
        ],
        'Category': ['果物', '技術', '日常', '不明']
    }
    sample_df = pd.DataFrame(data)

    print("\n--- ダミーDataFrame ---")
    print(sample_df)

    target_column = 'Tweet'
    print(f"\n--- '{target_column}' 列の形態素解析結果 ---")

    try:
        analysis_results_for_column = analyzer.analyze_column(sample_df, target_column)
        for i, (original_text, result_list) in enumerate(zip(sample_df[target_column], analysis_results_for_column)):
            print(f"\n元のテキスト {i+1}: {original_text}")
            if not result_list:
                print("  (解析結果なし or 空白テキスト)")
                continue
            for token in result_list:
                # (表層形, 品詞, 品詞細分類1, 品詞細分類2, 品詞細分類3, 活用型, 活用形, 原形, 読み, 発音)
                print(f"  形態素: {token[0]:<10} 品詞: {token[1]:<6} 原形: {token[7] if token[7] else '-':<8} 読み: {token[8] if token[8] else '-'}")

    except ValueError as e:
        print(f"エラー: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

    # 2. 単一テキストの解析テスト
    print("\n--- 単一テキストの解析テスト ---")
    test_texts = [
        "これはペンです。",
        "きゃりーぱみゅぱみゅは歌手です。",
        "吾輩は猫である。名前はまだ無い。",
        "We are testing Morphological Analyzer with English words. MeCab may not be optimal for this."
    ]
    for text in test_texts:
        print(f"\n解析対象テキスト: {text}")
        single_text_result = analyzer.analyze_text(text)
        if not single_text_result:
            print("  (解析結果なし or 空白テキスト)")
            continue
        for token in single_text_result:
            print(f"  形態素: {token[0]:<10} 品詞: {token[1]:<6} 原形: {token[7] if token[7] else '-':<8} 読み: {token[8] if token[8] else '-'}")

    print("\n--- テスト完了 ---") 