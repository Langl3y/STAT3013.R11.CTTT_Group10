<!--
Source text for the full report. build_report.py turns it into a .docx based on the
course template (Template_Do_An_Mon_Hoc_EN.docx) and then into PDF.

Markup:
  # Chapter ...        -> Heading 1 (new page)       ## 1. ...  -> Heading 2     ### 1.1. ... -> Heading 3
  - item               -> bullet                      **bold**  *italic*  `code`
  ![Caption](file.png){width}   -> figure + "Figure n." caption (file from outputs/figures)
  TABLE: Caption       -> next lines are a | pipe | table |, caption placed below as "Table n."
  $$ latex $$          -> centred equation (rendered as image)
  ```python ... ```    -> code block
  REF: text            -> reference list entry
-->

# ABSTRACT

This project studies how a private outpatient clinic can turn its routine records into management decisions. Because real patient files are protected, we generated a realistic but fully simulated clinic in Ho Chi Minh City covering January 2023 to December 2025: 5,000 patients, 24,872 visits and a 1,500-person satisfaction survey. The simulation rules are documented, so the true effects are known in advance and every method can be checked against them.

On this data we run one connected workflow with six stages: descriptive statistics, hypothesis testing (t-test, chi-square, ANOVA), a two-part regression model that predicts each patient's spending in the next year (Patient Lifetime Value, PLV), a structural equation model (SEM) of satisfaction and loyalty, ARIMA forecasting of weekly visits, and machine-learning models that predict which patients will not come back (churn).

The main results are: (1) the two-part model explains about 40% of next-year spending on unseen patients, and its top-decile patients spend almost 4 million VND on average while the bottom decile spends nothing; (2) doctor communication (β = 0.37) and service quality (β = 0.35) are the strongest drivers of satisfaction, and satisfaction drives loyalty (β = 0.69), all within 0.04 of the true values; (3) weekly demand can be forecast with 4.5–5.8% error; (4) a simple logistic regression predicts churn as well as random forest, gradient boosting and a neural network (cross-validated AUC 0.887), with time since the last visit being by far the strongest signal. We end with practical recommendations for clinic managers and a discussion of limitations, ethics and future work.

**Keywords:** healthcare analytics, patient lifetime value, two-part model, structural equation modeling, ARIMA, churn prediction, machine learning.

# Chapter I. INTRODUCTION.

## 1. Topic introduction.

### 1.1. Background and motivation.

Data analysis has become a normal part of running a business. Retailers use transaction histories to decide which customers to target, banks use them to predict who will leave, and e-commerce platforms recommend products from browsing behaviour. The same trend is now reaching healthcare. Hospitals and clinics hold large amounts of data in billing systems, appointment books and patient surveys, and the growth of electronic records, cloud computing and machine learning makes it cheaper than ever to analyse them [4], [5].

Private outpatient clinics are a particularly interesting case. In Vietnam, many people visit private clinics for routine care because waiting times in public hospitals are long. A private clinic earns most of its revenue from patients who come back again and again, for example people with diabetes or high blood pressure who need regular check-ups. This makes a clinic look very much like a service business: it has to attract patients, keep them satisfied, and plan staff for the right number of visits. At the same time, it is still a healthcare provider, so decisions also affect the quality of care.

In practice, small clinics rarely use their own data to answer these questions. Managers decide on marketing, staffing and service improvements mostly from experience. This project shows how standard statistical and machine-learning methods, the ones taught in this course, can be combined into a single workflow that supports such decisions.

### 1.2. Research objectives.

The project answers three management questions for a private clinic:

- **Who is valuable?** Which patients will spend the most at the clinic in the coming year, so that retention budgets can be focused on them?
- **What keeps patients satisfied and loyal?** Which parts of the service experience (service quality, doctor communication, access and waiting, price) matter most for satisfaction, and does stated loyalty translate into real return visits?
- **How much demand should we expect?** How many visits per week should the clinic plan for in the next quarter, and which patients are likely to stop coming?

To answer them we apply the six groups of methods required by the course: descriptive statistics, inferential statistics, regression, structural equation modeling, time-series forecasting and machine learning / deep learning.

### 1.3. Contributions.

The project makes three contributions:

- **An integrated workflow.** All six methods are applied to the same patient base, so the output of one stage informs the next. For example, the survey analysed with SEM is linked back to the real visit records to check whether loyalty predicts return visits.
- **A ground-truth check.** The data are simulated from rules we wrote ourselves. This lets us compare every estimate with the true value, which is impossible with real data and is a recommended way to evaluate statistical methods [6].
- **Practical recommendations.** Each result is translated into an action that a clinic manager or doctor could take.

### 1.4. Relation to the course and reasons for choosing the topic.

The course theme is the application of statistics and ML/DL models in economics, business and healthcare. A private clinic sits exactly at the intersection of these areas: patient spending is an economic and business question, while satisfaction and return visits are healthcare questions. The topic also allows every method in the course outline to be used naturally, without forcing a method onto data that does not suit it. Finally, simulated data was chosen because real patient data is confidential and difficult to obtain for a student project, and because it allowed the whole project to be completed and checked within the course timeline.

### 1.5. Structure of the report.

Chapter II reviews related research. Chapter III describes the data and the methods, including formulas, assumptions and hypotheses. Chapter IV explains how the workflow was implemented in Python, with code excerpts. Chapter V presents and discusses the results of each stage. Chapter VI concludes with recommendations, limitations and future work. The appendix contains links to the code and demo video, the plagiarism and AI-content checks, and additional tables.

## 2. Theoretical basis.

This section summarises the theory behind each method. Details of how each method is applied to the clinic data are given in Chapter III.

### 2.1. Descriptive statistics.

Descriptive statistics summarise a variable without making claims about a wider population. For a sample x₁, …, xₙ the sample mean and variance are:

$$ \bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i, \qquad s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x})^2 $$

Skewness measures asymmetry (positive values mean a long right tail) and kurtosis measures how heavy the tails are. Money and time variables, such as costs and waiting times, are usually right-skewed. This matters because many tests and models assume roughly normal data. Histograms, box plots and scatter plots are used to see these patterns.

### 2.2. Inferential statistics.

Inferential statistics use a sample to test claims (hypotheses) about a population. Each test compares a null hypothesis H₀ (no effect) with an alternative H₁. If the p-value is below the significance level α = 0.05, H₀ is rejected.

- **Welch's t-test** compares the means of two groups without assuming equal variances [16]. The statistic is t = (x̄₁ − x̄₂) / √(s₁²/n₁ + s₂²/n₂).
- **Mann–Whitney U test** is a non-parametric alternative that compares the ranks of two groups. It is used as a robustness check when data are strongly skewed.
- **Chi-square test of independence** checks whether two categorical variables are related, by comparing observed counts O with the counts E expected under independence: χ² = Σ (O − E)² / E.
- **One-way ANOVA** compares the means of more than two groups using the F ratio of between-group to within-group variance. The **Kruskal–Wallis** test is its non-parametric version.

A p-value only says whether an effect is likely to be non-zero, not whether it is large. We therefore also report effect sizes: Cohen's d for t-tests, Cramér's V for chi-square tests and η² for ANOVA.

### 2.3. Regression and the two-part model.

Multiple linear regression models an outcome y as a linear combination of predictors x plus an error term, y = xᵀβ + u, and estimates β by ordinary least squares (OLS). OLS relies on several assumptions: linearity, no strong multicollinearity, constant error variance (homoscedasticity), independent errors and approximately normal errors. These are checked with the variance inflation factor (VIF), the Breusch–Pagan test, the Durbin–Watson statistic and the Jarque–Bera test.

