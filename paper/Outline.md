# Paragraph Skeleton: FRESCO v2 — Cross-Cluster Workload Comparability

## Abstract (Single block, ~250 words)
> Cross-cluster workload comparison is essential for capacity planning and system procurement, yet no published study has empirically validated whether predictive models trained on one HPC cluster can generalize to another. We present FRESCO v2, a provenance-rich dataset extending the original schema to 65 columns, and use it to conduct an 84-experiment investigation proving that zero-shot cross-cluster memory prediction fails completely (yielding $R^2$ values as low as -24) due to fundamental domain shifts. Because model transfer is unviable, we propose a mathematically optimized "Local Telemetry Blueprint" that successfully restores predictive accuracy (achieving an $R^2$ of 0.31 on temporal splits) by defining the minimal required data inputs and a resilient local training strategy.

---

## §1. Introduction
* **¶1:** High-performance computing centers routinely make operational decisions that would benefit from comparing workload behavior across clusters, yet such comparisons are rarely attempted with empirical rigor.
* **¶2:** The growing availability of public HPC workload datasets naturally raises the question of whether a predictive model trained on one cluster's data can simply be transferred to another.
* **¶3:** However, our baseline experiments demonstrate that this assumption is empirically false: cross-cluster memory prediction models perform worse than simply guessing the target cluster's mean, yielding $R^2$ values as low as -24.
* **¶4:** This catastrophic failure is driven by severe covariate, conditional, and era shifts that prior datasets, like the original FRESCO release, lacked the measurement provenance to diagnose.
* **¶5:** In this paper, we present three core contributions: FRESCO v2 (a provenance-rich dataset of 20.9 million jobs), empirical proof that zero-shot transfer fails, and a mathematically optimized "Local Telemetry Blueprint" that successfully restores predictive accuracy.

---

## §2. Background & Related Work
* **¶1:** While several large-scale HPC datasets have been published to aid operational research, they predominantly lack standardized hardware context and explicit measurement semantics.
* **¶2:** In broader machine learning contexts, unsupervised domain adaptation is frequently used to bridge the gap between different data distributions.
* **¶3:** However, the rigid, hardware-bound nature of HPC telemetry means that domain adaptation techniques cannot overcome the fundamental shifts in feature-to-memory relationships across different clusters.

---

## §3. FRESCO v2 & Measurement Provenance
* **¶1:** To systematically investigate cross-cluster transferability, we developed FRESCO v2, expanding the original schema to 65 columns to capture deep measurement provenance.
* **¶2:** A critical addition in v2 is the normalization of hardware metrics, which ensures that resource requests and limits are comparable across vastly different node architectures.
* **¶3:** Beyond the data itself, we introduce a workload comparability framework designed to explicitly diagnose the hidden data shifts that derail machine learning models in production.

---

## §4. The Illusion of Transfer: 84 Experiments
* **¶1:** Using FRESCO v2, we conducted a systematic 84-experiment investigation into zero-shot cross-cluster memory prediction across three major academic clusters.
* **¶2:** When a model trained on one cluster is naively evaluated on another, the predictive signal completely collapses, resulting in negative $R^2$ scores.
* **¶3:** Even when employing best-case conditions—such as overlap-aware hardware regime matching and domain adaptation—the models failed to generalize.
* **¶4:** This universal failure is rooted in three distinct phenomena: covariate shift from disjoint node types, conditional shift where identical job metrics map to different memory outcomes, and era shift from aging hardware.

---

## §5. The Local Telemetry Blueprint
* **¶1:** Since our experiments definitively prove that cross-cluster model transfer is unviable, HPC centers must rely on locally trained predictive models.
* **¶2:** To prevent excessive logging overhead, we distilled our findings into a minimal telemetry blueprint, identifying a consensus of core features—such as user CPU time and raw runtime—that drive predictive success across all tested clusters.
* **¶3:** Because HPC telemetry exhibits extreme right-skewness, our blueprint mandates applying $\log(x+1)$ transformations to all continuous temporal features and the target memory variable.
* **¶4:** Furthermore, to combat era shift, the training pipeline must employ strict temporal data splitting rather than random shuffling, coupled with automated retraining triggers when cluster hardware evolves.
* **¶5:** When applied to the Anvil cluster, this optimized local blueprint successfully predicted future memory usage with an $R^2$ of 0.3175, rescuing the predictive signal that cross-cluster transfer destroyed.

---

## §6. Conclusion
* **¶1:** Cross-cluster workload comparison remains a highly desirable goal for HPC operations, but this work demonstrates that predictive models cannot be safely transferred between unique hardware environments.
* **¶2:** By adopting the FRESCO v2 telemetry blueprint and local training methodology, supercomputing centers can abandon the risks of naive transfer and build robust, future-proof operational models.
