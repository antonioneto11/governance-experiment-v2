results/sample\_100.jsonl

Add a script results/sample\_export.py that:  
  \- randomly samples 100 rows from judged\_results.jsonl  
    stratified by scenario × monitoring condition  
  \- writes results/sample\_100.jsonl  
  \- writes results/sample\_100\_readable.md —  
    a human-readable version showing the full prompt,  
    response, and scores for each sampled trial  
