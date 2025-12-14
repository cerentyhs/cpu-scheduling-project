# CPU Zamanlama Algoritmaları Projesi

Bu proje işletim sistemleri dersi için hazırlanmıştır. 6 farklı CPU zamanlama algoritmasını Python ile kodladım ve performanslarını karşılaştırdım.

## Kullanılan Algoritmalar

- FCFS (First Come First Served)
- Preemptive SJF (Shortest Job First)
- Non-Preemptive SJF
- Round Robin (quantum=4)
- Preemptive Priority Scheduling
- Non-Preemptive Priority Scheduling

## Nasıl Çalıştırılır

Projeyi çalıştırmak için Python 3 yüklü olması yeterli. Ekstra bir kütüphane kurmaya gerek yok.

```bash
python scheduler.py case1.csv
```

veya

```bash
python scheduler.py case2.csv
```

Kendi CSV dosyanızı da kullanabilirsiniz, format şöyle olmalı:

```csv
process,arrival,burst,priority
P001,0,10,3
P002,2,5,1
```

## Özellikler

Program çalıştırıldığında algoritmaları paralel mi yoksa sırayla mı çalıştırmak istediğinizi soruyor. Paralel çalıştırma seçeneğini seçerseniz tüm algoritmalar aynı anda thread'ler halinde çalışıyor.

Her algoritma için ayrı bir sonuç dosyası oluşturuluyor. Dosyalar `results_case1` veya `results_case2` klasörüne kaydediliyor.

## Hesaplanan Metrikler

Her algoritma için şu veriler hesaplanıp rapor ediliyor:

1. Zaman çizelgesi (hangi süreç ne zaman çalıştı)
2. Ortalama ve maksimum bekleme süreleri
3. Ortalama ve maksimum tamamlanma süreleri
4. Throughput değerleri (T=50, 100, 150, 200 için)
5. CPU kullanım oranı
6. Context switch sayısı

Bağlam değiştirme süresi 0.001 birim zaman olarak alındı.

## Dosya Yapısı

- `scheduler.py` - Ana program, CSV okuma ve sonuç yazma işlemlerini yapıyor
- `algorithms.py` - 6 zamanlama algoritmasının kodları burada
- `case1.csv` - 5 süreçli test verisi
- `case2.csv` - 6 süreçli test verisi

## Algoritma Karşılaştırması

Projeyi çalıştırdıktan sonra sonuç dosyalarından şunları gözlemledim:

**FCFS**: En basit algoritma ama uzun süreçler gelince küçük süreçler çok bekliyor (convoy effect). Bekleme süreleri yüksek çıkıyor.

**SJF**: En kısa işi önce çalıştırdığı için ortalama bekleme süresi düşük. Preemptive versiyonu daha iyi sonuç veriyor ama context switch sayısı artıyor.

**Round Robin**: Zaman dilimlerini adil paylaştırıyor. Quantum değeri çok önemli, 4 birim zaman makul bir değer gibi durdu. 

**Priority**: Öncelikli işleri hızlı bitiriyor ama düşük öncelikli işler açlık (starvation) problemi yaşayabiliyor.

## Notlar

- Priority değerlerinde düşük sayı yüksek öncelik anlamına geliyor (1 en yüksek)
- Round Robin için quantum değeri 4 olarak ayarlandı
- Paralel çalıştırma özelliği Python'ın threading modülü ile yapıldı

## Sorun Giderme

Eğer "No module named 'algorithms'" hatası alırsanız, terminal'in doğru klasörde olduğundan emin olun.

Git ile ilgili sorun yaşarsanız:
```bash
git init
git add .
git commit -m "ilk commit"
git push
```

Python bulunamadı hatası alırsanız `python3` veya `py` komutlarını deneyin.