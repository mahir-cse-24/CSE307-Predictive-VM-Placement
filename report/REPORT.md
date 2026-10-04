# CSE-307 Term Paper

## Paper title

**VM Resource Effects on an Ubuntu Workload**

The main study uses one fixed workload inside an Ubuntu VMware guest under five resource configurations: 1 GB/1 vCPU, 2 GB/1 vCPU, 4 GB/1 vCPU, 2 GB/2 vCPU, and 2 GB/4 vCPU.

The workload trace is generated once and reused for every condition. The guest records elapsed time, CPU time, page faults, context switches, and swap activity.

The repository also retains a separate predictive VM-placement extension with First-Fit, Best-Fit, regression-based load prediction, a demand shift, placement metrics, predictor ablation, threshold sensitivity, and explanation-confidence analysis.

The full IEEE LaTeX source is included in the local submission package. The PDF is submitted separately because the course submission asks for a PDF term paper in addition to the GitHub repository.

Before submission, populate the Ubuntu/VMware result table from `results/system_experiment.csv` after running all five conditions inside the guest.
