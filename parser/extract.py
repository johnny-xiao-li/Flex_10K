# -*- coding: utf-8 -*-
import os
import re
import glob
import json
import chardet
import argparse
from rapidfuzz import fuzz
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import defaultdict

# Defines the standard section titles to be extracted from a SEC 10-K report.
# The keys are unique identifiers for the items, and the values are the common text descriptions.
target_items = {
    "item_1":   "item 1 business",
    "item_1a":  "item 1a risk factors",
    "item_1b":  "item 1b unresolved staff comments",
    "item_1c":  "item 1c cybersecurity",
    "item_2":   "item 2 properties",
    "item_3":   "item 3 legal proceedings",
    "item_4":   "item 4 mine safety disclosures",
    "item_5":   "item 5 market for registrants common equity related stock holder matters and issuer purchases of equity securities",
    "item_6":   "item 6 reserved",
    "item_7":   "item 7 managements discussion and analysis of financial condition and results of operations",
    "item_7a":  "item 7a quantitative and qualitative disclosures about market risk",
    "item_8":   "item 8 financial statements and supplementary data",
    "item_9":   "item 9 changes in and disagreements with accountants on accounting and financial disclosure",
    "item_9a":  "item 9a controls and procedures",
    "item_9b":  "item 9b other information",
    "item_9c":  "item 9c disclosure regarding foreign jurisdictions that prevent inspections",
    "item_10":  "item 10 directors executive officers and corporate governance",
    "item_11":  "item 11 executive compensation",
    "item_12":  "item 12 security ownership of certain beneficial owners and management and related stock holder matters",
    "item_13":  "item 13 certain relationships and related transactions and director independence",
    "item_14":  "item 14 principal accounting fees and services",
    "item_15":  "item 15 exhibits financial statement schedules",
    "item_16":  "item 16 form 10k summary"
}

def extract_10k_filing(read_path):
    """
    Reads and extracts the HTML content of the 10-K report from a full SEC filing.

    Args:
        read_path (str): The path to the raw filing document.

    Returns:
        str: The extracted HTML content of the 10-K report.
    
    Raises:
        ValueError: If a unique 10-K document section is not found in the file.
    """
    # Read the file content in binary mode
    with open(read_path, 'rb') as f:
        doc_content = f.read()
    
    # Automatically detect the file encoding
    detected_encoding = chardet.detect(doc_content)['encoding']
    encoding = detected_encoding if detected_encoding else 'utf-8'

    # Decode the file content with the detected encoding, with a fallback
    try:
        decoded_content = doc_content.decode(encoding)
    except UnicodeDecodeError: 
        decoded_content = doc_content.decode('ISO-8859-1', errors='ignore')

    # Use regex to extract the 10-K section from the filing
    # <SEQUENCE>1 indicates it's the main document, not an exhibit
    pattern = r'<DOCUMENT>\\s*<TYPE>\\s*10-K\\s*<SEQUENCE>1\\b\\s*(.*?)</DOCUMENT>'
    content_10k = re.findall(pattern, decoded_content, re.DOTALL)

    # Validate that only one 10-K section was found
    if len(content_10k) != 1:
        raise ValueError(f'Error: 10-K Filing eXtraction, matches: {len(content_10k)}')

    # Handle modern XBRL-based reports
    if re.search(r"<XBRL[^>]*>", content_10k[0], re.IGNORECASE):
        pattern = r"<XBRL[^>]*>(.*?)</XBRL>"
        doc_html = re.findall(pattern, content_10k[0], re.DOTALL)[0]
        # Replace non-breaking space HTML entities with standard spaces
        doc_html = doc_html.replace('&nbsp;', ' ')
        return doc_html
    else:
        # For older formats, return the content directly
        return content_10k[0]

def clean_text(text):
    """
    Standardizes text for fuzzy matching.

    Args:
        text (str): The original text.

    Returns:
        str: The cleaned text (lowercase, no punctuation, no extra spaces).
    """
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-z0-9\\s]', '', text)  # Remove all non-alphanumeric characters except spaces
    text = re.sub(r'\\s+', ' ', text).strip()  # Replace multiple spaces with a single space and strip whitespace
    return text

