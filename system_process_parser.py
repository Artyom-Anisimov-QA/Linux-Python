import subprocess
from collections import defaultdict
import datetime

# Запускаем команду ps aux и возвращаем её вывод в виде списка строк.
def get_processes():
    # Запускаем команду ps aux и получаем её вывод
    result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').splitlines()
    return lines

# Парсим вывод команды ps aux, извлекая информацию о пользователе,
# использовании CPU, памяти и команде.
def parse_processes(lines):
    # Пропускаем заголовок
    processes = []
    for line in lines[1:]:
        parts = line.split()
        user = parts[0]
        cpu = float(parts[2])
        mem = float(parts[3])
        command = ' '.join(parts[10:])
        processes.append((user, cpu, mem, command))
    return processes

# Формируем отчёт
def generate_report(processes):
    # Считаем количество процессов по пользователям
    user_processes = defaultdict(int)
    total_memory = 0.0
    total_cpu = 0.0
    max_mem_process = ('', 0.0)
    max_cpu_process = ('', 0.0)

    for user, cpu, mem, command in processes:
        user_processes[user] += 1
        total_memory += mem
        total_cpu += cpu
        if mem > max_mem_process[1]:
            max_mem_process = (command[:20], mem)
        if cpu > max_cpu_process[1]:
            max_cpu_process = (command[:20], cpu)

# Формируем отчёт
    report = []
    report.append("Отчёт о состоянии системы:")
    report.append(f"Пользователи системы: {', '.join(user_processes.keys())}")
    report.append(f"Процессов запущено: {len(processes)}")
    report.append("\nПользовательских процессов:")
    for user, count in user_processes.items():
        report.append(f"{user}: {count}")
    report.append(f"\nВсего памяти используется: {total_memory:.1f}%")
    report.append(f"Всего CPU используется: {total_cpu:.1f}%")
    report.append(f"Больше всего памяти использует: {max_mem_process[0]} ({max_mem_process[1]:.1f}%)")
    report.append(f"Больше всего CPU использует: {max_cpu_process[0]} ({max_cpu_process[1]:.1f}%)")
    return '\n'.join(report)

# Сохраняем отчёт в файл с именем, соответствующим текущей дате и времени.
def save_report(report):
    # Сохраняем отчёт в файл с текущей датой и временем
    now = datetime.datetime.now()
    filename = now.strftime("%d-%m-%Y-%H:%M-scan.txt")
    with open(filename, 'w') as f:
        f.write(report)
    print(f"Отчёт сохранён в файл: {filename}")


# Основная функция,объединяющая все шаги.
def main():
    lines = get_processes()
    processes = parse_processes(lines)
    report = generate_report(processes)
    print(report)
    save_report(report)

if __name__ == "__main__":
    main()