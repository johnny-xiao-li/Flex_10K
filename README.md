# From Rules to Flexibility: A Resource and Method for SEC Item Extraction in Post-2021 10-K Filings

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Introduction

This project addresses the challenge of accurately extracting section-level text from 10-K filings following the SEC's mandatory adoption of the **iXBRL** format in 2021. Traditional rule-based parsers, such as those used for the original EDGAR-CORPUS, struggle to handle the growing structural complexity of modern financial reports.

To bridge this gap, we have developed a novel segmentation framework that combines **fuzzy matching** with **structural heuristics**. This framework robustly handles diverse report layouts, enabling flexible and reliable extraction of textual content from sections like Item 1A (Risk Factors) and Item 7 (MD&A).

This repository contains all the code, data, and tutorials associated with our paper, **From Rules to Flexibility: A Resource and Method for SEC Item Extraction in Post-2021 10-K Filings**. We hope this work provides critical infrastructure for researchers in the field of Financial Natural Language Processing (NLP).

---

## 🪧 Poster (One-page Overview)

Want a quick visual summary of the dataset and the extraction pipeline?

- 📄 **PDF (recommended):** [Flex_10K Poster](poster/Flex_10K_Poster.pdf)  
- 🖼️ **Preview image:** (shown below)

![Poster preview](poster/Flex_10K_Poster.png)

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

- **Scope**: 1,968 10-K filings submitted by S&P 500 constituents between 2021 and 2024.  
- **Format**: JSON file (`.json`) containing a list of extracted sections from each filing. Each object in the list represents a specific item (e.g., `item_1`, `item_1a`, `item_7`), along with its corresponding text content.  
- **Structure**: Each JSON object contains two fields:
  - `item_key`: the standard SEC item identifier (e.g., `"item_1"`, `"item_1a"`, `item_7`)
  - `text`: the full extracted text of that section
    ```json
    [
      {
        "item_key": "item_1",
        "text": "Business description text..."
      },
      {
        "item_key": "item_1a",
        "text": "Risk factors text..."
      }
      {
        "item_key": "...",
        "text": "..."
      } 
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
    git clone [https://https://github.com/johnny-xiao-li/Flex_10K.git](https://https://github.com/johnny-xiao-li/Flex_10K.git)
    cd Flex_10K
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the case study**:
    Open and run the Jupyter Notebook in `/tutorials/tutorial_{name}.ipynb`.

---

## ✍️ Citation

If you use our code or dataset in your research, please cite our paper:

```bibtex
@inproceedings{li2025rules,
  title={From Rules to Flexibility: A Resource and Method for SEC Item Extraction in Post-2021 10-K Filings},
  author={Li, Xiao and Jin, Changhong and Dong, Ruihai},
  booktitle={Proceedings of the 34th ACM International Conference on Information and Knowledge Management},
  pages={6451--6455},
  year={2025}
}
```

---

## 📁 Repository Structure

```
.
├── parser/                     # Scripts for text extraction
│   └── extract.py
│
├── dataset/                    # The extracted dataset
│   └── 10k_sp500_{2021-2024}   # Years\
│       └── {cik}_{date}.json   # Item-extracted 10-K reports
│
├── tutorials/                 # Code for reproducing the case study
│   └── tutorial.ipynb
│
├── benchmark_results/          # Tables with experimental results
│   └── volatility_mse.csv
│
├── requirements.txt            # Python dependencies
│
├── sample_extract_result/
│   └── sample_extract.html     # Sample extract result by using highlight in HTML
│ 
├── poster/                     # Poster for CIKM
│   └── Flex_10K_Poster.pdf
│   └── Flex_10K_Poster.png
│
└── README.md                   # This README file

```

---

## Poster

- PDF: [Flex_10K Poster](poster/Flex_10K_Poster.png)

![Poster preview](poster/Flex_10K_Poster.png)