# Quick run guide

Install dependencies:

python -m pip install -r requirements.txt

Run the main ten-seed experiment:

python src/vm_placement.py --seeds 10 --out-dir results

Run the statistical checks, predictor ablation, and confidence metrics:

python src/research_analysis.py

Run the small threshold-sensitivity pilot:

python src/sensitivity.py

Run the unit tests:

python -m pytest -q

The final IEEE paper is supplied as a separate 3-page PDF. The LaTeX source is maintained with the local submission package because the course requires the PDF rather than the editable source.
