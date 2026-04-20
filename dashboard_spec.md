After analysis.py, generate results/dashboard.html —  
a single self-contained HTML file that loads  
results/judged\_results.jsonl via a \<script\> tag  
embedding the JSON inline, and renders:

  1\. Δ(M) bar chart per pattern (S1) — 4 grouped bars,  
     one per monitoring condition, colored by significance  
  2\. Artifact decoupling scatter (S3) — narrative\_score  
     vs faithfulness\_score, colored by monitoring condition,  
     with Spearman ρ annotated per group  
  3\. Proxy exploitation rate chart (S2) — stacked bar  
     by monitoring condition  
  4\. Raw summary table — filterable by scenario,  
     monitoring condition, pattern

No external dependencies. Chart.js from cdnjs only.  
File must open correctly by double-clicking in Finder.  
