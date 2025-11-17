#!/usr/bin/env python3
"""
CSVデータ抽出スクリプト

指定されたCSVファイルから必要な列（data_id, question, answer, tokens, token_count）を
抽出してCSVまたはJSON形式で保存します。
"""

import pandas as pd
import json
import os
from pathlib import Path


def extract_csv_data(input_file: str, output_file: str, target_data_ids: list = None, output_format: str = 'csv') -> None:
    """
    CSVファイルから指定された列を抽出して新しいファイルに保存する
    
    Args:
        input_file (str): 入力CSVファイルのパス
        output_file (str): 出力ファイルのパス
        target_data_ids (list): 抽出対象のdata_idのリスト（指定順序で出力）
        output_format (str): 出力形式 ('csv' または 'json')
    """
    # 必要な列のリスト
    required_columns = ['data_id', 'question', 'answer', 'tokens', 'token_count']
    
    try:
        print(f"入力ファイルを読み込み中: {input_file}")
        
        # CSVファイルを読み込み
        df = pd.read_csv(input_file)
        
        # ヘッダーの確認
        print(f"元のファイルの列: {list(df.columns)}")
        print(f"データ行数: {len(df)}")
        
        # 必要な列が存在するかチェック
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"必要な列が見つかりません: {missing_columns}")
        
        # 特定のdata_idが指定されている場合はフィルタリング
        if target_data_ids:
            print(f"指定されたdata_id: {target_data_ids}")
            print(f"対象データ数: {len(target_data_ids)}")
            
            # data_idでフィルタリング
            filtered_df = df[df['data_id'].isin(target_data_ids)]
            print(f"フィルタリング後のデータ行数: {len(filtered_df)}")
            
            # 指定された順序でソート
            # data_idをカテゴリ型に変換して順序を指定
            filtered_df['data_id'] = pd.Categorical(
                filtered_df['data_id'], 
                categories=target_data_ids, 
                ordered=True
            )
            filtered_df = filtered_df.sort_values('data_id')
            
            # 見つからなかったdata_idを報告
            found_ids = set(filtered_df['data_id'].astype(int))
            missing_ids = [data_id for data_id in target_data_ids if data_id not in found_ids]
            if missing_ids:
                print(f"警告: 以下のdata_idが見つかりませんでした: {missing_ids}")
            
            extracted_df = filtered_df[required_columns]
        else:
            # 全データを抽出
            extracted_df = df[required_columns]
        
        # 出力ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_file)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 出力形式に応じてファイルに保存
        if output_format.lower() == 'json':
            # JSONファイルに保存
            # DataFrameを辞書のリストに変換
            data_list = extracted_df.to_dict('records')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            print(f"JSONデータ抽出完了!")
        else:
            # CSVファイルに保存
            extracted_df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"CSVデータ抽出完了!")
        
        print(f"出力ファイル: {output_file}")
        print(f"出力形式: {output_format.upper()}")
        print(f"抽出された列: {required_columns}")
        print(f"抽出されたデータ行数: {len(extracted_df)}")
        
    except FileNotFoundError:
        print(f"エラー: 入力ファイルが見つかりません: {input_file}")
    except pd.errors.EmptyDataError:
        print(f"エラー: 入力ファイルが空です: {input_file}")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")


def main():
    """メイン関数"""
    # ファイルパスの設定
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent  # プロジェクトルート
    
    input_file = project_root / "data" / "input" / "abc_2013_2014_tokenized.csv"
    output_file = project_root / "data" / "output" / "selected_questions.json"
    
    # 指定されたdata_idのリスト（指定順序）
    target_data_ids = [2201, 141, 2017, 1320, 1055, 495, 1825, 965, 1356, 1613, 667, 2210, 32, 1725, 326, 1524, 1342, 84]
    
    print("=== データ抽出スクリプト（JSON出力版）===")
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    print(f"対象data_id数: {len(target_data_ids)}")
    print()
    
    # データ抽出の実行（JSON形式で出力）
    extract_csv_data(str(input_file), str(output_file), target_data_ids, output_format='json')


if __name__ == "__main__":
    main()

