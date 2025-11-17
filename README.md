# LLM-Based Quiz Token Attribution System

クイズ問題のトークンに対する重要度をLLM（GPT-4.1/GPT-4o）を使って評価するシステムです。

## 📋 概要

このシステムは、早押しクイズの問題文を形態素解析でトークン化し、各トークンが正答を導くのにどの程度重要かを大規模言語モデル（GPT-4.1またはGPT-4o）に評価させます。

### 目的

クイズ問題における各トークンの重要度をLLMで定量的に評価するための研究用システムです。

## 🚀 クイックスタート

```bash
# 1. リポジトリをクローン
git clone https://github.com/bravebird0914/llm-quiz-attribution.git
cd llm-quiz-attribution

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. API設定ファイルを作成
cp src/config.py.example src/config.py
# config.py を編集してOpenAI APIキーを設定

# 4. スクリプトを実行
python src/extract_questions.py      # ステップ1: データ抽出
python src/calculate_weights.py      # ステップ2: 重要度計算
python src/convert_to_csv.py         # ステップ3: CSV変換
```

## 🗂️ ディレクトリ構造

```
llm-quiz-attribution/
├── README.md                     # このファイル
├── requirements.txt              # 依存パッケージ
├── src/                          # ソースコード
│   ├── extract_questions.py     # データ抽出スクリプト
│   ├── calculate_weights.py     # GPT重要度計算スクリプト
│   ├── convert_to_csv.py        # CSV変換スクリプト
│   └── config.py                # OpenAI API設定
└── data/
    ├── raw/                      # 生データ（大本）
    │   └── abc11-122013-2014.xlsx  # 早押しクイズ問題の生データ（2481問）
    ├── input/                    # 入力データ
    │   └── abc_2013_2014_tokenized.csv  # トークン化済みデータ
    └── output/                   # 出力データ
        ├── selected_questions.json       # 抽出済みクイズデータ
        ├── selected_questions.csv
        ├── gpt4_turbo_attention_weights.json
        ├── gpt4_turbo_attention_weights.csv
        ├── gpt4_turbo_attention_weights_no_header.csv
        ├── gpt4o_attention_weights.json
        ├── gpt4o_attention_weights.csv
        └── gpt4o_attention_weights_no_header.csv
```

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. OpenAI API キーの設定

⚠️ **重要**: APIキーは絶対にGitHubにコミットしないでください！

**ステップ**:

1. `config.py.example`をコピーして`config.py`を作成：
```bash
cp src/config.py.example src/config.py
```

2. `src/config.py`を編集してAPIキーを設定：
```python
# OpenAI API Configuration
key = "sk-your-actual-api-key-here"
```

3. `.gitignore`により`config.py`は自動的にGit管理から除外されます

**代替方法: 環境変数**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 📊 データの流れ

### データの全体像

```
data/raw/abc11-122013-2014.xlsx (生データ: 2481問)
    ↓ (形態素解析) ← 元プロジェクトで処理済み
data/input/abc_2013_2014_tokenized.csv (トークン化済みデータ)
    ↓ (18問抽出)
data/output/selected_questions.json
    ↓ (LLM評価: GPT-4.1/GPT-4oで重要度計算)
data/output/gpt4_turbo_attention_weights.json
    ↓ (CSV変換)
data/output/gpt4_turbo_attention_weights.csv
```

### データファイルの説明

- **`data/raw/abc11-122013-2014.xlsx`**: 早押しクイズの生データ（2481問）
  - ABC（Answer By Computer）大会 2013-2014年の問題集
  - 問題文、正答、カテゴリなどが含まれる
  
- **`data/input/abc_2013_2014_tokenized.csv`**: 形態素解析済みデータ
  - 形態素解析（MeCab）でトークン化済み
  - 列：`data_id`, `question`, `answer`, `tokens`, `token_count`
  - このデータをもとにLLM（GPT-4.1/GPT-4o）で重要度を計算します

## 📊 データ処理フロー

### ステップ1: データ抽出

トークン化済みデータから18問のクイズを抽出：

```bash
# プロジェクトルートディレクトリで実行
python src/extract_questions.py
```

**入力**: `data/input/abc_2013_2014_tokenized.csv`  
**出力**: `data/output/selected_questions.json`, `data/output/selected_questions.csv`