Healthcare spending causes two problems for plain OLS: many people spend nothing, and the positive amounts are very skewed. The standard solution in health economics is the **two-part model** [8]. Part 1 is a logistic regression for the probability of spending anything. Part 2 is an OLS regression on the logarithm of spending for those who spend. When converting predictions from the log scale back to money, a simple exponential underestimates the mean; Duan's smearing factor corrects this [9]. The idea is the same as Customer Lifetime Value (CLV) in marketing [1], [7], applied to patients, so we call it **Patient Lifetime Value (PLV)**.

### 2.4. Structural equation modeling.

Concepts such as satisfaction or service quality cannot be measured directly. Instead, survey respondents rate several statements (items) on a 1–5 Likert scale, and the concept is treated as a **latent variable** behind these items. SEM combines two parts [14]:

- the **measurement model** (confirmatory factor analysis), which links each latent variable to its items through factor loadings;
- the **structural model**, which specifies regression-like paths between latent variables.

The measurement model is assessed by reliability (Cronbach's α and composite reliability CR, both ideally ≥ 0.7), convergent validity (average variance extracted AVE ≥ 0.5) and discriminant validity (the Fornell–Larcker criterion: the square root of each construct's AVE should exceed its correlations with other constructs) [13]. Overall fit is judged by the comparative fit index (CFI) and Tucker–Lewis index (TLI), which should be at least about 0.95, and the root mean square error of approximation (RMSEA), which should be at most about 0.06 [15]. SEM is widely used to study service quality following the SERVQUAL tradition [12].

### 2.5. Time-series forecasting.

An ARIMA(p, d, q) model describes a series by its own past values (autoregressive part, order p), differencing to remove trend (order d) and past forecast errors (moving-average part, order q) [20]. Using the backshift operator B (B yₜ = yₜ₋₁):

$$ \phi(B)\,(1-B)^d\, y_t = c + \theta(B)\,\varepsilon_t $$

The Box–Jenkins approach has four steps: check stationarity (for example with the augmented Dickey–Fuller test), identify p and q from ACF/PACF plots or an information criterion such as AIC, estimate the model, and check that the residuals behave like white noise (Ljung–Box test). Seasonality can be added with seasonal ARIMA terms or, for long seasons such as 52 weeks, with Fourier terms [21]. Holt–Winters exponential smoothing, which updates level, trend and seasonal components with weighted averages, is a common benchmark [22].

### 2.6. Machine learning and deep learning for classification.

Churn prediction is a binary classification problem. We compare four models:

- **Logistic regression** models the log-odds of churn as a linear function of the features. It is simple and easy to interpret through odds ratios.
- **Random forest** averages many decision trees, each trained on a bootstrap sample with random feature subsets [17].
- **Gradient boosting** builds trees one after another, each correcting the errors of the previous ones [23].
- **Multi-layer perceptron (MLP)** is a feed-forward neural network, the deep-learning model of this project. It learns non-linear combinations of the inputs through hidden layers with ReLU activations.

Models are compared with k-fold cross-validation and a held-out test set using the following metrics:
- accuracy;
- precision, the share of predicted churners who really churn;
- sensitivity (recall), the share of real churners who are caught;
- specificity, the share of loyal patients correctly identified;
- the F1 score;
- the area under the ROC curve (AUC).

## 3. Tools and technologies.

The project is written in Python 3.12. The main libraries are:
- pandas and NumPy for data handling;
- SciPy for statistical tests;
- statsmodels for regression and ARIMA [24];
- semopy for SEM [18];
- scikit-learn for machine learning [24];
- Matplotlib and seaborn for charts.

Code is version-controlled with Git and published on GitHub. The IEEE paper is typeset in LaTeX.

# Chapter II. LITERATURE REVIEW.

## 1. Business analytics: customer value and churn.

Customer Lifetime Value (CLV) estimates how much a customer will be worth to a firm in the future. Gupta et al. [1] review the main families of CLV models, from simple RFM scoring to probability models and machine learning. Fader, Hardie and Lee [7] show that three summary measures, recency (time since the last purchase), frequency and monetary value (RFM), contain most of the information needed to predict future value. Reichheld and Sasser [2] argue that keeping existing customers is much cheaper than finding new ones and that small improvements in retention can raise profits strongly. This is the economic reason for churn analysis.

Churn prediction has been studied intensively in telecommunications. Verbeke et al. [3] compared a large number of classifiers and found that simple, understandable models such as logistic regression and decision trees often perform almost as well as complex ones, while being much easier to explain to managers. More recently, Grinsztajn et al. [25] showed that on typical tabular data, tree-based models still outperform deep neural networks. Both findings are relevant to our model comparison.

## 2. Healthcare analytics.

Raghupathi and Raghupathi [4] describe the promise of big-data analytics in healthcare, including better decisions, lower costs and personalised care. Rajkomar, Dean and Kohane [5] review how machine learning is entering clinical medicine and warn about issues of data quality, bias and transparency.

For **spending**, health economists have long known that medical expenditure is skewed with many zeros. The RAND Health Insurance Experiment led Duan et al. [8] to propose the two-part model, which is still standard today, together with Duan's smearing estimator [9]. For **demand**, Jones et al. [10] compared several time-series methods for forecasting daily emergency-department volumes and found that models with seasonal and calendar effects work well. For **patient non-attendance**, Dantas et al. [11] review a large literature on predicting no-shows, showing that past attendance behaviour is the most important predictor. This is similar to the role of recency in customer churn.

## 3. Service quality, satisfaction and loyalty.

Parasuraman, Zeithaml and Berry [12] introduced SERVQUAL, which measures service quality through several dimensions rated on Likert scales. Many later studies, including in hospitals, use SEM to test how such dimensions drive satisfaction and how satisfaction drives loyalty. The methodological standards for these studies are well established: reliability and validity checks from Fornell and Larcker [13] and Hair et al. [14], fit-index cut-offs from Hu and Bentler [15], and checks for common-method bias from Podsakoff et al. [19].

## 4. Research gap and rationale.

Most studies in these areas focus on **one** question with **one** method family. Spending, satisfaction, demand and churn are usually analysed separately. The link between what patients *say* in a survey and what they *do* afterwards is rarely tested on the same people. In addition, studies on real data cannot know whether their estimates are correct.

This project addresses both gaps on a small scale. It combines economic (spending), business (retention, demand) and healthcare (satisfaction, patient care) questions in one workflow on one patient base. Because the data are simulated, it can also report how close each estimate is to the truth. The approach is designed so that the same code can later be run on real, anonymised clinic records.

# Chapter III. RESEARCH METHODOLOGY.

## 1. Dataset.

### 1.1. Why simulated data.

The course allows simulated or public data. We chose simulation for three reasons. First, real patient records are confidential. Second, public healthcare datasets rarely combine visit histories, spending and a satisfaction survey for the same patients, which is needed to link SEM with behaviour. Third, simulation gives a known ground truth, so we can check every method [6]. The simulation is written in a single, commented file (`src/simulate.py`) with a fixed random seed (3013), so anyone can regenerate exactly the same data.

### 1.2. Simulation design.

The simulated clinic operates in Ho Chi Minh City from 1 January 2023 to 31 December 2025 and has five departments: General Medicine, Cardiology, Endocrinology, Dermatology and Dental. Data are generated in three steps.

**Patients.** For each of 5,000 patients we draw:
- age (normal, mean 42, limited to 18–85);
- gender;
- public health insurance (about 65%);
- a chronic condition, with a probability that rises with age;
- membership of a follow-up care programme, more common among chronic patients;
- acquisition channel (walk-in, referral or online);
- a main department.

