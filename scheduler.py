import csv
import threading
import os
from algorithms import *

CONTEXT_SWITCH_TIME = 0.001
QUANTUM = 4

def read_csv(filename):
    """CSV dosyasını okur ve süreç listesi döndürür"""
    processes = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            processes.append({
                'process': row['process'],
                'arrival': float(row['arrival']),
                'burst': float(row['burst']),
                'priority': int(row['priority'])
            })
    return processes

def write_results(algorithm_name, timeline, results, metrics, output_dir):
    """Sonuçları dosyaya yazar"""
    filename = os.path.join(output_dir, f'{algorithm_name}_results.txt')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{'='*60}\n")
        f.write(f"{algorithm_name} - Sonuçlar\n")
        f.write(f"{'='*60}\n\n")
        
        f.write("ZAMAN TABLOSU:\n")
        f.write("-" * 60 + "\n")
        for entry in timeline:
            f.write(f"[ {entry['start']:7.3f} ] - - {entry['process']:6} - - [ {entry['end']:7.3f} ]\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("BEKLEME SÜRESİ (Waiting Time):\n")
        f.write("-" * 60 + "\n")
        f.write(f"Ortalama: {metrics['avg_waiting']:.3f}\n")
        f.write(f"Maksimum: {metrics['max_waiting']:.3f}\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("TAMAMLANMA SÜRESİ (Turnaround Time):\n")
        f.write("-" * 60 + "\n")
        f.write(f"Ortalama: {metrics['avg_turnaround']:.3f}\n")
        f.write(f"Maksimum: {metrics['max_turnaround']:.3f}\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("THROUGHPUT (T anındaki tamamlanan iş sayısı):\n")
        f.write("-" * 60 + "\n")
        for tp in metrics['throughput']:
            f.write(f"T = {tp['time']:3d} : {tp['count']} iş\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("CPU VERİMLİLİĞİ:\n")
        f.write("-" * 60 + "\n")
        f.write(f"CPU Kullanım Oranı: {metrics['cpu_utilization']:.2f}%\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("BAĞLAM DEĞİŞTİRME:\n")
        f.write("-" * 60 + "\n")
        f.write(f"Toplam Bağlam Değiştirme: {metrics['context_switches']}\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("SÜREÇ DETAYLARI:\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Süreç':<10} {'Varış':<8} {'Burst':<8} {'Başlama':<10} {'Tamamlanma':<12} {'Turnaround':<12} {'Bekleme':<10}\n")
        f.write("-" * 60 + "\n")
        for r in results:
            f.write(f"{r['process']:<10} {r['arrival']:<8.2f} {r['burst']:<8.2f} {r['start']:<10.2f} "
                   f"{r['completion']:<12.2f} {r['turnaround']:<12.2f} {r['waiting']:<10.2f}\n")
    
    print(f"✓ {algorithm_name} sonuçları kaydedildi: {filename}")

def run_algorithm(algo_func, name, processes, output_dir):
    """Bir algoritmayı çalıştırır ve sonuçları kaydeder"""
    print(f"⚙️  {name} çalışıyor...")
    timeline, results, context_switches = algo_func(processes, QUANTUM if 'Round Robin' in name else None)
    metrics = calculate_metrics(results, context_switches)
    write_results(name, timeline, results, metrics, output_dir)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Kullanım: python scheduler.py <csv_dosyası>")
        print("Örnek: python scheduler.py case1.csv")
        return
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ Hata: {csv_file} bulunamadı!")
        return
    
    # Sonuç klasörünü oluştur
    case_name = os.path.splitext(os.path.basename(csv_file))[0]
    output_dir = f'results_{case_name}'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"CPU ZAMANLAMA ALGORİTMALARI SİMÜLASYONU")
    print(f"{'='*60}")
    print(f"📂 Dosya: {csv_file}")
    print(f"📁 Çıktı Klasörü: {output_dir}\n")
    
    # CSV'yi oku
    processes = read_csv(csv_file)
    print(f"✓ {len(processes)} süreç yüklendi\n")
    
    # BONUS: Tüm algoritmaları thread olarak çalıştır
    use_threads = input("Algoritmaları paralel çalıştır? (e/h): ").lower() == 'e'
    
    algorithms = [
        (fcfs, "FCFS", processes.copy()),
        (preemptive_sjf, "Preemptive_SJF", processes.copy()),
        (non_preemptive_sjf, "Non_Preemptive_SJF", processes.copy()),
        (round_robin, "Round_Robin", processes.copy()),
        (preemptive_priority, "Preemptive_Priority", processes.copy()),
        (non_preemptive_priority, "Non_Preemptive_Priority", processes.copy())
    ]
    
    if use_threads:
        print("\n🚀 Paralel çalıştırma modu aktif!\n")
        threads = []
        for algo_func, name, procs in algorithms:
            thread = threading.Thread(target=run_algorithm, args=(algo_func, name, procs, output_dir))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
    else:
        print("\n⏳ Sıralı çalıştırma modu...\n")
        for algo_func, name, procs in algorithms:
            run_algorithm(algo_func, name, procs, output_dir)
    
    print(f"\n{'='*60}")
    print(f"✅ Tüm algoritmalar tamamlandı!")
    print(f"📊 Sonuçlar '{output_dir}' klasöründe")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()