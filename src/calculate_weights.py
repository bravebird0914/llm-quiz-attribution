#!/usr/bin/env python3
"""
GPT-4.1/GPT-4oを使用した重要度算出スクリプト

クイズ問題のトークンデータを読み込み、各トークンが正答に対してどの程度重要か
（attention weight）をGPT-4.1/GPT-4oモデルに評価させて算出します。
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from openai import OpenAI
import time

class AttentionWeightCalculator:
    def __init__(self, config_dir: str = None):
        """
        重要度算出器の初期化
        
        Args:
            config_dir (str): 設定ファイルのディレクトリパス
        """
        self.client = None
        self.config_dir = config_dir or self._get_config_dir()
        self._setup_openai_client()
    
    def _get_config_dir(self) -> str:
        """設定ディレクトリのパスを取得"""
        script_dir = Path(__file__).parent.absolute()
        return str(script_dir)
    
    def _setup_openai_client(self):
        """OpenAI クライアントをセットアップ"""
        try:
            # config.pyファイルから読み込み
            script_dir = Path(__file__).parent.absolute()
            config_file = script_dir / "config.py"
            
            if config_file.exists():
                # config.pyからAPIキーを読み込み
                sys.path.insert(0, str(script_dir))
                import config
                api_key = config.key
                
                self.client = OpenAI(api_key=api_key)
                print(f"OpenAI API設定完了: {config_file}")
            else:
                # 環境変数から取得
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    print("OpenAI API設定完了: 環境変数から取得")
                else:
                    raise ValueError("OpenAI API keyが見つかりません")
        except Exception as e:
            print(f"OpenAI API設定エラー: {str(e)}")
            print(f"設定ファイル: src/config.py を確認してください")
            sys.exit(1)
    
    def load_quiz_data(self, json_file: str) -> List[Dict[str, Any]]:
        """
        JSONファイルからクイズデータを読み込み
        
        Args:
            json_file (str): JSONファイルのパス
            
        Returns:
            List[Dict]: クイズデータのリスト
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"クイズデータ読み込み完了: {len(data)}件")
            return data
        except Exception as e:
            print(f"データ読み込みエラー: {str(e)}")
            sys.exit(1)
    
    def _create_prompt(self, question: str, answer: str, tokens: str) -> str:
        """
        GPT-4.1/GPT-4o用のプロンプトを作成
        
        Args:
            question (str): 問題文
            answer (str): 正答
            tokens (str): トークン文字列（|区切り）
            
        Returns:
            str: 作成されたプロンプト
        """
        # トークンを分割してリスト化
        token_list = [token for token in tokens.split('|') if token.strip()]
        
        prompt = f"""【タスク】
クイズ問題のトークンごとの重要度評価

【問題文】
{question}

【正答】
{answer}

【トークン一覧】
{token_list}

【指示】
上記のクイズ問題について、各トークンが正答「{answer}」を導き出すのにどの程度重要か評価してください。

【評価基準】
- 正答を導くうえで全く手がかりにならないもの: 0に近い値
- 正答を導くうえで非常に有用な手がかりとなるもの: 1に近い値
- 各トークンの重要度の合計は必ず1.0になるように調整してください
- 小数第2位まで出力してください

【出力形式】
以下のJSON形式で出力してください：
{{
  "token_weights": [
    {{"token": "トークン1", "weight": 0.05}},
    {{"token": "トークン2", "weight": 0.12}},
    ...
  ],
  "total_weight": 1.00
}}

重要：JSONのみを出力し、説明文は含めないでください。"""
        
        return prompt
    
    def calculate_attention_weights(self, quiz_item: Dict[str, Any], model: str = "gpt-4.1") -> Dict[str, Any]:
        """
        単一のクイズ問題に対して重要度を算出
        
        Args:
            quiz_item (Dict): クイズデータ
            model (str): 使用するGPTモデル（デフォルト: gpt-4.1）
            
        Returns:
            Dict: 重要度算出結果
        """
        try:
            data_id = quiz_item['data_id']
            question = quiz_item['question']
            answer = quiz_item['answer']
            tokens = quiz_item['tokens']
            
            print(f"処理中: data_id={data_id}")
            
            # プロンプト作成
            prompt = self._create_prompt(question, answer, tokens)
            
            # GPT API呼び出し
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "あなたはクイズ問題の専門家です。与えられたトークンの重要度を正確に評価してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # レスポンス解析
            response_text = response.choices[0].message.content.strip()
            
            # JSONパース
            try:
                # ```json と ``` で囲まれている場合の対応
                if response_text.startswith('```json'):
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_content = response_text[json_start:json_end]
                else:
                    json_content = response_text
                
                weights_data = json.loads(json_content)
            except json.JSONDecodeError:
                # JSON形式でない場合の処理
                print(f"警告: data_id={data_id} のレスポンスがJSON形式ではありません")
                print(f"レスポンス: {response_text}")
                return None
            
            # 結果を整形
            result = {
                'data_id': data_id,
                'question': question,
                'answer': answer,
                'tokens': tokens,
                'token_count': quiz_item['token_count'],
                'attention_weights': weights_data['token_weights'],
                'total_weight': weights_data['total_weight'],
                'model': model,
                'model_response': response_text
            }
            
            print(f"完了: data_id={data_id}, total_weight={weights_data['total_weight']}")
            return result
            
        except Exception as e:
            print(f"エラー: data_id={quiz_item.get('data_id', 'unknown')} - {str(e)}")
            return None
    
    def process_all_quiz_data(self, quiz_data: List[Dict[str, Any]], 
                             output_file: str, model: str = "gpt-4.1", delay: float = 1.0) -> None:
        """
        全クイズデータを処理して結果を保存
        
        Args:
            quiz_data (List[Dict]): クイズデータのリスト
            output_file (str): 出力ファイルのパス
            model (str): 使用するGPTモデル
            delay (float): API呼び出し間の待機時間（秒）
        """
        results = []
        total_items = len(quiz_data)
        
        print(f"=== 重要度算出開始 ===")
        print(f"モデル: {model}")
        print(f"対象データ数: {total_items}")
        print(f"出力ファイル: {output_file}")
        print()
        
        for i, quiz_item in enumerate(quiz_data, 1):
            print(f"進捗: {i}/{total_items}")
            
            result = self.calculate_attention_weights(quiz_item, model=model)
            if result:
                results.append(result)
            
            # API制限対策の待機
            if i < total_items:
                time.sleep(delay)
            
            print()
        
        # 結果を保存
        self._save_results(results, output_file)
        
        print(f"=== 処理完了 ===")
        print(f"成功: {len(results)}/{total_items}")
        print(f"出力ファイル: {output_file}")
    
    def _save_results(self, results: List[Dict[str, Any]], output_file: str) -> None:
        """
        結果をJSONファイルに保存
        
        Args:
            results (List[Dict]): 算出結果のリスト
            output_file (str): 出力ファイルのパス
        """
        try:
            # 出力ディレクトリが存在しない場合は作成
            output_dir = os.path.dirname(output_file)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # JSONファイルに保存
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"結果保存完了: {output_file}")
            
        except Exception as e:
            print(f"保存エラー: {str(e)}")


def main():
    """メイン関数"""
    # ファイルパスの設定
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    
    input_file = project_root / "data" / "output" / "selected_questions.json"
    output_file = project_root / "data" / "output" / "gpt4_turbo_attention_weights.json"
    
    # モデルの選択（gpt-4.1 または gpt-4o）
    model = "gpt-4.1"  # ここを "gpt-4o" に変更することも可能
    
    print(f"=== GPT-4.1/GPT-4o 重要度算出スクリプト ===")
    print(f"使用モデル: {model}")
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    print()
    
    # 重要度算出器を初期化
    calculator = AttentionWeightCalculator()
    
    # クイズデータを読み込み
    quiz_data = calculator.load_quiz_data(str(input_file))
    
    # 全データを処理
    calculator.process_all_quiz_data(quiz_data, str(output_file), model=model, delay=2.0)


if __name__ == "__main__":
    main()

