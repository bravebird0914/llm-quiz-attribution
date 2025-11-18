# LLM-Based Quiz Token Attribution System

**English | [日本語](README.ja.md)**

A system for evaluating the importance (attention weight) of tokens in quiz questions using LLMs (GPT-4.1/GPT-4o).

## 📋 Overview

This system tokenizes quiz questions using morphological analysis and evaluates how important each token is for deriving the correct answer using large language models (GPT-4.1 or GPT-4.o).

### Purpose

A research system for quantitatively evaluating the importance of each token in quiz questions using LLMs.

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/bravebird0914/llm-quiz-attribution.git
cd llm-quiz-attribution

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create API configuration file
cp src/config.py.example src/config.py
# Edit config.py and set your OpenAI API key

# 4. Run scripts
python src/extract_questions.py      # Step 1: Extract questions
python src/calculate_weights.py      # Step 2: Calculate weights
python src/convert_to_csv.py         # Step 3: Convert to CSV
```

## 🗂️ Directory Structure

```
llm-quiz-attribution/
├── README.md                     # This file
├── requirements.txt              # Dependencies
├── src/                          # Source code
│   ├── extract_questions.py     # Data extraction script
│   ├── calculate_weights.py     # GPT weight calculation script
│   ├── convert_to_csv.py        # CSV conversion script
│   └── config.py                # OpenAI API configuration
└── data/
    ├── raw/                      # Raw data
    │   └── abc11-122013-2014.xlsx  # Quiz questions (2481 questions)
    ├── input/                    # Input data
    │   └── abc_2013_2014_tokenized.csv  # Tokenized data
    └── output/                   # Output data
        ├── selected_questions.json       # Extracted quiz data
        ├── selected_questions.csv
        ├── gpt4_turbo_attention_weights.json
        ├── gpt4_turbo_attention_weights.csv
        ├── gpt4_turbo_attention_weights_no_header.csv
        ├── gpt4o_attention_weights.json
        ├── gpt4o_attention_weights.csv
        └── gpt4o_attention_weights_no_header.csv
```

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

⚠️ **Important**: Never commit your API key to GitHub!

**Steps**:

1. Copy `config.py.example` to create `config.py`:
```bash
cp src/config.py.example src/config.py
```

2. Edit `src/config.py` and set your API key:
```python
# OpenAI API Configuration
key = "sk-your-actual-api-key-here"
```

3. `.gitignore` automatically excludes `config.py` from Git management

**Alternative: Environment Variable**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 📊 Data Flow

### Overall Data Flow

```
data/raw/abc11-122013-2014.xlsx (Raw data: 2481 questions)
    ↓ (Morphological analysis) ← Pre-processed in original project
data/input/abc_2013_2014_tokenized.csv (Tokenized data)
    ↓ (Extract 18 questions)
data/output/selected_questions.json
    ↓ (LLM evaluation: Calculate weights with GPT-4.1/GPT-4o)
data/output/gpt4_turbo_attention_weights.json
    ↓ (CSV conversion)
data/output/gpt4_turbo_attention_weights.csv
```

### Data Files Description

- **`data/raw/abc11-122013-2014.xlsx`**: Raw quiz data (2481 questions)
  - ABC (Answer By Computer) competition 2013-2014 problem set
  - Contains questions, correct answers, categories, etc.
  
- **`data/input/abc_2013_2014_tokenized.csv`**: Tokenized data
  - Tokenized using morphological analysis (MeCab)
  - Columns: `data_id`, `question`, `answer`, `tokens`, `token_count`
  - Used as input for LLM (GPT-4.1/GPT-4o) weight calculation

## 📊 Processing Steps

### Step 1: Data Extraction

Extract 18 quiz questions from tokenized data:

```bash
# Run from project root directory
python src/extract_questions.py
```

**Input**: `data/input/abc_2013_2014_tokenized.csv`  
**Output**: `data/output/selected_questions.json`, `data/output/selected_questions.csv`

### Step 2: Weight Evaluation with GPT-4.1/GPT-4o

Evaluate the importance of each token using GPT-4.1 or GPT-4o:

```bash
python src/calculate_weights.py
```

**Input**: `data/output/selected_questions.json`  
**Output**: `data/output/gpt4_turbo_attention_weights.json` (when using GPT-4.1)

To change the model, edit line 279 of `src/calculate_weights.py`:

```python
model = "gpt-4o"  # gpt-4.1 or gpt-4o
```

### Step 3: CSV Conversion

Convert JSON results to CSV (one-line format):

```bash
# Default (gpt4_turbo_attention_weights.json)
python src/convert_to_csv.py

# Specify a JSON file (e.g., GPT-4o version)
python src/convert_to_csv.py gpt4o_attention_weights.json
```

**Output**:
- `gpt4_turbo_attention_weights.csv` (with header)
- `gpt4_turbo_attention_weights_no_header.csv` (without header)

## 📄 Data Format

### JSON Format (Intermediate Data)

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

### CSV Format (Final Output)

```csv
data_id,question,answer,tokens,weights,token_count
2201,イリオス遺跡...,トルコ,|イリオス|遺跡|...|,|0.200000|0.050000|...|,19
```

## 🔧 Customization

### Change Target Quiz Questions

Edit line 113 of `src/extract_questions.py` to specify target data_ids:

```python
target_data_ids = [2201, 141, 2017, ...]  # List of data_ids to extract
```

### Change GPT Model

Edit line 279 of `src/calculate_weights.py`:

```python
model = "gpt-4o"  # or "gpt-4.1", "gpt-4-turbo", etc.
```

### Adjust Prompt

Edit the `_create_prompt` method (lines 83-131) in `src/calculate_weights.py` to customize the prompt.

## 💰 Cost Estimation

- **GPT-4.1**: Approximately $0.03-0.05 per question
- **GPT-4o**: Approximately $0.01-0.02 per question

Processing 18 questions costs approximately $0.5-1.0 (depending on model)

## 📝 Notes

1. **API Key Management**: 
   - `src/config.py` is excluded from Git management in `.gitignore`
   - **Never commit `config.py` to GitHub**
   - `config.py.example` is provided as a template
2. **Rate Limiting**: 2-second wait time between API calls (`delay=2.0`)
3. **Tokenization**: Original data is tokenized using morphological analysis (MeCab)

## 🐛 Troubleshooting

### API Key Error

```
OpenAI API Configuration Error
```

→ Check that `src/config.py` exists and contains a valid API key

### File Not Found

```
Error: Input file not found
```

→ Check that required files exist in `data/input/` or `data/output/`

### JSON Format Error

```
Warning: Response for data_id=XXX is not in JSON format
```

→ GPT response may be invalid. Re-run or adjust the prompt

## 📚 Related Information

- **Morphological Analysis**: Tokenized using MeCab + NEologd dictionary
- **Quiz Data**: Using ABC competition 2013-2014 problem set

## 📄 License

(To be added as needed)

## 👤 Author

Affiliation: Shizuoka University, Faculty of Informatics, Kano Laboratory  

Name: Yuto Yoshida

---

**Last Updated**: 2025-11-17
