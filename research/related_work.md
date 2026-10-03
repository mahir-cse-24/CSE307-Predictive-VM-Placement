# Research notes: predictive VM placement

The CSE-307 brief remains the authoritative source for the assignment requirements. The papers below are used for research context and comparison.

## 1. VM placement as packing

VM placement is commonly modeled as bin packing. When CPU, memory, bandwidth, or other resource dimensions are considered together, the problem becomes vector bin packing. Jangiti and Shankar Sriram discuss VM placement in this form and compare scalable greedy heuristics with more complex approaches.

Reference: S. Jangiti and V. S. Shankar Sriram, "Scalable and direct vector bin-packing heuristic based on residual resource ratios for virtual machine placement in cloud data centers," *Computers & Electrical Engineering*, vol. 68, pp. 44-61, 2018, doi:10.1016/j.compeleceng.2018.03.029.

## 2. Dynamic consolidation and migration cost

Beloglazov and Buyya study dynamic VM consolidation with live migration and adaptive heuristics. Their work is useful here because it treats resource efficiency together with the cost of moving VMs. That is why this project reports migration count rather than looking only at utilization.

Reference: A. Beloglazov and R. Buyya, "Optimal online deterministic algorithms and adaptive heuristics for energy and performance efficient dynamic consolidation of virtual machines in Cloud data centers," *Concurrency and Computation: Practice and Experience*, vol. 24, no. 13, pp. 1397-1420, 2012, doi:10.1002/cpe.1867.

## 3. Prediction-aware consolidation

Hsieh et al. use predicted utilization to improve VM consolidation and evaluate the method with real workload traces in CloudSim. Their approach considers future utilization when detecting overload and underload states. This project is much smaller: one normalized resource, homogeneous hosts, and a simple linear regressor. The paper is therefore a source for framing the research problem, not a claim that the student implementation reproduces the published system.

Reference: S.-Y. Hsieh, C.-S. Liu, R. Buyya, and A. Y. Zomaya, "Utilization-prediction-aware virtual machine consolidation approach for energy-efficient cloud data centers," *Journal of Parallel and Distributed Computing*, vol. 139, pp. 99-109, 2020, doi:10.1016/j.jpdc.2019.12.014.

## 4. Prediction windows and decision trade-offs

Awad, Kara, and Leivadeas combine a Kalman filter with support vector regression to forecast utilization and use the forecast to guide VM consolidation. Their evaluation also studies the effect of prediction-window size and reports a trade-off between SLA violations, energy, and migrations. This supports the decision to keep a small threshold-sensitivity study in the course project.

Reference: M. Awad, N. Kara, and A. Leivadeas, "Utilization prediction-based VM consolidation approach," *Journal of Parallel and Distributed Computing*, vol. 170, pp. 24-38, 2022, doi:10.1016/j.jpdc.2022.08.001.

## Research questions used in the enhanced study

**RQ1:** Does proactive prediction reduce host-utilization imbalance and overload events relative to First-Fit and Best-Fit?

**RQ2:** Does regression add useful information beyond a simple persistence forecast?

**RQ3:** How sensitive is the predictive policy to the proactive headroom threshold?

**RQ4:** Does the optional explanation confidence score track actual decision correctness?

RQ1 is the required course experiment. RQ2-RQ4 are extensions for a stronger research discussion.
