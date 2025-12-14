def calculate_metrics(results, context_switches):
    """Performans metriklerini hesaplar"""
    waiting_times = [r['waiting'] for r in results]
    turnaround_times = [r['turnaround'] for r in results]
    max_completion = max(r['completion'] for r in results)
    
    throughput = []
    for t in [50, 100, 150, 200]:
        count = len([r for r in results if r['completion'] <= t])
        throughput.append({'time': t, 'count': count})
    
    total_burst = sum(r['burst'] for r in results)
    cpu_utilization = (total_burst / (max_completion + context_switches * 0.001)) * 100
    
    return {
        'avg_waiting': sum(waiting_times) / len(waiting_times),
        'max_waiting': max(waiting_times),
        'avg_turnaround': sum(turnaround_times) / len(turnaround_times),
        'max_turnaround': max(turnaround_times),
        'throughput': throughput,
        'cpu_utilization': cpu_utilization,
        'context_switches': context_switches
    }

def compress_timeline(timeline):
    """Ardışık aynı süreçleri birleştirir"""
    compressed = []
    for entry in timeline:
        if not compressed or entry['process'] != compressed[-1]['process']:
            compressed.append(dict(entry))
        else:
            compressed[-1]['end'] = entry['end']
    return compressed

def fcfs(processes, quantum=None):
    """First Come First Served"""
    sorted_procs = sorted(processes, key=lambda x: x['arrival'])
    current_time = 0
    timeline = []
    results = []
    context_switches = 0
    
    for i, proc in enumerate(sorted_procs):
        if current_time < proc['arrival']:
            timeline.append({'process': 'IDLE', 'start': current_time, 'end': proc['arrival']})
            current_time = proc['arrival']
        
        if i > 0:
            context_switches += 1
        
        start = current_time
        end = current_time + proc['burst']
        
        timeline.append({'process': proc['process'], 'start': start, 'end': end})
        
        results.append({
            'process': proc['process'],
            'arrival': proc['arrival'],
            'burst': proc['burst'],
            'start': start,
            'completion': end,
            'turnaround': end - proc['arrival'],
            'waiting': start - proc['arrival']
        })
        
        current_time = end
    
    return timeline, results, context_switches

def preemptive_sjf(processes, quantum=None):
    """Preemptive Shortest Job First"""
    current_time = 0
    timeline = []
    completed = []
    remaining = [{'process': p['process'], 'arrival': p['arrival'], 
                  'burst': p['burst'], 'priority': p['priority'],
                  'remaining': p['burst'], 'start': -1} for p in processes]
    context_switches = 0
    last_process = None
    
    while len(completed) < len(processes):
        available = [p for p in remaining if p['arrival'] <= current_time and p['remaining'] > 0]
        
        if not available:
            next_proc = min([p for p in remaining if p['remaining'] > 0], 
                          key=lambda x: x['arrival'])
            timeline.append({'process': 'IDLE', 'start': current_time, 'end': next_proc['arrival']})
            current_time = next_proc['arrival']
            continue
        
        shortest = min(available, key=lambda x: x['remaining'])
        
        if last_process and last_process != shortest['process']:
            context_switches += 1
        
        if shortest['start'] == -1:
            shortest['start'] = current_time
        
        timeline.append({'process': shortest['process'], 'start': current_time, 
                        'end': current_time + 1})
        
        shortest['remaining'] -= 1
        current_time += 1
        last_process = shortest['process']
        
        if shortest['remaining'] == 0:
            original = next(p for p in processes if p['process'] == shortest['process'])
            completed.append({
                'process': shortest['process'],
                'arrival': shortest['arrival'],
                'burst': shortest['burst'],
                'start': shortest['start'],
                'completion': current_time,
                'turnaround': current_time - shortest['arrival'],
                'waiting': shortest['start'] - shortest['arrival'] + 
                          (current_time - shortest['start'] - shortest['burst'])
            })
    
    return compress_timeline(timeline), completed, context_switches

def non_preemptive_sjf(processes, quantum=None):
    """Non-Preemptive Shortest Job First"""
    current_time = 0
    timeline = []
    completed = []
    remaining = processes.copy()
    context_switches = 0
    
    while remaining:
        available = [p for p in remaining if p['arrival'] <= current_time]
        
        if not available:
            next_proc = min(remaining, key=lambda x: x['arrival'])
            timeline.append({'process': 'IDLE', 'start': current_time, 'end': next_proc['arrival']})
            current_time = next_proc['arrival']
            continue
        
        shortest = min(available, key=lambda x: x['burst'])
        
        if completed:
            context_switches += 1
        
        start = current_time
        end = current_time + shortest['burst']
        
        timeline.append({'process': shortest['process'], 'start': start, 'end': end})
        
        completed.append({
            'process': shortest['process'],
            'arrival': shortest['arrival'],
            'burst': shortest['burst'],
            'start': start,
            'completion': end,
            'turnaround': end - shortest['arrival'],
            'waiting': start - shortest['arrival']
        })
        
        current_time = end
        remaining.remove(shortest)
    
    return timeline, completed, context_switches

