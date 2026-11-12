# Parallel Computing Lab — стартовый комплект

Проект рассчитан на Python 3 без сторонних библиотек и macOS / Windows / Linux.
Запускайте этапы по одному, из Terminal, находясь в папке проекта.

## Важно
- Все численные результаты должны быть получены на вашем компьютере.
- Скрипты печатают измерения и VERIFY_HASH; не подставляйте вымышленные значения.
- Лабораторная в исходном PDF требует самостоятельного офлайн-выполнения без AI.
  Используйте этот комплект только в рамках разрешений преподавателя.
- Нагрузки Phase 2 и Phase 3 могут занять много времени и нагреть ноутбук.
  Сначала используйте `--quick` (если доступен), затем полный режим.
- На Apple Silicon `hw.logicalcpu` и `hw.physicalcpu` могут совпадать; не предполагайте Hyper-Threading.

## Быстрый старт (macOS)
```bash
cd ~/parallel_lab
python3 --version
python3 task0_cal.py
```

Затем:
```bash
python3 task1_falsesharing.py
python3 task2_scaling.py
python3 task3a_roofline.py
python3 task3b_gemm.py
python3 task4_scheduling.py
```

Для каждого этапа сохраняйте вывод терминала в отчёт:
```bash
python3 task0_cal.py | tee phase0_output.txt
```
На macOS команда `tee` доступна по умолчанию.

## Файлы
- `harness.py` — таймер, статистика, FNV-1a verification hash.
- `task0_cal.py` — аппаратная информация и калибровка таймера.
- `task1_falsesharing.py` — shared-memory stride и process scaling.
- `task2_scaling.py` — strong / weak scaling.
- `task3a_roofline.py` — пропускная способность памяти и Python compute ceiling.
- `task3b_gemm.py` — три варианта GEMM и sweep размера тайла.
- `task4_scheduling.py` — static / cyclic / dynamic chunk scheduling.
- `lab_report_template.md` — шаблон итогового отчёта.

## Ограничения реализации
Python-циклы и multiprocessing имеют большой overhead. Результаты отражают всю программную систему
(Python interpreter + OS scheduling + memory subsystem), а не чистый аппаратный предел CPU.
На macOS multiprocessing использует `spawn`, поэтому все worker-функции находятся на уровне модуля.