def fuzzy_match(text, target_dict=target_items):
    """
    Compares a given text against the target item list using fuzzy string matching.

    Args:
        text (str): The cleaned text extracted from HTML.
        target_dict (dict): The dictionary of target item titles.

    Returns:
        tuple: (best matching item key, match score).
    """
    best_key, best_score = None, 0
    # Iterate through all target items
    for key, value in target_dict.items():
        # Calculate the similarity ratio between the input text and the target item title
        score = fuzz.ratio(text, value)
        if score > best_score:
            best_key, best_score = key, score
    return best_key, best_score

def extract_item_tags(doc_html, score_threshold=70):
    """
    Parses the HTML and finds the best-matching header tag for each target item.

    Args:
        doc_html (str): The raw HTML of the 10-K report.
        score_threshold (int): Matches with a score below this will be ignored.

    Returns:
        tuple: (max_scores, soup)
            - max_scores (dict): A dictionary of the best match for each item, including score, tag, and index.
            - soup (BeautifulSoup): The parsed BeautifulSoup object.
    
    Raises:
        ValueError: If a match for every required item is not found in the document.
    """
    soup = BeautifulSoup(doc_html, "html.parser")
    
    # Remove irrelevant HTML tags to reduce noise
    for tag in soup.find_all(["ix:header", "a", "hr"]):
        tag.decompose()
    
    body = soup.body
    match_results = defaultdict(list)
    
    # Iterate over all potential header tags (div, p, table)
    for index, tag in enumerate(body.find_all(['div', 'p', 'table'])):
        raw_text = tag.get_text(separator=' ', strip=True)
        # Ignore empty or overly long text (unlikely to be a header)
        if not raw_text or len(raw_text) > 200:
            continue
        
        # Perform fuzzy matching on the text
        item_key, score = fuzzy_match(clean_text(raw_text))
        if score > score_threshold:
            match_results[item_key].append({'score': score, 'tag': tag, 'index': index, 'item_key': item_key})

    # Check if all target items have at least one match
    missing_items = set(target_items.keys()) - set(match_results.keys())
    if missing_items:
        raise ValueError(f'\\tFuzzy Match Error: Item(s) {missing_items} missing.')

    # Select the best match (highest score) for each item from its potential matches
    max_scores = {}
    for item_key, results in match_results.items():
        # Find the dictionary with the max 'score' value
        best_match = max(results, key=lambda x: x['score'])
        max_scores[item_key] = best_match
        
    return max_scores, soup

def eval_item_extract(max_scores):
    """
    Validates that the extracted item tags meet quality standards.

    Args:
        max_scores (dict): The best match information for each item.
    
    Raises:
        ValueError: If the match scores are too low or the items are not in the correct order.
    """
    # 1. Check if all required items were found.
    if len(max_scores) < len(target_items):
        missing = set(target_items.keys()) - set(max_scores.keys())
        raise ValueError(f"\\n❌ Missing items after selection: {missing}")

    # 2. Check if the extracted items appear in the standard document order.
    # First, sort the found items according to the standard order defined in `target_items`.
    sorted_items = sorted(max_scores.values(), key=lambda v: list(target_items.keys()).index(v['item_key']))
    
    # 3. Check if the document indices of the sorted items are monotonically increasing.
    is_in_order = all(sorted_items[i]["index"] < sorted_items[i+1]["index"] for i in range(len(sorted_items)-1))
    if not is_in_order:
        raise ValueError("❌ Extracted ITEMs are not in the correct document order.")

def label_item(max_scores, soup):
    """
    Marks the position of each item header in the HTML with a unique, easily parsable delimiter.

    Args:
        max_scores (dict): The best match tag information for each item.
        soup (BeautifulSoup): The parsed BeautifulSoup object.

    Returns:
        BeautifulSoup: The BeautifulSoup object with markers.
    """
    delim = "*" * 20
    
    # Iterate through all the best-matched tags
    for item_key, result in max_scores.items():
        tag = result['tag']
        # Create a new div tag to act as our delimiter
        new_tag = soup.new_tag('div')
        new_tag.string = f"{delim}[{item_key}]{delim}"
        # (Optional) Add style to the marker for easier debugging in a browser
        new_tag['style'] = 'background-color:lightgreen; border: 2px solid green;'
        # Replace the original header tag with our new marker tag
        tag.replace_with(new_tag)

    # Remove all tables, as their complex structure is often not needed for text analysis
    for tag in soup.find_all('table'):
        tag.decompose()

    return soup