def round_robin(processes, quantum=4):
    """Round Robin"""
    current_time = 0
    timeline = []
    queue = []
    remaining = [{'process': p['process'], 'arrival': p['arrival'], 
                  'burst': p['burst'], 'priority': p['priority'],
                  'remaining': p['burst'], 'start': -1} for p in processes]
    completed = []
    context_switches = 0
    last_process = None
    
    while len(completed) < len(processes) or queue:
        # Yeni süreçleri kuyruğa ekle
        for p in remaining:
            if (p['arrival'] <= current_time and p['remaining'] > 0 and 
                p not in queue and (last_process != p['process'] or p['remaining'] == p['burst'])):
                queue.append(p)
        
        if not queue:
            next_proc = min([p for p in remaining if p['remaining'] > 0], 
                          key=lambda x: x['arrival'])
            timeline.append({'process': 'IDLE', 'start': current_time, 'end': next_proc['arrival']})
            current_time = next_proc['arrival']
            continue
        
        current = queue.pop(0)
        
        if last_process and last_process != current['process']:
            context_switches += 1
        
        if current['start'] == -1:
            current['start'] = current_time
        
        execute_time = min(quantum, current['remaining'])
        timeline.append({'process': current['process'], 'start': current_time, 
                        'end': current_time + execute_time})
        
        current['remaining'] -= execute_time
        current_time += execute_time
        last_process = current['process']
        
        # Yeni gelen süreçleri kontrol et
        for p in remaining:
            if (p['arrival'] <= current_time and p['remaining'] > 0 and 
                p not in queue and p != current):
                queue.append(p)
        
        if current['remaining'] > 0:
            queue.append(current)
        else:
            original = next(p for p in processes if p['process'] == current['process'])
            completed.append({
                'process': current['process'],
                'arrival': current['arrival'],
                'burst': current['burst'],
                'start': current['start'],
                'completion': current_time,
                'turnaround': current_time - current['arrival'],
                'waiting': current_time - current['arrival'] - current['burst']
            })
    
    return compress_timeline(timeline), completed, context_switches

def preemptive_priority(processes, quantum=None):
    """Preemptive Priority Scheduling (Düşük sayı = Yüksek öncelik)"""
    current_time = 0
    timeline = []
    completed = []
    remaining = [{'process': p['process'], 'arrival': p['arrival'], 
                  'burst': p['burst'], 'priority': p['priority'],
                  'remaining': p['burst'], 'start': -1} for p in processes]
    context_switches = 0
    last_process = None
    
    while len(completed) < len(processes):
        available = [p for p in remaining if p['arrival'] <= current_time and p['remaining'] > 0]
        
        if not available:
            next_proc = min([p for p in remaining if p['remaining'] > 0], 
                          key=lambda x: x['arrival'])
            timeline.append({'process': 'IDLE', 'start': current_time, 'end': next_proc['arrival']})
            current_time = next_proc['arrival']
            continue
        
        highest = min(available, key=lambda x: x['priority'])
        
        if last_process and last_process != highest['process']:
            context_switches += 1
        
        if highest['start'] == -1:
            highest['start'] = current_time
        
        timeline.append({'process': highest['process'], 'start': current_time, 
                        'end': current_time + 1})
        
        highest['remaining'] -= 1
        current_time += 1
        last_process = highest['process']
        
        if highest['remaining'] == 0:
            completed.append({
                'process': highest['process'],
                'arrival': highest['arrival'],
                'burst': highest['burst'],
                'start': highest['start'],
                'completion': current_time,
                'turnaround': current_time - highest['arrival'],
                'waiting': highest['start'] - highest['arrival'] + 
                          (current_time - highest['start'] - highest['burst'])
            })
    
    return compress_timeline(timeline), completed, context_switches

def non_preemptive_priority(processes, quantum=None):
    """Non-Preemptive Priority Scheduling (Düşük sayı = Yüksek öncelik)"""
    current_time = 0
    timeline = []
    completed = []
    remaining = processes.copy()
    context_switches = 0
    
    while remaining:
        available = [p for p in remaining if p['arrival'] <= current_time]
        
        if not available:
            next_proc = min(remaining, key=lambda x: x['arrival'])
            timeline.append({'process': 'IDLE', 'start': current_time, 'end': next_proc['arrival']})
            current_time = next_proc['arrival']
            continue
        
        highest = min(available, key=lambda x: x['priority'])
        
        if completed:
            context_switches += 1
        
        start = current_time
        end = current_time + highest['burst']
        
        timeline.append({'process': highest['process'], 'start': start, 'end': end})
        
        completed.append({
            'process': highest['process'],
            'arrival': highest['arrival'],
            'burst': highest['burst'],
            'start': start,
            'completion': end,
            'turnaround': end - highest['arrival'],
            'waiting': start - highest['arrival']
        })
        
        current_time = end
        remaining.remove(highest)
    
    return timeline, completed, context_switches