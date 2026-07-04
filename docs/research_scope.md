# Research Scope

This document outlines potential research directions for academic publication or further study.

## 1. Deep Clustering Comparison

Compare classical clustering (KMeans, GMM, HDBSCAN) against deep learning approaches:

- **DEC** (Deep Embedded Clustering) — Xie et al. 2016
- **VaDE** (Variational Deep Embedding) — Jiang et al. 2017
- **DCN** (Deep Clustering Network) — Yang et al. 2017
- **ClusterGAN** — Mukherjee et al. 2019

**Research question**: Do deep clustering methods produce more business-interpretable segments than classical methods on customer tabular data?

## 2. Contrastive Customer Representations

Apply SimCLR / MoCo / BYOL to customer feature vectors to learn representations where:
- Similar customers (same true segment) have high cosine similarity
- Dissimilar customers (different segments) have low cosine similarity

Then cluster in the learned embedding space.

## 3. Causal Inference & Uplift Modeling

Train per-segment uplift models using:
- **T-learner**: separate models for treatment vs. control
- **S-learner**: single model with treatment indicator
- **X-learner**: Künzel et al. 2019

Estimate Conditional Average Treatment Effect (CATE) per customer per campaign, enabling true ROI optimization.

## 4. Graph Neural Network Segmentation

Build a customer-product bipartite graph:
- Nodes: customers + products
- Edges: purchase events weighted by amount

Apply GraphSAGE / GAT to learn customer embeddings that capture social/collaborative signal, then cluster.

## 5. Explainability Research

Extend SHAP/LIME with:
- **Anchors** (Ribeiro et al. 2018) — high-precision rule-based explanations
- **Counterfactual explanations** (Wachter et al. 2017) — "what would need to change to move this customer to a different segment?"
- **DiCE** (Mothilal et al. 2020) — diverse counterfactual generation

## 6. Fairness Audit

Per-segment fairness analysis:
- Demographic parity: are segments balanced across protected attributes?
- Equal opportunity: within each segment, do protected groups have equal true positive rate?
- Disparate impact: 80% rule compliance

Use **Fairlearn** or **AIF360**.

## 7. Bayesian Deep Learning

Replace point-estimate classifiers with Bayesian Neural Networks (via **TensorFlow Probability** or **Pyro**) to:
- Quantify epistemic uncertainty
- Flag low-confidence predictions for human review
- Enable active learning

## 8. Multi-Objective Optimisation

Construct a Pareto frontier of:
- Silhouette score (cluster quality)
- Cluster interpretability (balance)
- Business value (per-segment revenue lift)

Use NSGA-II or MOEA/D to explore trade-offs.

## 9. Online / Incremental Clustering

Customer behavior drifts over time. Apply:
- **STREAMLS** — streaming k-means
- **DenStream** — density-based streaming clustering
- **CluStream** — micro/macro clustering

to update segments without retraining from scratch.

## 10. Self-Supervised Pretraining

Pretrain a Transformer on customer event sequences using masked-language-modeling-style objectives, then fine-tune on the segmentation task. Compare transfer learning gains vs. training from scratch.

## 11. Meta-Learning for New-Product Cold Start

When a new product launches, there's no historical purchase data. Use meta-learning (MAML, Reptile) to rapidly adapt the segment recommender using only a few early-adopter purchases.

## 12. Robustness & Adversarial Analysis

Test classifier robustness:
- Add Gaussian noise to inputs and measure accuracy decay
- Apply adversarial perturbations (FGSM, PGD) — is the classifier fooled?
- Use **CleverHans** or **Foolbox** for adversarial benchmarking

## Publication Targets

- **KDD** — Applied data mining
- **NeurIPS** — Deep learning methods
- **ICDM** — Data mining research
- **RecSys** — Recommender systems
- **Marketing Science** — Business applications
- **JMLR** — Methods and theory

## Suggested Paper Titles

1. "Deep vs. Classical Clustering for Customer Categorizer: An Empirical Comparison"
2. "Causal Customer Categorizer: Uplift-Aware Cluster Discovery"
3. "Counterfactual Customer Explanations: From SHAP to Actionable Insights"
4. "Graph Neural Networks for Customer-Product Bipartite Segmentation"
5. "Bayesian Uncertainty Quantification for Customer Segment Assignment"