def extract_blocks(soup):
    """
    Splits the document text into blocks based on the delimiters inserted by `label_item`.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object with markers.

    Returns:
        list: A list of dictionaries, where each dictionary contains an "item_key" and its "text".
    """
    # Get the entire document's plain text, preserving line breaks
    doc_content = soup.get_text("\\n", strip=True)
    
    # Regex to find our delimiter, e.g., "********************[item_1a]********************"
    pattern = re.compile(r'\\*{20}\\[(item_\\d+[a-z]?)\\]\\*{20}', re.IGNORECASE)
    
    blocks = []
    matches = list(pattern.finditer(doc_content))

    # Iterate through all found markers (i.e., the start of each item)
    for i, match in enumerate(matches):
        item_key = match.group(1).lower() # Extract the item key and convert to lowercase
        start_pos = match.end()
        # The end position of the current item is the start position of the next item
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(doc_content)
        
        # Extract the text between the two delimiters
        content = doc_content[start_pos:end_pos].strip()
        
        blocks.append({
            "item_key": item_key,
            "text": content
        })

    return blocks

def process_filing(file_path, output_dir, score_threshold):
    """
    Executes the full pipeline for processing a single 10-K file.

    Args:
        file_path (str): The input 10-K filename.
        output_dir (str): The directory to save the output JSON file.
        score_threshold (int): The minimum score for fuzzy matching.
    """
    # Step 1: Extract 10-K HTML from the raw filing
    doc_html = extract_10k_filing(file_path)
    
    # Step 2: Find the header tags for each Item
    max_scores, soup = extract_item_tags(doc_html, score_threshold)
    
    # Step 3: Validate the quality of the results
    eval_item_extract(max_scores)
    
    # Step 4: Mark the Items in the HTML with delimiters
    labeled_soup = label_item(max_scores, soup)
    
    # Step 5: Extract text blocks based on the delimiters
    doc_blocks = extract_blocks(labeled_soup)

    # Step 6: Construct the output path and save the result as a JSON file
    base_filename = os.path.basename(file_path)
    output_filename = os.path.splitext(base_filename)[0] + '.json'
    save_path = os.path.join(output_dir, output_filename)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(doc_blocks, f, ensure_ascii=False, indent=2)

def main(year, score_threshold):
    """
    Main execution function for batch processing 10-K files.
    
    Args:
        year (int): The year of the filings to process.
        score_threshold (int): The minimum score for fuzzy matching.
    """
    # --- Configuration ---
    INPUT_DIR = f'./10k_sp500/{year}' # Input directory
    OUTPUT_DIR = f'./10k_json/{year}'  # Output directory for JSON files
    ERROR_LOG_FILE = f'error_log_{year}.txt' # Error log file
    # --- End Configuration ---

    # Get all .txt files that need to be processed
    file_paths = glob.glob(os.path.join(INPUT_DIR, '*.txt'))
    
    if not file_paths:
        print(f"No .txt files found in the specified directory: {INPUT_DIR}")
        return

    # Clear any previous error log
    with open(ERROR_LOG_FILE, 'w') as f:
        f.write(f"Error log for year {year}\\n{'='*30}\\n")
    
    error_count = 0
    
    print(f"Starting to process {len(file_paths)} files for the year {year}...")
    # Use tqdm for a progress bar
    for f_p in tqdm(file_paths, desc="Processing 10-K files"):
        try:
            # Process a single file
            process_filing(f_p, OUTPUT_DIR, score_threshold)
        except Exception as e:
            # If any error occurs, log it to the error file
            with open(ERROR_LOG_FILE, 'a') as f:
                f.write(f"!--- ERROR ---!\nFile: {f_p}\nError: {e}\\n\n")
            error_count += 1
            
    print(f"\\nProcessing complete!")
    print(f"Successfully processed files: {len(file_paths) - error_count}")
    print(f"Failed files: {error_count}")
    if error_count > 0:
        print(f"Error details can be found in the log file: {ERROR_LOG_FILE}")

# This block ensures the code runs only when the script is executed directly
if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Process SEC 10-K filings to segment them into standard items."
    )
    # Add 'year' as a required command-line argument
    parser.add_argument(
        "year", 
        type=int, 
        help="The year of the filings to process (e.g., 2024)."
    )
    # Add 'threshold' as an optional command-line argument
    parser.add_argument(
        "--threshold", 
        type=int, 
        default=70, 
        help="The minimum fuzzy match score (0-100) to consider a header valid. Default is 70."
    )
    
    args = parser.parse_args()
    
    # Call the main function with the parsed arguments
    main(year=args.year, score_threshold=args.threshold)