### ステップ2: GPT-4.1/GPT-4oによる重要度評価

GPT-4.1またはGPT-4oを使って各トークンの重要度を評価：

```bash
python src/calculate_weights.py
```

**入力**: `data/output/selected_questions.json`  
**出力**: `data/output/gpt4_turbo_attention_weights.json` (GPT-4.1使用時)

モデルを変更する場合は、`src/calculate_weights.py` の279行目を編集：

```python
model = "gpt-4o"  # gpt-4.1 または gpt-4o
```

### ステップ3: CSV変換

JSON形式の結果をCSV（1行形式）に変換：

```bash
# デフォルト（gpt4_turbo_attention_weights.json）
python src/convert_to_csv.py

# 特定のJSONファイルを指定（例：GPT-4o版）
python src/convert_to_csv.py gpt4o_attention_weights.json
```

**出力**:
- `gpt4_turbo_attention_weights.csv` （ヘッダー付き）
- `gpt4_turbo_attention_weights_no_header.csv` （ヘッダーなし）

## 📄 データ形式

### JSON形式（中間データ）

```json
{
  "data_id": 2201,
  "question": "イリオス遺跡、カッパドキア、トプカプ宮殿などの観光地がある国といえばどこでしょう？",
  "answer": "トルコ",
  "tokens": "|イリオス|遺跡|、|カッパドキア|、|トプカプ|宮殿|など|の|観光地|が|ある|国|と|いえ|ば|どこ|でしょう|？|",
  "token_count": 19,
  "attention_weights": [
    {"token": "イリオス", "weight": 0.20},
    {"token": "遺跡", "weight": 0.05},
    ...
  ],
  "total_weight": 1.00,
  "model": "gpt-4.1"
}
```

### CSV形式（最終出力）

```csv
data_id,question,answer,tokens,weights,token_count
2201,イリオス遺跡...,トルコ,|イリオス|遺跡|...|,|0.200000|0.050000|...|,19
```

## 🔧 カスタマイズ

### 対象クイズ問題の変更

`src/extract_questions.py` の113行目で対象data_idを編集：

```python
target_data_ids = [2201, 141, 2017, ...]  # 抽出したいdata_idのリスト
```

### GPTモデルの変更

`src/calculate_weights.py` の279行目を編集：

```python
model = "gpt-4o"  # または "gpt-4.1", "gpt-4-turbo" など
```

### プロンプトの調整

`src/calculate_weights.py` の `_create_prompt` メソッド（83-131行目）を編集してプロンプトをカスタマイズできます。

## 💰 コスト見積もり

- **GPT-4.1**: 約$0.03-0.05 per 問題
- **GPT-4o**: 約$0.01-0.02 per 問題

18問の処理で約$0.5-1.0程度（モデルによる）

## 📝 注意事項

1. **APIキーの管理**: 
   - `src/config.py`は`.gitignore`で管理対象外になっています
   - **絶対に`config.py`をGitHubにコミットしないでください**
   - 代わりに`config.py.example`をテンプレートとして提供しています
2. **レート制限**: API呼び出し間に2秒の待機時間を設定（`delay=2.0`）
3. **トークン化**: 元データは形態素解析（MeCab）でトークン化されています

## 🐛 トラブルシューティング

### APIキーエラー

```
OpenAI API設定エラー
```

→ `src/config.py` が存在し、有効なAPIキーが設定されているか確認

### ファイルが見つからない

```
エラー: 入力ファイルが見つかりません
```

→ `data/input/` または `data/output/` に必要なファイルが存在するか確認

### JSON形式エラー

```
警告: data_id=XXX のレスポンスがJSON形式ではありません
```

→ GPTの応答が不正な場合があります。再実行するか、プロンプトを調整してください

## 📚 関連情報

- **形態素解析**: MeCab + NEologd辞書を使用してトークン化済み
- **クイズデータ**: ABC（Answer By Computer）大会 2013-2014年の問題集を使用

## 📄 ライセンス

（必要に応じて追加）

## 👤 作成者

所属：静岡大学 情報学部 狩野研究室
氏名：吉田勇翔

---

**更新日**: 2025-11-17