First-visit dates grow by about 60% over the three years, reflecting a growing clinic. Each patient also receives hidden ("latent") experience scores for service quality, doctor communication, access and convenience (lower when the typical waiting time is long), and price fairness (higher for insured and programme patients). Satisfaction and loyalty are then generated from these scores by fixed equations (Table 2).

**Visits.** While a patient is active, visits arrive as a Poisson process. The visit rate is higher for chronic patients and programme members. The calendar adds:
- a flu-season cycle peaking in late January;
- weekday effects, with Mondays busiest and Sundays quiet;
- an almost-closed week at Lunar New Year (Tet).

Each patient stays with the clinic for a random time whose average increases with loyalty. This is the mechanism that links satisfaction to real behaviour. Each visit has:
- a department;
- a total cost that depends on the department;
- an out-of-pocket payment (insured patients pay 60%, programme members get a further 10% discount);
- a waiting time, longer in flu season and on Mondays.

**Survey.** 1,500 randomly chosen patients answer 20 Likert items (1–5) covering six constructs. Each item equals 3 plus a loading times the patient's latent score plus random noise, rounded and clipped to the 1–5 range.

TABLE: Data dictionary of the three simulated tables.
| Table | Variable | Description |
| patients | patient_id, age, gender | Identifier and demographics |
| patients | insurance, chronic_condition | Public insurance (Yes/No), chronic disease (Yes/No) |
| patients | care_programme | Member of follow-up care programme (Yes/No) |
| patients | acquisition_channel, main_department | How the patient found the clinic; usual department |
| patients | first_visit_date | Date of first visit |
| visits | visit_id, patient_id, visit_date | One row per visit |
| visits | department | Department of the visit |
| visits | total_cost_kvnd, out_of_pocket_kvnd | Cost and patient payment (thousand VND) |
| visits | wait_minutes | Waiting time in minutes |
| survey | SQ1–SQ4, DC1–DC4 | Service quality; doctor communication |
| survey | AC1–AC3, PF1–PF3 | Access and convenience; price fairness |
| survey | SAT1–SAT3, LOY1–LOY3 | Satisfaction; loyalty intention |

TABLE: Main simulation rules (the "ground truth").
| Relation | True value |
| Satisfaction ← service quality | 0.30 (standardised: 0.34) |
| Satisfaction ← doctor communication | 0.35 (standardised: 0.40) |
| Satisfaction ← access and convenience | 0.20 (standardised: 0.23) |
| Satisfaction ← price fairness | 0.20 (standardised: 0.24) |
| Loyalty ← satisfaction | 0.65 (standardised: 0.68) |
| Log visit rate ← chronic condition | +0.60 (visit rate × 1.82) |
| Log visit rate ← care programme | +0.30 (visit rate × 1.35) |
| Out-of-pocket share, insured | 0.60 of cost |
| Out-of-pocket share, programme member | 0.90 of cost |

## 2. Overall workflow.

Figure 1 shows the workflow. The simulated data are preprocessed once into patient-level features, and then six analysis stages are run. Each stage follows the sequence required by the course: data preparation → preprocessing → modeling → evaluation. The results are combined into recommendations in Chapter VI.

![Overall project workflow.](f0_workflow.png){6.2}

## 3. Preprocessing and feature engineering.

For the patient-level models (regression and churn), we fix an observation **cut-off date of 31 December 2024**. All features use only visits on or before this date, and all targets look at what happens afterwards. This mirrors how a clinic would use the model in practice and prevents "information leakage" from the future. The features are:
- **frequency** (number of visits);
- **monetary** (total out-of-pocket spend) and **average spend** per visit;
- **average waiting time**;
- **recency** (days since the last visit);
- **tenure** (days since the first visit);
- **number of departments** visited;
- the patient's demographic and programme variables.

The two targets are:
- **PLV**: total out-of-pocket spend from January to December 2025;
- **churn**: equal to 1 if the patient makes no visit between January and June 2025.

The resulting cohort contains 3,070 patients. 62.4% of them churn and 60.2% have zero PLV. For modeling, the cohort is split into 80% training and 20% test data, stratified by the target. For the time series, visits are counted per week (Monday to Sunday), giving 155 complete weeks.

## 4. Model specifications and hypotheses.

### 4.1. Inferential statistics.

We test five groups of hypotheses at α = 0.05:

- **H1:** Care-programme members spend a different amount per year than non-members (Welch t-test on 2024 spending among patients registered before 2024; Mann–Whitney U as robustness check).
- **H2:** Returning to the clinic in the first half of 2025 is associated with insurance status (chi-square). **H2b:** it is associated with having a chronic condition.
- **H3:** Returning is associated with the acquisition channel (chi-square).
- **H4:** Mean waiting time differs between departments (one-way ANOVA, Kruskal–Wallis as robustness check, Levene test for equal variances).
- **H5:** Programme members report higher satisfaction (Welch t-test on the mean of SAT1–SAT3).

### 4.2. Two-part PLV model.

For patient i with features xᵢ, Part 1 is a logistic regression and Part 2 an OLS regression on log spending:

$$ \Pr(Y_i > 0 \mid x_i) = \frac{1}{1 + e^{-x_i^\top \gamma}}, \qquad \log Y_i \mid (Y_i > 0) = x_i^\top \beta + u_i $$

The expected PLV combines both parts with Duan's smearing factor φ, the average of the exponentiated Part-2 residuals:

$$ \hat{E}[Y_i \mid x_i] = \hat{\Pr}(Y_i > 0 \mid x_i)\cdot e^{x_i^\top \hat{\beta}}\cdot \hat{\phi}, \qquad \hat{\phi} = \frac{1}{n_+}\sum_{Y_i>0} e^{\hat{u}_i} $$

The predictors are:
- age, gender, insurance, chronic condition, programme membership and channel;
- log frequency and log average spend;
- recency and tenure in months;
- average waiting time.

Part 2 uses heteroscedasticity-robust (HC3) standard errors. A random forest regressor trained directly on PLV is used as a non-linear benchmark. A mean-only model is the naive baseline.

### 4.3. Structural equation model.

The SEM has six latent constructs. Four exogenous constructs explain satisfaction, which in turn explains loyalty:

$$ \mathrm{SAT} = \gamma_1 \mathrm{SQ} + \gamma_2 \mathrm{DC} + \gamma_3 \mathrm{AC} + \gamma_4 \mathrm{PF} + \zeta_1, \qquad \mathrm{LOY} = \beta_1 \mathrm{SAT} + \zeta_2 $$

