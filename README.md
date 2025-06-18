# From Rules to Flexibility: A Resource and Method for SEC Item Extraction in Post-2021 10-K Filings

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Introduction

This project addresses the challenge of accurately extracting section-level text from 10-K filings following the SEC's mandatory adoption of the **iXBRL** format in 2021. Traditional rule-based parsers, such as those used for the original EDGAR-CORPUS, struggle to handle the growing structural complexity of modern financial reports.

To bridge this gap, we have developed a novel segmentation framework that combines **fuzzy matching** with **structural heuristics**. This framework robustly handles diverse report layouts, enabling flexible and reliable extraction of textual content from sections like Item 1A (Risk Factors) and Item 7 (MD&A).

This repository contains all the code, data, and tutorials associated with our paper, **From Rules to Flexibility: A Resource and Method for SEC Item Extraction in Post-2021 10-K Filings**. We hope this work provides critical infrastructure for researchers in the field of Financial Natural Language Processing (NLP).

---

## ✨ What's in this Repository?

* **🐍 Python Parser (`/parser`)**: The complete Python script to extract all standard sections from raw 10-K HTML files.
* **📊 The Dataset (`/dataset`)**: The 2021-2024 10-K filings from S&P 500 companies, processed by our framework. The text is pre-segmented by item and ready for analysis.
* **📈 Benchmark Results (`/benchmark_results`)**: The performance metrics (MSE values) for all models reported in our case study.
* **🎓 Case Study Tutorial (`/case_study`)**: A detailed Jupyter Notebook demonstrating how to use our dataset to reproduce the volatility prediction case study from our paper.

---

## 🚀 Our Approach

Unlike traditional methods that rely on a fixed HTML structure, the core advantages of our framework are its **robustness** and **flexibility**:

1.  **Flattened DOM Traversal**: We first flatten the complex HTML tree, retaining only visible text blocks and their basic style information.
2.  **Fuzzy Matching**: We use fuzzy string matching algorithms to align the extracted text blocks against a standardized library of section titles, effectively identifying variations like "Item 1A.", "ITEM 1A:", or "Risk Factors".
3.  **Global Ordering Constraints**: We enforce the natural sequence of report items (e.g., Item 1 must precede Item 1A) to prune incorrect matches and ensure a globally consistent segmentation.

Evaluated by our automated validation protocol, this method achieves an average extraction success rate of **87.8%** on filings from 2021-2024.

---

## 📦 The Dataset

* **Scope**: 1,968 10-K filings submitted by S&P 500 constituents between 2021 and 2024.
* **Format**: JSON Lines (`.jsonl`), where each line is a JSON object representing a single corporate filing.
* **Structure**: Each JSON object contains the company CIK, filing date, and a dictionary of all standard section texts.
    ```json
    [
      {
        "item_key": "item_1",
        "text": "Business description text..."
      },
      {
        "item_key": "item_1a"
        "text": "Risk factors text..."
      }
      ...
    ]
    ```

---

## 🔬 Case Study: Volatility Prediction

To demonstrate the practical utility of our dataset, we conducted a case study to predict future stock volatility using the text from **Item 1A (Risk Factors)**.

* **Models**: We benchmarked several models, including **XGBoost**, **FinBERT**, **RoBERTa**, and **Longformer**.
* **Task**: To predict realized volatility over n = [3, 7, 15, 30, 60, 90] days following the filing date.
* **Findings**: The dataset can be effectively used by all models to achieve significant predictive power over future volatility. For detailed results and reproduction code, please see the `/case_study` directory.

---

## ⚙️ Installation & Usage

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/your_username/your_repository_name.git](https://github.com/your_username/your_repository_name.git)
    cd your_repository_name
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the case study**:
    Open and run the Jupyter Notebook in `/case_study/tutorial.ipynb`.

---

## ✍️ Citation

If you use our code or dataset in your research, please cite our paper:

```bibtex
@article{your_lastname_2025_decoding,
  title={Decoding Modern EDGAR: An Extensible SEC 10-K Corpus for the Post-iXBRL Era},
  author={Your Name and Co-authors},
  journal={Journal or Conference Name},
  year={2025},
  volume={XX},
  pages={XX--XX}
}
```

---

## 📁 Repository Structure

```
.
├── parser/                 # Scripts for text extraction
│   └── extract.py
├── dataset/                # The extracted dataset
│   └── 10k_2021_2024.jsonl
├── case_study/             # Code for reproducing the case study
│   └── tutorial.ipynb
├── benchmark_results/      # Tables with experimental results
│   └── volatility_mse.csv
├── requirements.txt        # Python dependencies
└── README.md               # This README file
