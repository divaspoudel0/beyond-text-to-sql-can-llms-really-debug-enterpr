#!/usr/bin/env python3
"""
Proxy benchmark evaluation for SQL debugging.
Tests LLMs on a small set of SQL debugging tasks following the Squirrel Benchmark taxonomy.
Uses Graph Match Score (GM) as the primary metric.
"""
import json
import sys
import re
import difflib
from typing import Dict, List

def normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison."""
    sql = sql.strip()
    sql = re.sub(r'\s+', ' ', sql)
    sql = sql.lower()
    sql = sql.rstrip(';')
    return sql

def graph_match_score(predicted: str, expected: str) -> float:
    """Compute a simplified Graph Match Score based on structural similarity."""
    pred_norm = normalize_sql(predicted)
    exp_norm = normalize_sql(expected)
    
    if pred_norm == exp_norm:
        return 1.0
    
    matcher = difflib.SequenceMatcher(None, pred_norm, exp_norm)
    ratio = matcher.ratio()
    
    pred_tokens = set(re.findall(r'\b\w+\b', pred_norm))
    exp_tokens = set(re.findall(r'\b\w+\b', exp_norm))
    
    if not exp_tokens:
        return 0.0
    
    token_overlap = len(pred_tokens & exp_tokens) / len(exp_tokens)
    score = 0.6 * ratio + 0.4 * token_overlap
    return min(score, 1.0)

def evaluate_task(task: Dict, model_response: str) -> Dict:
    """Evaluate a single task."""
    fixed_sql = task.get('fixed_sql', '')
    buggy_sql = task.get('buggy_sql', '')
    
    gm_score = graph_match_score(model_response, fixed_sql)
    mb_score = 1.0 if graph_match_score(model_response, buggy_sql) < gm_score else 0.0
    em_score = 1.0 if normalize_sql(model_response) == normalize_sql(fixed_sql) else 0.0
    
    return {
        'task_id': task['id'],
        'type': task['type'],
        'em': em_score,
        'gm': gm_score,
        'mb': mb_score
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python evaluate.py <tasks_file> [predictions_file]")
        sys.exit(1)
    
    tasks_file = sys.argv[1]
    predictions_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    with open(tasks_file) as f:
        tasks = json.load(f)
    
    if predictions_file:
        with open(predictions_file) as f:
            predictions = json.load(f)
        
        results = []
        for task in tasks:
            task_id = task['id']
            if task_id in predictions:
                result = evaluate_task(task, predictions[task_id])
                results.append(result)
        
        syntax_results = [r for r in results if r['type'] == 'syntax']
        semantic_results = [r for r in results if r['type'] == 'semantic']
        
        print(f"Total tasks: {len(results)}")
        
        if syntax_results:
            avg_gm_s = sum(r['gm'] for r in syntax_results) / len(syntax_results)
            print(f"Squirrel-Syntax GM: {avg_gm_s*100:.2f}%")
        
        if semantic_results:
            avg_gm_sem = sum(r['gm'] for r in semantic_results) / len(semantic_results)
            print(f"Squirrel-Semantic GM: {avg_gm_sem*100:.2f}%")
        
        output = {
            'syntax_gm': avg_gm_s*100 if syntax_results else 0,
            'semantic_gm': avg_gm_sem*100 if semantic_results else 0,
            'details': results
        }
        
        output_file = predictions_file.replace('.json', '_results.json')
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {output_file}")
    else:
        print(f"Loaded {len(tasks)} tasks")
