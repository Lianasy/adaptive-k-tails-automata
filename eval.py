import os
import re
import pandas as pd   # ✅ REQUIRED FIX

# 👉 Your main folder
RESULT_FOLDER = r"C:\Users\HP\Downloads\evl output"


# -----------------------------
# Extract TP, TN, FP, FN
# -----------------------------
def extract_metrics(text):
    def get(pattern):
        m = re.search(pattern, text, re.IGNORECASE)
        return int(m.group(1)) if m else 0

    # Robust patterns
    TP = get(r"\bTP\b\s*[:=]?\s*(\d+)")
    TN = get(r"\bTN\b\s*[:=]?\s*(\d+)")
    FP = get(r"\bFP\b\s*[:=]?\s*(\d+)")
    FN = get(r"\bFN\b\s*[:=]?\s*(\d+)")

    return TP, TN, FP, FN


# -----------------------------
# Compute metrics
# -----------------------------
def compute_scores(TP, TN, FP, FN):
    total = TP + TN + FP + FN

    accuracy = (TP + TN) / total if total else 0
    precision = TP / (TP + FP) if (TP + FP) else 0
    recall = TP / (TP + FN) if (TP + FN) else 0
    specificity = TN / (TN + FP) if (TN + FP) else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0

    return accuracy, precision, recall, specificity, f1


# -----------------------------
# Main processing
# -----------------------------
results = []

for root, dirs, files in os.walk(RESULT_FOLDER):
    for filename in files:
        if filename.endswith(".txt"):
            path = os.path.join(root, filename)

            print("Reading:", path)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                TP, TN, FP, FN = extract_metrics(text)

                # Debug missing metrics
                if TP + TN + FP + FN == 0:
                    print("⚠ No metrics found in:", filename)
                    print("Preview:", text[:200])
                    continue

                acc, prec, rec, spec, f1 = compute_scores(TP, TN, FP, FN)

                results.append({
                    "Folder": os.path.basename(root),
                    "File": filename,
                    "TP": TP,
                    "TN": TN,
                    "FP": FP,
                    "FN": FN,
                    "Accuracy": round(acc, 4),
                    "Precision": round(prec, 4),
                    "Recall": round(rec, 4),
                    "Specificity": round(spec, 4),
                    "F1": round(f1, 4)
                })

            except Exception as e:
                print("❌ Error reading:", filename, "|", e)


# -----------------------------
# Output results
# -----------------------------
if not results:
    print("\n❌ No valid data found. Check your .txt files.")
else:
    df = pd.DataFrame(results)

    print("\n==============================")
    print("📊 INDIVIDUAL RESULTS")
    print("==============================")
    print(df)

    print("\n==============================")
    print("📈 AVERAGE SUMMARY")
    print("==============================")
    print(df.mean(numeric_only=True))

    # Save CSV
    output_path = os.path.join(RESULT_FOLDER, "final_evaluation.csv")
    df.to_csv(output_path, index=False)

    print("\n✅ Results saved to:", output_path)