The model is estimated by maximum likelihood. We report reliability, validity and fit indices as described in Section I.2.4. To check for common-method bias, a model with a single general factor for all 20 items (Harman's test) is compared with the six-construct model [19]. Finally, for respondents who are also in the 2024 cohort, a logistic regression of actual return on the standardised loyalty score, controlling for recency, tests whether stated loyalty predicts behaviour.

### 4.4. ARIMA model.

The weekly series yₜ is modelled as ARIMA(p, 1, q) with a linear drift. Two pairs of Fourier terms capture the yearly cycle, and a dummy variable marks Tet weeks:

$$ \phi(B)(1-B)\,y_t = c + \sum_{k=1}^{2}\left[a_k \sin\frac{2\pi k t}{52.18} + b_k \cos\frac{2\pi k t}{52.18}\right] + \delta\,\mathrm{Tet}_t + \theta(B)\,\varepsilon_t $$

p and q are chosen from 0 to 3 by the lowest AIC on the training data. The last 13 weeks (one quarter) are kept as the test set. The benchmarks are:
- additive Holt–Winters with a 52-week season;
- a seasonal naive forecast, which repeats the value from the same week of the previous year.

Accuracy is measured by MAE, RMSE and MAPE.

### 4.5. Churn classifiers.

The four classifiers of Section I.2.6 are trained inside identical pipelines. Numeric features are standardised and categorical features are one-hot encoded inside the pipeline, so information from validation folds never leaks into training. The model settings are:
- random forest: 500 trees, minimum leaf size 5;
- gradient boosting: learning rate 0.05, maximum depth 4, 300 iterations;
- MLP: hidden layers of 64 and 32 neurons, L2 penalty 0.001, early stopping.

Models are compared by 5-fold stratified cross-validated AUC on the training set and by all metrics on the test set, at a threshold of 0.5. Permutation importance (the drop in test AUC when a feature is randomly shuffled) explains the best model.

# Chapter IV. IMPLEMENTATION AND EXPERIMENTS.

## 1. Environment and project structure.

The project runs on any computer with Python 3.10 or newer. It was developed on macOS with Python 3.12.6 and needs no GPU. The library versions are pinned in `requirements.txt`. The repository is organised as follows:

```text
src/simulate.py          data generator (seed 3013)
src/common.py            loading, feature engineering, helpers
src/s1_descriptive.py    stage 1  - descriptive statistics
src/s2_inferential.py    stage 2  - hypothesis tests
src/s3_regression.py     stage 3  - two-part PLV model
src/s4_sem.py            stage 4  - structural equation model
src/s5_forecast.py       stage 5  - ARIMA forecasting
src/s6_ml.py             stage 6  - churn classifiers
src/run_all.py           runs everything in order
data/                    patients.csv, visits.csv, survey.csv
outputs/figures, tables  every figure and table in this report
outputs/results.json     every number quoted in this report
```

The whole project is reproduced with four commands, and a full run takes about 15 seconds:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd src
python run_all.py
```

## 2. Implementation of each stage.

### 2.1. Data generation.

The key idea of the simulation is that the same hidden satisfaction and loyalty scores drive both the survey answers and the patient's real behaviour. The excerpt below shows how the structural relations are generated and how loyalty sets the patient's expected time with the clinic:

```python
sat = 0.30*sq + 0.35*dc + 0.20*ac + 0.20*pf + rng.normal(0, 0.6, n)
loy = 0.65*sat + rng.normal(0, 0.6, n)
# months the patient stays with the clinic - loyal patients stay longer
mean_life = np.exp(2.4 + 0.5*loy[i] + 0.35*prog + 0.3*chronic)
```

Survey items are produced from the latent scores and then rounded to the 1–5 scale:

```python
noise = rng.normal(0, np.sqrt(1 - lam**2), n_resp)
item  = np.clip(np.round(3 + 1.1*(lam*z + noise)), 1, 5)
```

### 2.2. Feature engineering.

The function `patient_features` in `common.py` builds one row per patient from the visit table. Features use only the history up to the cut-off, and the targets use only later visits:

```python
hist = visits[visits.visit_date <= CUTOFF]
g = hist.groupby("patient_id")
feats = pd.DataFrame({
    "frequency":    g.size(),
    "monetary":     g.out_of_pocket_kvnd.sum(),
    "recency_days": (CUTOFF - g.visit_date.max()).dt.days,
    "tenure_days":  (CUTOFF - g.visit_date.min()).dt.days, ...})
```

### 2.3. Hypothesis tests.

All tests use SciPy. For example, H1 and H2 are run as:

```python
t, p   = stats.ttest_ind(members, non_members, equal_var=False)  # Welch
u, pu  = stats.mannwhitneyu(members, non_members)                # robustness
chi2, p, dof, _ = stats.chi2_contingency(pd.crosstab(df.insurance, df.returned))
```

### 2.4. Two-part PLV model.

Both parts are fitted with statsmodels formulas, and the predictions are combined with the smearing factor:

```python
part1 = smf.logit(f"any_spend ~ {RHS}", data=train).fit()
spenders = train[train.any_spend == 1]
part2 = smf.ols(f"log_plv ~ {RHS}", data=spenders).fit(cov_type="HC3")
smear = np.mean(np.exp(part2.resid))
pred  = part1.predict(test) * np.exp(part2.predict(test)) * smear
```

The first version of this stage used a single OLS on log(1 + PLV). Converting its predictions back to money gave a negative R² on the original scale, because the model could not handle the 60% of zero values. This problem led us to the two-part model, which is a good example of how checking the results changed the method.

### 2.5. Structural equation model.

The SEM is written in lavaan-style syntax and estimated with semopy. In this syntax, `=~` means "is measured by" and `~` means "is regressed on":

```python
model = semopy.Model("""
SQ  =~ SQ1 + SQ2 + SQ3 + SQ4
DC  =~ DC1 + DC2 + DC3 + DC4
AC  =~ AC1 + AC2 + AC3
PF  =~ PF1 + PF2 + PF3
SAT =~ SAT1 + SAT2 + SAT3
LOY =~ LOY1 + LOY2 + LOY3
SAT ~ SQ + DC + AC + PF
LOY ~ SAT""")
model.fit(items)
fit = semopy.calc_stats(model)      # chi2, CFI, TLI, RMSEA, ...
```

### 2.6. ARIMA forecasting.

The ARIMA model is fitted with SARIMAX from statsmodels, with the Fourier terms and Tet dummy as exogenous regressors. A small grid search over p and q picks the order with the lowest AIC:

```python
for p, q in itertools.product(range(4), range(4)):
    m = SARIMAX(train, exog=X_train, order=(p, 1, q), trend="t").fit(disp=False)
    grid.append({"p": p, "q": q, "AIC": m.aic})
```

### 2.7. Churn classifiers.

The four classifiers share one preprocessing step inside a scikit-learn pipeline, which guarantees that scaling and encoding are learned only from training folds:

```python
prep = ColumnTransformer([("num", StandardScaler(), NUMS),
                          ("cat", OneHotEncoder(drop="first"), CATS)])
model = Pipeline([("prep", prep), ("clf", MLPClassifier(hidden_layer_sizes=(64, 32),
                                                       early_stopping=True))])
cv_auc = cross_val_score(model, X_train, y_train, cv=StratifiedKFold(5), scoring="roc_auc")
```

## 3. Visualisations produced.

The pipeline automatically creates 14 figures and 21 tables. The figures are:
- histograms and box plots (Figures 2 and 3);
- a scatter plot (Figure 4) and the weekly time series (Figure 5);
- the survey correlation heat map (Figure 6);
- regression diagnostics and coefficient plots (Figures 7 and 8);
- the SEM path diagram (Figure 9);
- ACF/PACF plots, the forecast and residual plots (Figures 10–12);
- ROC curves, the confusion matrix and feature importance (Figures 13–14).

All are referenced in Chapter V.

# Chapter V. RESULTS AND DISCUSSION.

## 1. Descriptive statistics.

Table 3 summarises the main numeric variables. The average patient is 42 years old. One visit costs about 695 thousand VND, of which the patient pays 489 thousand on average after insurance and discounts. The median waiting time is 25 minutes. All money and time variables are clearly right-skewed (skewness between 1.7 and 3.1), as Figure 2 shows. Next-year spending (PLV) is the most extreme: its median is zero because 60% of the cohort spends nothing in 2025, while a few patients spend more than 15 million VND. These shapes justify the log transformation and the non-parametric robustness checks used later.

TABLE: Descriptive statistics of key variables.
| Variable | N | Mean | SD | Median | Min | Max | Skewness |
| Age (years) | 5,000 | 42.17 | 14.19 | 42.0 | 18 | 85 | 0.25 |
| Visit cost ('000 VND) | 24,872 | 694.61 | 419.98 | 597.0 | 67 | 4,977 | 1.70 |
| Out-of-pocket ('000 VND) | 24,872 | 488.99 | 331.31 | 404.0 | 40 | 4,069 | 2.01 |
| Waiting time (min) | 24,872 | 29.12 | 20.00 | 24.6 | 0.7 | 248.8 | 1.65 |
| Visits per patient to 2024 | 3,070 | 4.28 | 4.02 | 3.0 | 1 | 34 | 2.20 |
| PLV 2025 ('000 VND) | 3,070 | 942.01 | 1,817.93 | 0.0 | 0 | 19,412 | 3.09 |

![Distributions of patient age, out-of-pocket payment per visit and waiting time.](f1_histograms.png){6.2}

By department (Figure 3), Cardiology and Dental are the most expensive, and General Medicine is the cheapest but has the longest waiting times. The patient base is 55% female, 66% insured, 31% chronic and 30% programme members. Walk-in is the most common acquisition channel (45%).

![Visit cost and waiting time by department (outliers hidden).](f2_boxplots.png){6.2}

Figure 4 shows a clear positive relationship between the number of visits up to 2024 and spending in 2025, with chronic patients concentrated at the top. Figure 5 shows the weekly number of visits. The clinic grows from about 50 to about 300 visits per week. Every year there is a peak in winter, a trough in mid-year, and a sharp drop during Tet week.

![Past visit frequency versus next-year spending, coloured by chronic condition.](f3_scatter_freq_plv.png){4.6}

![Weekly visits, January 2023 to December 2025.](f4_weekly_visits.png){6.2}

Finally, Figure 6 shows the correlations between the 20 survey items. Items of the same construct correlate strongly with each other, forming visible blocks along the diagonal. Satisfaction and loyalty items correlate with all other constructs. This is a first sign that the measurement model will work.

![Spearman correlations between the 20 survey items.](f5_survey_corr.png){4.6}

## 2. Hypothesis tests.

Table 4 lists all test results.

TABLE: Results of the hypothesis tests (α = 0.05).
| Hypothesis | Test | Statistic | p-value | Effect size | Decision |
| H1 Spend: programme vs. not | Welch t | 5.63 | < 0.001 | d = 0.37 | Reject H₀ |
| H1 robustness | Mann–Whitney U | 246,922.5 | < 0.001 | – | Reject H₀ |
| H2 Return × insurance | χ²(1) | 1.58 | 0.208 | V = 0.02 | Fail to reject |
| H2b Return × chronic | χ²(1) | 72.46 | < 0.001 | V = 0.15 | Reject H₀ |
| H3 Return × channel | χ²(2) | 0.25 | 0.882 | V = 0.01 | Fail to reject |
| H4 Wait × department | ANOVA F | 491.58 | < 0.001 | η² = 0.073 | Reject H₀ |
| H4 robustness | Kruskal–Wallis H | 2,141.82 | < 0.001 | – | Reject H₀ |
| H5 Satisfaction: programme vs. not | Welch t | 0.19 | 0.852 | d = 0.01 | Fail to reject |

The results can be interpreted as follows:

- **H1 is supported.** Programme members spent 1.82 million VND in 2024 on average, compared with 1.09 million for non-members (medians 816 vs. 302 thousand). The effect is small to medium (d = 0.37). The Mann–Whitney test confirms it, so the result does not depend on the skewed distribution.
- **H2b is supported.** 48.7% of chronic patients returned in the first half of 2025, compared with 32.6% of other patients.
- **H4 is supported, but the effect is modest.** Departments explain only 7.3% of the variation in waiting time. The Levene test shows unequal variances, which is why the Kruskal–Wallis test is also reported. It gives the same conclusion.
- **H2, H3 and H5 are not supported.** Insurance, acquisition channel and programme membership show no significant relationship with returning or with satisfaction. For H5 this agrees with the simulation, where the programme affects satisfaction only indirectly through price fairness, an effect of about 0.06 standard deviations that is too small to detect with this sample.

It is worth noting that not all hypotheses are confirmed. A "failure to reject" is also a useful result for management. For example, there is no evidence that online patients are less loyal than walk-in patients, so there is no reason to change the marketing mix on this basis.

## 3. Regression: Patient Lifetime Value.

### 3.1. Coefficients and interpretation.

Table 5 shows the main coefficients of both parts of the model.

TABLE: Two-part PLV model – selected coefficients (Part 1: odds ratios; Part 2: % change in spending).
| Variable | Part 1 OR | Part 1 p | Part 2 % change | Part 2 p |
| Insured | 1.29 | 0.055 | −24.7% | < 0.001 |
| Chronic condition | 1.38 | 0.021 | +74.2% | < 0.001 |
| Care programme | 1.34 | 0.020 | +30.2% | < 0.001 |
| Age (per year) | 1.00 | 0.955 | +0.5% | 0.020 |
| log frequency | 0.84 | 0.176 | +27.6% | < 0.001 |
| log average spend | 1.17 | 0.230 | +50.7% | < 0.001 |
| Recency (per month) | 0.61 | < 0.001 | +2.1% | 0.153 |
| Tenure (per month) | 1.04 | 0.025 | −3.1% | < 0.001 |
| Average wait (per minute) | 1.00 | 0.939 | −0.1% | 0.544 |
| Model fit | pseudo-R² = 0.41 | | R² = 0.29 (n = 978) | |

**Part 1 (will the patient spend anything?)** is dominated by recency. Each extra month since the last visit multiplies the odds of any spending in 2025 by 0.61. Chronic patients (OR = 1.38) and programme members (OR = 1.34) are more likely to come back and spend.

**Part 2 (how much, if they spend?)** shows that chronic patients spend 74% more and programme members 30% more. Insured patients spend 25% less out of pocket, as expected since insurance pays part of the bill. Patients who visited often and spent more per visit in the past also spend more in the future (Figure 7).

These results agree with the simulation rules. The true visit-rate multiplier for chronic patients is e^0.6 = 1.82, which lies inside the 95% confidence interval of the estimate (+53% to +98%). The insurance effect (−25%) is smaller than the pure 40% price discount, because insured patients also tend to be slightly more satisfied and stay a little longer, which partly offsets the lower price.

![Part 2 OLS coefficients on log(PLV) with 95% confidence intervals.](f7_plv_coefficients.png){5.0}

### 3.2. Assumption checks.

The model assumptions were checked as follows:
- **Multicollinearity:** the largest VIF is 3.9, well below the usual limit of 10.
- **Independence:** the Durbin–Watson statistic is 2.00, so the residuals are independent.
- **Normality:** the residuals are slightly left-skewed (skewness −0.57), and the Jarque–Bera test rejects exact normality. With almost 1,000 observations this has little effect on the coefficient tests.
- **Homoscedasticity:** the Breusch–Pagan test (p = 0.043) shows mild heteroscedasticity, which is why robust HC3 standard errors are used.

The left and middle panels of Figure 8 confirm that the residuals have no clear pattern and are close to normal.

### 3.3. Predictive performance.

Table 6 compares the models on the 614 test patients. The two-part model reduces the RMSE from 1,836 to 1,422 thousand VND and explains 40% of the variance in PLV. The random forest performs almost identically (R² = 0.39) but cannot provide interpretable coefficients. The most useful result for managers is the decile chart in Figure 8 (right). Patients in the top 10% of predicted value spent 3.93 million VND on average in 2025, the second-highest decile spent 1.90 million, and the bottom two deciles spent almost nothing. The model therefore ranks patients well, which is what a retention campaign needs.

TABLE: PLV prediction on the test set ('000 VND).
| Model | RMSE | MAE | R² | Spearman ρ |
| Mean baseline | 1,835.6 | 1,277.9 | −0.002 | – |
| Two-part model | 1,421.9 | 793.6 | 0.399 | 0.672 |
| Random forest | 1,428.5 | 800.1 | 0.393 | 0.693 |

![PLV model diagnostics: residuals vs. fitted values, normal Q–Q plot, and mean actual PLV by predicted decile.](f6_plv_diagnostics.png){6.2}

## 4. Structural equation model.

### 4.1. Measurement model.

All six constructs are reliable and valid (Table 7):
- **Reliability:** Cronbach's α and composite reliability are between 0.74 and 0.83, above the 0.7 threshold.
- **Loadings:** all standardised loadings are between 0.65 and 0.81 and significant at p < 0.001 (Appendix D).
- **Convergent validity:** AVE is above 0.5 for every construct except access and convenience (0.48). This is acceptable because its composite reliability is above 0.7 [13].
- **Discriminant validity:** the Fornell–Larcker criterion holds. The largest correlation between two constructs (satisfaction and loyalty, 0.55) is smaller than the square root of the AVE of every construct.

TABLE: Reliability and validity of the measurement model.
| Construct | Items | Cronbach's α | CR | AVE | √AVE |
| Service quality (SQ) | 4 | 0.820 | 0.821 | 0.536 | 0.732 |
| Doctor communication (DC) | 4 | 0.824 | 0.826 | 0.544 | 0.738 |
| Access & convenience (AC) | 3 | 0.735 | 0.736 | 0.483 | 0.695 |
| Price fairness (PF) | 3 | 0.769 | 0.771 | 0.531 | 0.729 |
| Satisfaction (SAT) | 3 | 0.822 | 0.822 | 0.607 | 0.779 |
| Loyalty intention (LOY) | 3 | 0.775 | 0.776 | 0.537 | 0.733 |

### 4.2. Model fit.

The six-construct model fits the data very well. The single-factor model fits poorly (Table 8), so the six constructs are clearly distinct and common-method bias is not a concern. The perfect fit (CFI = 1.000, RMSEA = 0.000) is expected here, because the survey was generated from exactly this structure. With real survey data, CFI values around 0.95 would be normal and still acceptable.

TABLE: Fit of the six-construct SEM and the single-factor comparison model.
| Model | χ² | df | CFI | TLI | RMSEA |
| Six-construct SEM | 157.8 | 159 | 1.000 | 1.000 | 0.000 |
| Single factor (Harman) | 5,368.3 | 170 | 0.504 | 0.446 | 0.143 |
| Recommended threshold | – | – | ≥ 0.95 | ≥ 0.95 | ≤ 0.06 |

### 4.3. Structural paths.

Figure 9 and Table 9 show the estimated paths. All paths are positive and significant at p < 0.001:
- **Doctor communication** is the strongest driver of satisfaction (β = 0.37).
- **Service quality** follows closely (β = 0.35).
- **Access and convenience** (β = 0.27) and **price fairness** (β = 0.22) have smaller effects.

Together the four drivers explain 49% of the variance in satisfaction. Satisfaction strongly drives loyalty (β = 0.69), explaining 48% of its variance. Every estimate is within 0.04 of the true standardised value, which confirms that the method works as intended.

![SEM path diagram with standardised coefficients (*** p < 0.001).](f8_sem_path_diagram.png){5.8}

TABLE: Estimated vs. true standardised path coefficients.
| Path | Estimate | Std. error | True value | Absolute error |
| SAT ← SQ | 0.347 | 0.033 | 0.341 | 0.006 |
| SAT ← DC | 0.366 | 0.031 | 0.399 | 0.033 |
| SAT ← AC | 0.269 | 0.032 | 0.232 | 0.037 |
| SAT ← PF | 0.219 | 0.028 | 0.244 | 0.025 |
| LOY ← SAT | 0.692 | 0.032 | 0.680 | 0.012 |

### 4.4. From survey to behaviour.

The most practical question is whether what patients say predicts what they do. Among the 1,028 survey respondents who are also in the 2024 cohort, a one-standard-deviation increase in the loyalty score raises the odds of actually returning in the first half of 2025 by a factor of 1.60 (p < 0.001). This holds even after controlling for recency. A short loyalty survey therefore contains real, usable information about future visits.

## 5. Forecasting weekly demand.

### 5.1. Model identification.

The augmented Dickey–Fuller test cannot reject a unit root for the level of the series (p = 0.37), but the first difference is clearly stationary (p < 0.001), so d = 1. The ACF and PACF of the differenced series (Figure 10) show significant spikes only at the first one or two lags, suggesting a low-order model. The AIC grid search selects **ARIMA(2,1,1)** with Fourier terms and the Tet dummy (AIC = 1,294.7). The next-best models are within one AIC point.

![ACF and PACF of the first-differenced weekly series.](f9_acf_pacf.png){6.2}

TABLE: Estimated parameters of the ARIMA(2,1,1) model with Fourier terms.
| Parameter | Estimate | Std. error | z | p-value |
| Drift | 0.019 | 0.013 | 1.49 | 0.136 |
| sin₁ (yearly) | 13.84 | 8.34 | 1.66 | 0.097 |
| cos₁ (yearly) | 30.60 | 8.62 | 3.55 | < 0.001 |
| sin₂ | −5.11 | 4.90 | −1.04 | 0.297 |
| cos₂ | −1.29 | 4.21 | −0.31 | 0.760 |
| Tet week | −60.69 | 6.44 | −9.43 | < 0.001 |
| AR(1) | −0.342 | 0.107 | −3.19 | 0.001 |
| AR(2) | −0.302 | 0.100 | −3.02 | 0.003 |
| MA(1) | −0.518 | 0.124 | −4.17 | < 0.001 |

The large positive cos₁ coefficient captures the winter peak. The Tet dummy shows that the clinic loses about 61 visits during the holiday week. The Ljung–Box test finds no remaining autocorrelation in the residuals (p = 0.90 at lag 10 and 0.99 at lag 20), and the residual plots in Figure 11 look like white noise.

![Residuals of the ARIMA model and their autocorrelation.](f11_arima_residuals.png){6.2}

### 5.2. Forecast accuracy.

On the 13 test weeks (October–December 2025), ARIMA achieves a mean absolute percentage error of 5.8% (Table 11), and all 13 actual values fall inside its 95% prediction interval. Holt–Winters is slightly more accurate (4.5%). Both are far better than the seasonal naive forecast (19.4%), which repeats last year's numbers and cannot follow the clinic's growth. Refitted on all data, ARIMA forecasts about 4,050 visits for the first quarter of 2026: roughly 310–330 per week, with a dip to about 260 in Tet week (Figure 12).

TABLE: Forecast accuracy on the last 13 weeks of 2025.
| Model | MAE | RMSE | MAPE (%) |
| ARIMA(2,1,1) + Fourier | 16.19 | 19.18 | 5.75 |
| Holt–Winters (additive) | 12.51 | 16.23 | 4.51 |
| Seasonal naive (t − 52) | 52.38 | 55.21 | 19.38 |

![Weekly visits with test-period forecasts and the Q1-2026 outlook (shaded areas: 95% prediction intervals).](f10_forecast.png){6.2}

## 6. Machine learning: churn prediction.

### 6.1. Model comparison.

Table 12 compares the four classifiers. All models reach a cross-validated AUC between 0.876 and 0.887 with very small standard deviations, so they all rank patients well and the differences between them are minor. **Logistic regression** has the best cross-validated AUC (0.887), test AUC (0.879), accuracy (0.805) and specificity (0.84). The random forest has the best sensitivity (0.80) and F1 score. The MLP neural network is the weakest on the test set.

TABLE: Churn classifiers – 5-fold cross-validation and test-set performance.
| Model | CV AUC (sd) | Test AUC | Accuracy | Precision | Sensitivity | Specificity | F1 |
| Logistic regression | 0.887 (0.006) | 0.879 | 0.805 | 0.890 | 0.783 | 0.840 | 0.833 |
| Random forest | 0.885 (0.007) | 0.878 | 0.801 | 0.868 | 0.804 | 0.797 | 0.835 |
| Gradient boosting | 0.876 (0.007) | 0.868 | 0.782 | 0.851 | 0.789 | 0.771 | 0.818 |
| MLP neural network | 0.879 (0.011) | 0.859 | 0.767 | 0.853 | 0.757 | 0.784 | 0.802 |

![ROC curves of the four classifiers and confusion matrix of logistic regression (test set).](f12_roc_confusion.png){6.2}

The confusion matrix in Figure 13 shows how the best model performs on the 614 test patients:
- 300 of 383 churners are correctly flagged;
- 194 of 231 returning patients are correctly identified;
- only 37 loyal patients would be contacted unnecessarily.

### 6.2. What drives churn.

Permutation importance (Figure 14) shows that **recency** alone accounts for almost all of the predictive power: shuffling it lowers the test AUC by 0.34. Visit frequency and chronic condition follow at a much lower level. The logistic regression odds ratios tell the same story. Each standard deviation of recency (about six and a half months) multiplies the odds of churn by about 16, while being chronic (OR = 0.72) or a programme member (OR = 0.76) lowers them.

![Permutation importance of the features in the logistic regression model.](f13_feature_importance.png){4.6}

### 6.3. Why the simple model wins.

Logistic regression performs as well as the more complex models because the main relationship (more months since the last visit means higher churn risk) is simple and almost monotonic. With 3,070 patients and 14 features, a neural network has little extra structure to learn and is more prone to overfitting. This agrees with the literature [3], [25]. For a clinic, the simpler model is also better in practice: managers can understand and trust it, and it is easy to implement in a spreadsheet or a booking system.

## 7. Summary of model comparisons.

Table 13 brings together the best model of each stage and the key metric.

TABLE: Summary of the best model in each analysis stage.
| Stage | Best model | Key metric | Benchmark |
| Inferential | Welch t / χ² / ANOVA | 3 of 6 hypotheses supported (H1, H2b, H4) | – |
| Regression (PLV) | Two-part model | Test R² = 0.40 | Mean baseline R² = 0.00 |
| SEM | Six-construct model | CFI = 1.00, RMSEA = 0.00 | Single factor CFI = 0.50 |
| Forecasting | Holt–Winters (ARIMA close) | MAPE = 4.5% (5.8%) | Seasonal naive 19.4% |
| ML (churn) | Logistic regression | CV AUC = 0.887 | MLP 0.879 |

## 8. Practical implications.

**For business (marketing, sales, retention):**
- PLV scores make it possible to rank all patients by expected value. A retention campaign aimed at the top three deciles would reach patients who generate most of the next year's revenue.
- Recency is the clearest warning sign. Patients who have not visited for about three months should receive a reminder or a follow-up call.
- Care-programme members spend more and are more likely to return, so the programme is worth promoting, especially to chronic patients.
- The acquisition channel does not affect loyalty, so marketing can choose channels on cost alone.

**For healthcare (treatment, patient care):**
- Doctor communication is the strongest driver of satisfaction. Communication training for doctors is likely to bring the largest improvement in satisfaction and, through loyalty, in continuity of care.
- For chronic patients, returning regularly is also medically important. The churn model can identify chronic patients at risk of dropping out of follow-up care.
- Weekly forecasts allow the clinic to add doctors and nurses for the January flu peak and reduce staff in Tet week. This shortens waiting times, which also improves the access dimension of satisfaction.

# Chapter VI. CONCLUSION AND RECOMMENDATIONS.

## 1. Summary of findings.

This project built a complete, reproducible analytics workflow for a simulated private outpatient clinic. In one connected study, it applied all six method families required by the course to answer three management questions:
- **Who is valuable?** The two-part PLV model explains 40% of next-year spending and ranks patients clearly from no spending to about 4 million VND.
- **What drives satisfaction and loyalty?** Doctor communication and service quality matter most, and loyalty measured in a survey predicts real return visits.
- **How much demand, and who will leave?** Weekly visits can be forecast with about 5% error, and churn can be predicted with an AUC near 0.89, mainly from the time since the last visit.

Because the true effects were known, we could also confirm that every method recovered them closely. Simple, interpretable models such as logistic regression and Holt–Winters performed as well as or better than complex ones.

## 2. Recommendations for clinics and hospitals.

- Score every patient's expected value each quarter with the two-part model and focus retention budgets on the top deciles.
- Set up an automatic reminder when a patient's last visit is more than about three months ago, giving priority to chronic patients.
- Promote the follow-up care programme to chronic patients.
- Invest in doctor communication training and consistent service quality before considering price cuts.
- Reduce waiting times in General Medicine with better scheduling.
- Plan staffing with a weekly forecast that is updated every month.
- Run a short satisfaction survey regularly, since loyalty scores carry real information about future visits.

## 3. Limitations.

- **Simulated data.** The effect sizes reflect our assumptions, not real Vietnamese clinics, and the near-perfect SEM fit would not occur with a real survey. The results show that the *methods* work. They do not prove *facts* about real patients.
- **Survey sampling.** Respondents were chosen at random. In reality, satisfied patients are more likely to answer surveys.
- **Fixed windows.** Churn is defined with a fixed six-month window, and the models do not use information that changes over time.
- **Short series.** The time series covers only three years, which limits the estimation of yearly seasonality.
- **One-person project.** All stages were carried out by a single student, so the work could not be cross-checked by team members. It was instead checked against the ground truth and by re-running all code.

## 4. Future work.

- Apply the same code to real, anonymised data from a partner clinic.
- Add **explainable AI** tools such as SHAP values, so that each churn prediction comes with a reason that a receptionist or doctor can understand.
- Model churn as a time-to-event outcome with **survival analysis** (for example, Cox regression).
- Study **ethical AI** issues: audit the models for fairness across age, gender and insurance groups, protect patient privacy, and keep humans responsible for decisions about care.
- Turn the workflow into a simple dashboard for clinic managers.

## 5. Lessons learned.

- Checking results is part of modeling. The first PLV model gave a negative R², and understanding why led to the two-part model.
- Not every hypothesis is confirmed, and that is a valid result.
- A clear, reproducible project structure (one script per stage, all numbers saved to files) made it much easier to write the report and the paper without copying mistakes.
- More complex models are not automatically better. The value of a model for a business depends as much on whether people can understand it as on its accuracy.

# REFERENCE

REF: S. Gupta, D. Hanssens, B. Hardie, W. Kahn, V. Kumar, N. Lin, N. Ravishanker, and S. Sriram, "Modeling customer lifetime value," Journal of Service Research, vol. 9, no. 2, pp. 139–155, 2006.
REF: F. F. Reichheld and W. E. Sasser, "Zero defections: Quality comes to services," Harvard Business Review, vol. 68, no. 5, pp. 105–111, 1990.
REF: W. Verbeke, K. Dejaeger, D. Martens, J. Hur, and B. Baesens, "New insights into churn prediction in the telecommunication sector: A profit driven data mining approach," European Journal of Operational Research, vol. 218, no. 1, pp. 211–229, 2012.
REF: W. Raghupathi and V. Raghupathi, "Big data analytics in healthcare: Promise and potential," Health Information Science and Systems, vol. 2, p. 3, 2014.
REF: A. Rajkomar, J. Dean, and I. Kohane, "Machine learning in medicine," New England Journal of Medicine, vol. 380, no. 14, pp. 1347–1358, 2019.
REF: T. P. Morris, I. R. White, and M. J. Crowther, "Using simulation studies to evaluate statistical methods," Statistics in Medicine, vol. 38, no. 11, pp. 2074–2102, 2019.
REF: P. S. Fader, B. G. S. Hardie, and K. L. Lee, "RFM and CLV: Using iso-value curves for customer base analysis," Journal of Marketing Research, vol. 42, no. 4, pp. 415–430, 2005.
REF: N. Duan, W. G. Manning, C. N. Morris, and J. P. Newhouse, "A comparison of alternative models for the demand for medical care," Journal of Business & Economic Statistics, vol. 1, no. 2, pp. 115–126, 1983.
REF: N. Duan, "Smearing estimate: A nonparametric retransformation method," Journal of the American Statistical Association, vol. 78, no. 383, pp. 605–610, 1983.
REF: S. S. Jones, A. Thomas, R. S. Evans, S. J. Welch, P. J. Haug, and G. L. Snow, "Forecasting daily patient volumes in the emergency department," Academic Emergency Medicine, vol. 15, no. 2, pp. 159–170, 2008.
REF: L. F. Dantas, J. L. Fleck, F. L. Cyrino Oliveira, and S. Hamacher, "No-shows in appointment scheduling – a systematic literature review," Health Policy, vol. 122, no. 4, pp. 412–421, 2018.
REF: A. Parasuraman, V. A. Zeithaml, and L. L. Berry, "SERVQUAL: A multiple-item scale for measuring consumer perceptions of service quality," Journal of Retailing, vol. 64, no. 1, pp. 12–40, 1988.
REF: C. Fornell and D. F. Larcker, "Evaluating structural equation models with unobservable variables and measurement error," Journal of Marketing Research, vol. 18, no. 1, pp. 39–50, 1981.
REF: J. F. Hair, W. C. Black, B. J. Babin, and R. E. Anderson, Multivariate Data Analysis, 8th ed. Andover, UK: Cengage, 2019.
REF: L. Hu and P. M. Bentler, "Cutoff criteria for fit indexes in covariance structure analysis: Conventional criteria versus new alternatives," Structural Equation Modeling, vol. 6, no. 1, pp. 1–55, 1999.
REF: B. L. Welch, "The generalization of 'Student's' problem when several different population variances are involved," Biometrika, vol. 34, no. 1/2, pp. 28–35, 1947.
REF: L. Breiman, "Random forests," Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.
REF: A. A. Igolkina and G. Meshcheryakov, "semopy: A Python package for structural equation modeling," Structural Equation Modeling, vol. 27, no. 6, pp. 952–963, 2020.
REF: P. M. Podsakoff, S. B. MacKenzie, J.-Y. Lee, and N. P. Podsakoff, "Common method biases in behavioral research: A critical review of the literature and recommended remedies," Journal of Applied Psychology, vol. 88, no. 5, pp. 879–903, 2003.
REF: G. E. P. Box, G. M. Jenkins, G. C. Reinsel, and G. M. Ljung, Time Series Analysis: Forecasting and Control, 5th ed. Hoboken, NJ: Wiley, 2015.
REF: R. J. Hyndman and G. Athanasopoulos, Forecasting: Principles and Practice, 3rd ed. Melbourne, Australia: OTexts, 2021. [Online]. Available: https://otexts.com/fpp3/
REF: P. R. Winters, "Forecasting sales by exponentially weighted moving averages," Management Science, vol. 6, no. 3, pp. 324–342, 1960.
REF: J. H. Friedman, "Greedy function approximation: A gradient boosting machine," The Annals of Statistics, vol. 29, no. 5, pp. 1189–1232, 2001.
REF: F. Pedregosa et al., "Scikit-learn: Machine learning in Python," Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011; and S. Seabold and J. Perktold, "Statsmodels: Econometric and statistical modeling with Python," in Proc. 9th Python in Science Conf., 2010.
REF: L. Grinsztajn, E. Oyallon, and G. Varoquaux, "Why do tree-based models still outperform deep learning on typical tabular data?" in Advances in Neural Information Processing Systems (NeurIPS), Datasets and Benchmarks Track, 2022.

# APPENDIX

## A. Source code, dataset and demo video.

- GitHub repository: https://github.com/Langl3y/STAT3013.R11.CTTT_Group10
- Dataset: https://github.com/Langl3y/STAT3013.R11.CTTT_Group10/tree/main/data
- Demo video (15 minutes): <ADD LINK>

## B. Plagiarism check report.

The Turnitin similarity report (required ≤ 10%) is attached as a separate screenshot file. Its result is also inserted here:

<INSERT TURNITIN SCREENSHOT – similarity: __%>

## C. AI-generated content audit.

An AI assistant (Claude, Anthropic) was used during this project. The table below lists where it was used and how its output was checked. The AI-detection screenshot (Grammarly/QuillBot) is attached as a separate file. A full one-page AI Usage Disclosure Statement is submitted with the project.

TABLE: AI usage and human verification by project component.
| Component | AI assistance | Human verification and editing |
| Topic and method choice | Suggested options that fit the course outline | Student chose the topic and approved the design |
| Simulation and analysis code | Drafted the Python scripts | Student ran all code, checked outputs and fixed parameters |
| Numbers, tables and figures | None (generated by the code) | Every number traced to outputs/results.json |
| Report and paper text | Drafted structure and first versions | Student rewrote the text and checked every claim and reference |
| References | Proposed well-known sources | Student verified each reference on Google Scholar |
| Slides and demo | Drafted outline and script | Student recorded the narrated demo personally |

## D. Additional tables.

TABLE: Standardised factor loadings of the measurement model (all p < 0.001; the first item of each construct is the reference item).
| Construct | Item 1 | Item 2 | Item 3 | Item 4 |
| SQ | 0.766 | 0.734 | 0.663 | 0.760 |
| DC | 0.797 | 0.759 | 0.719 | 0.670 |
| AC | 0.730 | 0.707 | 0.645 | – |
| PF | 0.801 | 0.712 | 0.666 | – |
| SAT | 0.807 | 0.771 | 0.759 | – |
| LOY | 0.774 | 0.748 | 0.673 | – |

TABLE: Fornell–Larcker criterion (diagonal: √AVE; off-diagonal: correlations between constructs).
| | SQ | DC | AC | PF | SAT | LOY |
| SQ | 0.732 | | | | | |
| DC | 0.367 | 0.738 | | | | |
| AC | −0.012 | 0.016 | 0.695 | | | |
| PF | −0.016 | 0.030 | −0.017 | 0.729 | | |
| SAT | 0.410 | 0.439 | 0.209 | 0.170 | 0.779 | |
| LOY | 0.274 | 0.295 | 0.139 | 0.119 | 0.553 | 0.733 |
