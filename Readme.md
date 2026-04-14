# Employee Turnover Predictor — Salifort Motors

A machine learning web app that predicts whether an employee is likely to leave a company — and explains  why .

Built as my capstone project for the   Google Advanced Data Analytics Certificate  .

🔗   [Live Demo →](#)   &nbsp;|&nbsp; 📓   [Jupyter Notebook →](Salifort%20Motors%20project.ipynb)   &nbsp;|&nbsp; 📊   [Dataset →](HR_dataset.csv)  

---

![App Screenshot](Screenshot%202026-04-14%20121558.png)

---

## What this project is actually about

Most companies find out an employee is leaving when they get the resignation letter. By then it's too late.

This project flips that. Given an employee's work history — how many projects they handle, their evaluation score, how long they've been around — the model flags who's at risk  before  they walk out the door.

I analysed 15,000 employee records from a fictional automotive company (Salifort Motors) and found something counterintuitive:   salary barely matters  . What actually predicts turnover is workload, recognition, and time.

---

## The app

Input an employee's details → get a prediction with a risk score and an explanation of what's driving it.

- Risk gauge (0–100% turnover probability)
- Colour-coded verdict: Stay / Leave
- Flags the specific reasons — overwork, low satisfaction, no promotion, etc.
- Sidebar shows full model performance metrics

---

## What I found in the data

Three types of employees tend to leave:

  The Burned Out   — Working 240–310 hours a month, handling 6–7 projects. Satisfaction tanks. They don't quit because they hate the job. They quit because the job consumed them.

  The Undervalued Overachiever   — Evaluation score above 0.8, satisfaction below 0.5. Doing excellent work. Getting nothing back. These are the most expensive employees to lose.

  The Checked-Out   — Satisfaction near zero. Already mentally gone. The resignation is just paperwork.

### Top predictors (Random Forest feature importance)

| Feature | Importance |
|---|---|
| Last evaluation score | 36.2% |
| Number of projects | 35.1% |
| Tenure | 19.8% |
| Overwork status | 8.3% |
| Satisfaction level | 0.6% |

Salary ranked 5th. Almost irrelevant compared to the top four.

---

## Model performance

Trained a Random Forest classifier on 80% of the data, tested on the remaining 20%.

| Metric | Score |
|---|---|
| Accuracy | 96.2% |
| Precision | 87.0% |
| Recall | 90.4% |
| F1 Score | 88.7% |
| AUC | 93.8% |

Also trained a Decision Tree for comparison — the Random Forest generalised better and had a higher AUC, so that's what the app uses.

---

## Tech stack

-   Python   — data wrangling, modelling, feature engineering
-   Pandas / NumPy   — EDA and preprocessing
-   Scikit-learn   — Random Forest, Decision Tree, train/test split, metrics
-   Matplotlib / Seaborn   — all visualisations
-   Streamlit   — web app
-   Plotly   — interactive gauge chart

---

## Run it locally

```bash
# Clone the repo
git clone https://github.com/yourusername/salifort-motors-predictor-model
cd ssalifort-motors-predictor-model

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

That's it. Opens at `http://localhost:8501`.

---

## Project structure

```
├── app.py                                  # Streamlit app
├── hr_rf1_model.pkl                        # Trained Random Forest model
├── requirements.txt
├── HR_dataset.csv                          # Raw dataset
└── Sailfort Motors project.ipynb           # Full analysis — EDA, modelling, evaluation
```

---

## Key decisions I made along the way

  Why Random Forest over Decision Tree?  
The Decision Tree had slightly higher raw accuracy but overfit more on the training data. The Random Forest's AUC was meaningfully better (93.8% vs ~91%), which matters more when the goal is ranking risk, not just binary classification.

  Why retrain instead of using the original pickle?  
The original model was trained on scikit-learn 0.22. Modern sklearn added a `missing_go_to_left` field to its internal tree structure, making old pickles incompatible. I retrained on the same dataset with identical hyperparameters — same results, no dependency headaches.

  The `overworked` feature  
I engineered a binary `overworked` flag for employees working over 175 hours/month (~10% above the standard 160). It ended up being the 4th most important feature, which validated the hypothesis from the EDA scatter plots.

---

## What I'd do differently with more time

- Proper cross-validation instead of a single train/test split
- SHAP values for per-prediction explainability (more honest than hand-coded flag logic)
- A department-level view in the app — some departments had notably higher attrition than others
- Handle class imbalance more carefully (the dataset is ~83% "stayed")

---

## About

Built by 🖤 Bhishant.

[LinkedIn](https://www.linkedin.com/in/bhishant) &nbsp;·&nbsp; [Portfolio](https://bhishant.in/) &nbsp;·&nbsp; [GitHub](https://github.com/Bhishant/Bhishant)