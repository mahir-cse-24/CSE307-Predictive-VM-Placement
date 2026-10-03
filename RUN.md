# Quick Run

```bash
python -m pip install -r requirements.txt
python src/vm_placement.py --seeds 10 --out-dir results
python src/plot_results.py
python -m pytest -q
```

The IEEE report source is `report/term_paper.tex`. Compile it with `pdflatex` from the `report/` directory.
