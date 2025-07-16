from concurrent.futures import ThreadPoolExecutor

def run_parallel_tasks(task_functions):
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(func) for func in task_functions]
        for future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                results.append({"error": str(e)})
    return results
