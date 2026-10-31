# Evan Miller on A/B testing and statistics: a brief for agent evaluation

Fetched 2026-10-31. Every page below was fetched with WebFetch unless it is marked **unverified**. Formulas are copied from the fetched page. LLM-agent applications are my inference from those formulas, not Miller's claims, except in the arXiv eval paper (2411.00640), which is about LLM evals.

## Index check

The index lists these A/B and statistics items (https://www.evanmiller.org/):
Adding Error Bars to Evals (arXiv), Likelihood-ratio inference on differences in quantiles (arXiv), Formulas for Bootstrapping Sample Medians, You Can't Spell CUPED Without Frisch-Waugh-Lovell, Simple Sequential A/B Testing, Formulas for Bayesian A/B Testing, The Low Base Rate Problem, A/B Testing Duration Data, Lazy Assignment and A/B Testing, Announcing Evan's Awesome A/B Tools, Linear Regression For Fun And Profit, How Not To Run An A/B Test (https://www.evanmiller.org/).
The ratings section lists How Not To Sort By Average Rating, Bayesian Average Ratings, Ranking Items With Star Ratings, Ranking News Items With Upvotes, Deriving the Reddit Formula, and Rank Hotness With Newton's Law of Cooling. The applied-math section lists Statistical Formulas for Programmers and How To Read an Unlabeled Sales Chart (https://www.evanmiller.org/).

Titles from the brief, checked against the index:
- "Bayesian A/B Testing" and "Formulas for Bayesian A/B Testing" are one page, https://www.evanmiller.org/bayesian-ab-testing.html. Other pages link to it under the shorter name (https://www.evanmiller.org/how-not-to-run-an-ab-test.html).
- "Deriving the Bayesian A/B formulas" is not a separate article. The derivations are subsections of the Bayesian page (https://www.evanmiller.org/bayesian-ab-testing.html).
- **unverified.** "A/B Testing Rigorously (without losing your job)" is not on the index. A web search found the title in an unrelated link list with no author attached (WebSearch, 2026-10-31).
- **unverified.** "Why Multi-armed Bandit algorithms are not better than A/B testing" is not on the index, and a search found no Evan Miller page with that title (WebSearch, 2026-10-31). I believe it is someone else's post (Chris Stucchio is my guess, unverified). Do not attribute it to Miller.
- **unverified.** "A/B Testing with Boundaries" is not on the index and a search did not find it (WebSearch, 2026-10-31).

On the index but missing from the brief's list: Adding Error Bars to Evals, Likelihood-ratio inference on quantiles, Bootstrapping Sample Medians, CUPED/FWL, A/B Testing Duration Data, Announcing Evan's Awesome A/B Tools, Linear Regression For Fun And Profit, How Not To Sort By Average Rating, Statistical Formulas for Programmers (https://www.evanmiller.org/).

## Calculators and tools

All tools are listed at https://www.evanmiller.org/ab-testing/.
- **Sample Size Calculator** (https://www.evanmiller.org/ab-testing/sample-size.html). It takes a baseline rate, an absolute or relative MDE, power, and alpha, and returns the sample size per variation. The page states no formula.
- **Sequential Sampling Calculator** (https://www.evanmiller.org/ab-testing/sequential.html). It takes a baseline rate, MDE, power, and alpha. It returns the total conversions N and the lead d the treatment needs. The test is one-sided.
- **Chi-Squared Test** (https://www.evanmiller.org/ab-testing/chi-squared.html). It takes successes and trials for each of two groups, and returns a CI per group plus a verdict with a p-value.
- **Two-Sample T-Test** (https://www.evanmiller.org/ab-testing/t-test.html). It takes raw data or summary statistics (mean, count, SD) for each group (https://www.evanmiller.org/announcing-evans-awesome-ab-tools.html).
- **Poisson Means Test** (https://www.evanmiller.org/ab-testing/poisson-means.html). It takes events and days for each of two samples, and returns rate CIs and a p-value.
- **Survival Curves** (https://www.evanmiller.org/ab-testing/survival-curves.html). It takes two lists of survival times, and returns Kaplan-style curves and a log-rank z and p. The page does not say whether it handles censoring.
- **Survival Means Test** (https://www.evanmiller.org/ab-testing/survival-times.html). It tests whether either group stays longer when only the mean is known (https://www.evanmiller.org/ab-testing-duration-data.html).
- **A/B Buddy**, an iOS sample size app (https://itunes.apple.com/us/app/a-b-buddy/id1446129030, link taken from https://www.evanmiller.org/).
- **SampleMedianBootstrap**, code for the median bootstrap (https://github.com/evanmiller/SampleMedianBootstrap, linked from https://www.evanmiller.org/bootstrapping-sample-medians.html).

## Articles

### 1. How Not To Run An A/B Test
URL: https://www.evanmiller.org/how-not-to-run-an-ab-test.html
- **Summary.** Significance math assumes a sample size fixed in advance. Stopping when the dashboard first shows significance gives noise extra chances to look like a winner, so the real false-positive rate climbs far above the nominal one. Fix the sample size first. If you must look early, use a sequential or Bayesian design. Dashboards should report the detectable effect at the current n instead of live significance (https://www.evanmiller.org/how-not-to-run-an-ab-test.html).
- **Rule.** The rule of thumb is `n = 16 σ² / δ²` per group, with `σ² = p(1-p)` for a binary metric. The effect detectable at the current n is `δ = (t_{α/2} + t_β) σ √(2/n)` (https://www.evanmiller.org/how-not-to-run-an-ab-test.html).
- **Peeking numbers.** In a simulation with a 50% rate, no real effect, and stopping at p<0.05 or 150 observations, 26.1% of tests reported a winner (https://www.evanmiller.org/how-not-to-run-an-ab-test.html). To keep a true 5% rate, the per-look threshold must drop to 2.9% for 1 peek, 2.2% for 2, 1.8% for 3, 1.4% for 5, and 1.0% for 10 (https://www.evanmiller.org/how-not-to-run-an-ab-test.html).
- **Agents.** A team watching task-success rates on a live dashboard for a prompt-vs-prompt or model-vs-model change, and shipping when the graph turns green, is running this flawed experiment. Fix n before launch from `16 p(1-p)/δ²`. At p=0.7 success and δ=0.03, that is about 3,730 sessions per arm (my arithmetic). For judge scores, latency, or cost, use the sample variance as σ². The dashboard should show "detectable δ at current n" rather than a p-value.

### 2. Simple Sequential A/B Testing
URL: https://www.evanmiller.org/sequential-ab-testing.html
- **Summary.** Miller treats T−C, the difference in successes between treatment and control, as a random walk and borrows gambler's-ruin boundaries. The test can stop early for a real winner without inflating false positives. It ignores failures and you can run it by hand. It wins for small lifts at low base rates. It loses when there is no effect, and can lose when the lift is large (https://www.evanmiller.org/sequential-ab-testing.html).
- **Rule (one-sided).** Pick N in advance and split 50/50. If `T − C` reaches `2√N`, stop and declare the treatment the winner. If `T + C` reaches `N`, stop with no winner. For a two-sided test, use `2.25√N` in both directions (https://www.evanmiller.org/sequential-ab-testing.html).
- **Table (α=0.05, power 0.8, 1% baseline).** A 50% lift needs N=170 with d*=26. A 20% lift needs N=808 with d*=56. A 10% lift needs N=2,922 with d*=106. Expected savings against a fixed-sample test are −13.9%, 10.0%, and 17.4% (https://www.evanmiller.org/sequential-ab-testing.html).
- **When it wins.** The test tends to beat a fixed-sample design when `1.5p + δ < 36%` (https://www.evanmiller.org/sequential-ab-testing.html).
- **Agents.** This is the right tool for "watch the dashboard" teams, because each new success event updates T or C and the boundary check is valid at every look. It fits rare-success outcomes best. Examples are "agent completed a purchase" or "user accepted the PR", and the inverted outcome "agent caused an incident" counted as the success event. It fits poorly when task success is about 70%, because 1.5p already exceeds 36%. There, use a fixed-n test or invert the metric to the failure rate when failures are rare (inferred from the 36% rule above).

### 3. Formulas for Bayesian A/B Testing (includes the derivations)
URL: https://www.evanmiller.org/bayesian-ab-testing.html
- **Summary.** The page gives closed-form posterior probabilities that one variant beats another. It covers binary outcomes with a Beta posterior and count outcomes with a Gamma posterior, for 2, 3, and 4 variants, with Julia code and a derivation for each case (https://www.evanmiller.org/bayesian-ab-testing.html).
- **Binary formula.** Set `α = successes+1` and `β = failures+1`. Then `Pr(p_B > p_A) = Σ_{i=0}^{α_B−1} B(α_A+i, β_A+β_B) / [(β_B+i) B(1+i, β_B) B(α_A, β_A)]` (https://www.evanmiller.org/bayesian-ab-testing.html).
- **Count formula.** Set α to the event count and β to the exposure. Then `Pr(λ_1 > λ_2) = Σ_{k=0}^{α_1−1} (β_1+β_2)^{−(k+α_2)} β_1^k β_2^{α_2} / [(k+α_2) B(k+1, α_2)]` (https://www.evanmiller.org/bayesian-ab-testing.html).
- **Three variants.** `Pr(p_C > max{p_A,p_B}) = 1 − Pr(p_A>p_C) − Pr(p_B>p_C) + ΣΣ B(i+j+α_C, β_A+β_B+β_C)/[(β_A+i)(β_B+j)B(1+i,β_A)B(1+j,β_B)B(α_C,β_C)]` (https://www.evanmiller.org/bayesian-ab-testing.html).
- **Caveats.** Compute in log-beta to avoid overflow. Iterate over the smaller count. The page assumes a uniform prior, and an informative prior must keep α and β integers (https://www.evanmiller.org/bayesian-ab-testing.html). The page says no fixed sample size is needed, and points to the other articles for the peeking problem (https://www.evanmiller.org/bayesian-ab-testing.html).
- **Agents.** For model-vs-model task success, report `Pr(B better)` from success and failure counts. For counts per exposure, use the Gamma version. Examples are tool-call errors per 1,000 turns, escalations per session-hour, and hallucination flags per 1k tokens, with α set to events and β to exposure. The 3-variant formula covers routing among three prompts. Do not treat `Pr(B>A) > 0.95` as license to peek freely. Miller does not claim that, and his sequential page is the fix for peeking.

### 4. The Low Base Rate Problem
URL: https://www.evanmiller.org/the-low-base-rate-problem.html
- **Summary.** At a low base rate, a test is underpowered unless it is very large, so its negative results mean little. Set the effect size and n beforehand. If n is impractical, redesign the test to raise the base rate. Always ask what power a null result had (https://www.evanmiller.org/the-low-base-rate-problem.html).
- **Numbers (per branch, 10% relative lift, 80% power).** A 50% base rate needs 1,567. 20% needs 6,347. 10% needs 14,313. 5% needs 30,244. 1% needs 157,697. 0.1% needs 1,591,535 (https://www.evanmiller.org/the-low-base-rate-problem.html). A 50% lift off a 1% base still needs about 6,000 per branch (https://www.evanmiller.org/the-low-base-rate-problem.html).
- **Agents.** Rare failures are the usual agent safety metric: destructive tool calls, data leaks, policy violations, infinite loops. If one of these happens at 0.1%, an online A/B test cannot show that a new model cuts it by 10% without about 1.6M sessions per arm (table above). Raise the base rate in one of three ways. You can measure a more common precursor, such as "attempted a destructive command" or "judge flagged risk". You can run the comparison offline on an adversarial set where the rate is about 20 to 50%. You can lazily assign only the risky sessions (see 5). A "no regression" claim on a rare failure needs its power stated.

### 5. Lazy Assignment and A/B Testing
URL: https://www.evanmiller.org/lazy-assignment-and-ab-testing.html
- **Summary.** Assign subjects at the point where they are exposed to the change, not at entry. Unexposed subjects count as failures in both arms and dilute the effect (https://www.evanmiller.org/lazy-assignment-and-ab-testing.html).
- **Rule.** The 2×2 chi-squared sample size is `n = θ_{α,β}[δ²/(p(1−p))]⁻¹`. The efficiency gain from lazy assignment is `E = (1−p₁)/(1−p₂)`, where p₁ is the rate from entry and p₂ is the rate from exposure (https://www.evanmiller.org/lazy-assignment-and-ab-testing.html). In his checkout example, assigning at entry needs 60,488 visitors and assigning at checkout needs 31,340 (https://www.evanmiller.org/lazy-assignment-and-ab-testing.html).
- **Agents.** Many products send only some sessions down the agent path, for example only queries the classifier routes to the coding agent, or only turns that call a tool. Randomize when the router hands off to the agent, not when the user logs in. Analyze over sessions that reached the agent. If assignment happens upstream, the effect is diluted and the needed n grows. Log `exposure_ts` separately from `session_start` so the analysis can filter to exposed sessions. When a variant changes the router itself, exposure is no longer independent of arm, so you must assign upstream and accept the dilution (inferred).

### 6. A/B Testing Duration Data
URL: https://www.evanmiller.org/ab-testing-duration-data.html
- **Summary.** A t-test on mean visit length needs the SD, which analytics tools often omit. If leaving happens at a constant hazard, durations are exponential and `variance = mean²`, so SD ≈ mean. Report SDs alongside means (https://www.evanmiller.org/ab-testing-duration-data.html).
- **Agents.** Agent latency and time-to-resolution are durations. The exponential shortcut is a fallback only, because agent latency is usually right-skewed with heavy tails rather than exponential (my guess). Log raw per-session values and use the t-test, survival curves (https://www.evanmiller.org/ab-testing/survival-curves.html), or quantile methods (see 9). Sessions abandoned before resolution are censored observations (inferred).

### 7. You Can't Spell CUPED Without Frisch-Waugh-Lovell
URL: https://www.evanmiller.org/you-cant-spell-cuped-without-frisch-waugh-lovell.html
- **Summary.** By the FWL theorem, CUPED's two steps (residualize, then test) equal one regression of Y on the treatment indicator plus covariates. Adding indicators for every concurrent experiment ("VaReSE") removes variance that those experiments add (https://www.evanmiller.org/you-cant-spell-cuped-without-frisch-waugh-lovell.html).
- **Rule.** Fit `Y = μ + Zβ + T·1_treated + ε`, or with K experiments `Y = μ + Zβ + T_1 + … + T_K + ε`. The variance reduction is `Δ = Σ_k ¼T_k² / σ²_CUPED`. Sample size still uses `N = 16σ²/δ²` (https://www.evanmiller.org/you-cant-spell-cuped-without-frisch-waugh-lovell.html). The page does not give the textbook `θ = cov/var` form.
- **Agents.** Use pre-period covariates: user's past success rate, task difficulty or category, repo size, prompt length. Regress judge score or cost on the arm plus those covariates. Smaller residual variance gives a smaller n. When several prompt, model, and tool experiments run at once, add their arm indicators as regressors.

### 8. Formulas for Bootstrapping Sample Medians
URL: https://www.evanmiller.org/bootstrapping-sample-medians.html
- **Summary.** Under a Poisson bootstrap, the distribution of which sample point becomes the bootstrapped median has an exact Bessel-function form. It is lighter-tailed than Spotify's binomial approximation, so the binomial gives slightly conservative CIs (https://www.evanmiller.org/bootstrapping-sample-medians.html).
- **Rule.** The approximation is `Pr(y_i = τ̂_{1/2}) ≈ 2e^{−(n−1)} I_0(2√((n+1−i) i))`. Use scaled Bessel functions such as `scipy.special.jve` (https://www.evanmiller.org/bootstrapping-sample-medians.html).
- **Agents.** This gives a median-latency or median-cost CI per arm without resampling.

### 9. Likelihood-ratio inference on differences in quantiles (arXiv 2401.10233)
URL: https://arxiv.org/abs/2401.10233
- **Summary.** The paper gives a two-sample likelihood-ratio test and CI for a difference in quantiles. The conservative version needs no density estimate, and both versions use only four ranked values per sample (https://arxiv.org/abs/2401.10233).
- **Agents.** The main use is comparing p50 or p95 latency, or p95 cost, between agent variants. The abstract does not mention latency, so this use is inferred.

### 10. Adding Error Bars to Evals (arXiv 2411.00640)
URL: https://arxiv.org/abs/2411.00640 (full text https://arxiv.org/html/2411.00640)
- **Summary.** LLM evals are experiments over a super-population of questions. Report CLT standard errors, cluster when questions come in groups, cut variance by resampling answers or by using next-token probabilities, compare models on paired per-question differences, and run power analysis (https://arxiv.org/html/2411.00640).
- **Formulas.**
  - Standard error of the mean: `SE = √(Σ(s_i − s̄)²/(n(n−1)))`. For binary scores, `SE = √(s̄(1−s̄)/n)` (https://arxiv.org/html/2411.00640).
  - Clustered: `SE_cl = (SE² + (1/n²) Σ_c Σ_i Σ_{j≠i} (s_ic − s̄)(s_jc − s̄))^{1/2}` (https://arxiv.org/html/2411.00640).
  - Paired: `SE_{A−B} = √(SE_A² + SE_B² − 2 SE_A SE_B Corr(s_A, s_B))` (https://arxiv.org/html/2411.00640).
  - Resampling K answers per question: `Var(s_i) = σ_i²/K` (https://arxiv.org/html/2411.00640).
  - Power: `n = (z_{α/2} + z_β)² (ω² + σ_A²/K_A + σ_B²/K_B) / δ²`, with `ω² = Var(x_A) + Var(x_B) − 2Cov(x_A, x_B)` (https://arxiv.org/html/2411.00640).
- **Agents.** This is the offline counterpart of the online A/B section, and it is directly about LLMs. Run both agent variants on the same tasks and analyze per-task differences. Cluster SEs by task family or repo. Run K>1 trials per task when the agent is stochastic.

### 11. Statistical Formulas for Programmers
URL: https://www.evanmiller.org/statistical-formulas-for-programmers.html
- **Rules.**
  - Mean CI: `x̄ ± t SE`.
  - Welch t-test: `t = (x̄₁ − x̄₂)/√(s₁²/n₁ + s₂²/n₂)`, with Welch df.
  - Wilson interval for a proportion: `(p + z²/2N ± z√([p(1−p) + z²/4N]/N))/(1 + z²/N)`.
  - Chi-squared over O and E.
  - Poisson rate CI from inverse gamma.
  - Conditional two-Poisson test.
  - Kolmogorov-Smirnov one-, two-, and k-sample tests.
  - Regression slope with its SE (https://www.evanmiller.org/statistical-formulas-for-programmers.html).
- **Agents.** Use the Wilson interval for success rates on small task suites, KS to check whether a variant changes the whole judge-score distribution rather than only the mean, and the Poisson tests for error counts.

### 12. How Not To Sort By Average Rating
URL: https://www.evanmiller.org/how-not-to-sort-by-average-rating.html
- **Summary and rule.** Net votes and raw averages both mis-rank items. Sort by the Wilson lower bound `(p̂ + z²/2n − z√((p̂(1−p̂) + z²/4n)/n))/(1 + z²/n)` (https://www.evanmiller.org/how-not-to-sort-by-average-rating.html).
- **Agents.** Use it to rank agent variants, prompts, or tools on a leaderboard by thumbs-up rate without letting a variant with 5 votes top the list.

### 13. Bayesian Average Ratings
URL: https://www.evanmiller.org/bayesian-average-ratings.html
- **Summary and rule.** Use a Beta belief over the up/down share and a loss that penalizes over-ranking L times more than under-ranking. Sort by the X that solves `I_X(U+1, D+1) = 1/(1+L)`. With decay, use `I_X(U·2^{−t_U/H}, D·2^{−t_D/H}) = 1/(1+L)` (https://www.evanmiller.org/bayesian-average-ratings.html).
- **Agents.** Rank variants by a loss-aware quantile of the posterior. The half-life decay suits feedback on a prompt that keeps changing.

### 14. Ranking Items With Star Ratings
URL: https://www.evanmiller.org/ranking-items-with-star-ratings.html
- **Rule.** `S = Σ s_k (n_k+1)/(N+K) − z √[(Σ s_k² (n_k+1)/(N+K) − (Σ s_k (n_k+1)/(N+K))²)/(N+K+1)]`. This is a Dirichlet prior with one pseudo-vote per level, followed by a normal lower bound (https://www.evanmiller.org/ranking-items-with-star-ratings.html).
- **Agents.** Apply it directly to 1 to 5 LLM-judge or human rubric scores to get a conservative per-variant score that accounts for sample size.

### 15. Linear Regression For Fun And Profit
URL: https://www.evanmiller.org/linear-regression-for-fun-and-profit.html
- **Summary and rule.** Fit one β vector per experiment branch on user covariates and serve each user the branch with the highest predicted value. Use a Chow test for whether the branches differ, and avoid collinear dummies (https://www.evanmiller.org/linear-regression-for-fun-and-profit.html).
- **Agents.** This is the contextual-routing idea: route each task to the agent variant predicted best for its task category or language. It is also the closest thing Miller has written to bandit routing (inferred).

### 16. How To Read an Unlabeled Sales Chart
URL: https://www.evanmiller.org/how-to-read-an-unlabeled-sales-chart.html
- **Rule.** For Poisson counts, mean equals variance, so sales per pixel is `S = (n−1)P̄ / Σ(P_i − P̄)²`. The page does not discuss experiments (https://www.evanmiller.org/how-to-read-an-unlabeled-sales-chart.html).
- **Agents.** The use is marginal. Var ≫ mean in per-day agent error counts signals overdispersion, so the Poisson tests in 3 and 11 would be anti-conservative (inferred).

### Bandits (no Miller source)
- **unverified.** I found no Miller article on bandits. In the third-party material, the common critiques are biased arm estimates, starved losing arms, and no clean stopping rule (https://www.koji.so/docs/multi-armed-bandit-vs-ab-test, https://engineeringblog.yelp.com/2022/12/lessons-from-ab-testing-on-bandit-subjects.html).
- **Agents.** For routing traffic between agent variants, cite those critiques, or Miller's regression routing (15) as a contextual alternative. Do not cite Miller for the bandit claims.

## What a Python demo in the repo should implement from this

1. **`plan_sample_size.py`.**
   - Binary success: `n = 16 p(1−p)/δ²`, plus the exact `(z_{α/2}+z_β)²` form. It prints the low-base-rate table for rare failures (https://www.evanmiller.org/how-not-to-run-an-ab-test.html, https://www.evanmiller.org/the-low-base-rate-problem.html).
   - Judge scores: the paired power formula `n = (z_{α/2}+z_β)²(ω² + σ_A²/K_A + σ_B²/K_B)/δ²` (https://arxiv.org/html/2411.00640).
   - A `--exposure-rate` flag that applies the lazy-assignment efficiency `E = (1−p₁)/(1−p₂)` (https://www.evanmiller.org/lazy-assignment-and-ab-testing.html).
2. **`sequential_runner.py`.** It streams JSONL agent-session logs (`arm`, `success`, `exposure_ts`). It applies Miller's rule, declaring a winner if `T − C ≥ 2√N` (or `2.25√N` two-sided) and no winner if `T + C ≥ N`. It warns when `1.5p + δ ≥ 0.36` (https://www.evanmiller.org/sequential-ab-testing.html).
3. **`bayes_ab.py`.** It computes the closed-form `Pr(p_B > p_A)` in log-beta via `scipy.special.betaln`, the Gamma-Poisson `Pr(λ_1 > λ_2)` for errors per exposure, and the 3-arm formula for three prompts. A Monte Carlo cross-check serves as the test (https://www.evanmiller.org/bayesian-ab-testing.html).
4. **`peeking_simulator.py`.** It simulates A/A tests on agent success with a daily dashboard peek and should reproduce Miller's figure of about 26% false positives. It also shows that the sequential rule holds alpha (https://www.evanmiller.org/how-not-to-run-an-ab-test.html, https://www.evanmiller.org/sequential-ab-testing.html).
5. **`paired_eval_compare.py`.** It takes offline model-vs-model results over shared tasks and reports the paired SE, the clustered SE by task family, the effect of K trials per task, and the MDE at the current n (https://arxiv.org/html/2411.00640).
6. **`covariate_adjust.py`.** It runs the CUPED/FWL regression `Y ~ arm + pre-period covariates + other concurrent arms` with HC (robust) SEs on judge score or cost, and reports the variance reduction compared with the unadjusted test (https://www.evanmiller.org/you-cant-spell-cuped-without-frisch-waugh-lovell.html).

Optional seventh script: Wilson and star-rating lower bounds for a variant leaderboard (https://www.evanmiller.org/how-not-to-sort-by-average-rating.html, https://www.evanmiller.org/ranking-items-with-star-ratings.html).
