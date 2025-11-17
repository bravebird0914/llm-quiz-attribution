#!/usr/bin/env python3
"""
重要度算出結果をCSV形式に変換するスクリプト

JSONファイルから読み込んだ重要度データを、
1行形式のCSVに変換します。

出力形式:
data_id,question,answer,|token1|token2|...|,|weight1|weight2|...|,token_count
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
import sys


def convert_to_csv(input_json: str, output_file: str, with_header: bool = True) -> None:
    """
    重要度算出結果を1行形式のCSVに変換
    
    Args:
        input_json (str): 入力JSONファイルのパス
        output_file (str): 出力CSVファイルのパス
        with_header (bool): ヘッダー行を含めるかどうか
    """
    try:
        # JSONファイルを読み込み
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📖 データ読み込み完了: {len(data)}件")
        
        # 出力ファイルのディレクトリを作成
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # CSVファイルに書き込み
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # ヘッダーを書き込み（オプション）
            if with_header:
                writer.writerow(['data_id', 'question', 'answer', 'tokens', 'weights', 'token_count'])
            
            for item in data:
                data_id = item['data_id']
                question = item['question']
                answer = item['answer']
                token_count = item['token_count']
                
                # トークンリストを作成
                tokens = []
                weights = []
                
                for token_data in item['attention_weights']:
                    tokens.append(token_data['token'])
                    weights.append(f"{token_data['weight']:.6f}")
                
                # |区切り形式で結合
                tokens_str = "|" + "|".join(tokens) + "|"
                weights_str = "|" + "|".join(weights) + "|"
                
                # 1行で出力
                row = [data_id, question, answer, tokens_str, weights_str, token_count]
                writer.writerow(row)
        
        print(f"✅ CSV変換完了: {output_file}")
        print(f"📊 出力データ数: {len(data)}行")
        
        # サンプル表示
        print(f"\n📋 出力サンプル（最初の{2 if with_header else 1}行）:")
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:2]):
                line = line.strip()
                if len(line) > 150:
                    line = line[:150] + "..."
                print(f"  {i+1}: {line}")
        
        # 形式検証
        verify_format(data, output_file, with_header)
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")


def verify_format(original_data: List[Dict[str, Any]], output_file: str, with_header: bool) -> None:
    """
    変換結果の形式を検証
    """
    try:
        print(f"\n🔍 === 形式検証 ===")
        
        # 変換後データの確認
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            converted_data = list(reader)
        
        # ヘッダーがある場合は除外
        data_rows = converted_data[1:] if with_header else converted_data
        
        print(f"📊 元データ: {len(original_data)}件")
        print(f"📊 変換後: {len(data_rows)}行")
        
        if len(data_rows) > 0:
            sample_row = data_rows[0]
            print(f"\n📋 サンプル行の構造:")
            print(f"  列数: {len(sample_row)}")
            print(f"  data_id: {sample_row[0]}")
            print(f"  question: {sample_row[1][:50]}...")
            print(f"  answer: {sample_row[2]}")
            print(f"  tokens: {sample_row[3][:30]}...")
            print(f"  weights: {sample_row[4][:30]}...")
            print(f"  token_count: {sample_row[5]}")
            
            # トークン数と重要度数の整合性確認
            tokens_count = sample_row[3].count('|') - 1  # 先頭と末尾の|を除く
            weights_count = sample_row[4].count('|') - 1
            declared_count = int(sample_row[5])
            
            print(f"\n🔢 数値確認:")
            print(f"  トークン数: {tokens_count}")
            print(f"  重要度数: {weights_count}")
            print(f"  宣言された数: {declared_count}")
            
            if tokens_count == weights_count == declared_count:
                print("  ✅ 数値整合性: OK")
            else:
                print("  ❌ 数値整合性: NG")
        
        print(f"✅ 検証完了")
        
    except Exception as e:
        print(f"❌ 検証エラー: {str(e)}")


def main():
    """メイン関数"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    
    # コマンドライン引数からJSONファイル名を取得（指定がない場合はデフォルト）
    if len(sys.argv) > 1:
        json_filename = sys.argv[1]
    else:
        json_filename = "gpt4_turbo_attention_weights.json"
    
    input_json = project_root / "data" / "output" / json_filename
    output_dir = project_root / "data" / "output"
    
    # 出力ファイル名を決定
    base_name = json_filename.replace('.json', '')
    output_with_header = output_dir / f"{base_name}.csv"
    output_no_header = output_dir / f"{base_name}_no_header.csv"
    
    print("=== 重要度データ CSV変換スクリプト ===")
    print(f"📂 入力ファイル: {input_json}")
    print(f"📁 出力ディレクトリ: {output_dir}")
    print()
    
    # ヘッダー付きCSVを作成
    print("📋 ヘッダー付きCSV作成中...")
    convert_to_csv(str(input_json), str(output_with_header), with_header=True)
    
    print("\n" + "="*60 + "\n")
    
    # ヘッダーなしCSVを作成
    print("📄 ヘッダーなしCSV作成中...")
    convert_to_csv(str(input_json), str(output_no_header), with_header=False)
    
    print(f"\n🎉 変換完了！")
    print(f"📋 作成されたファイル:")
    print(f"  - {output_with_header.name}  (ヘッダー付き)")
    print(f"  - {output_no_header.name}  (ヘッダーなし)")


if __name__ == "__main__":
    main()

