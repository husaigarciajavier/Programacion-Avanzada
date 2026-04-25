#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_acquisition.py
Proyecto de ejemplo: adquisición de lecturas de temperatura y LDR durante 1 minuto,
guardado en CSV y generación de una gráfica.
Autor: (Tu nombre)
Versión: 1.0.1

Cambios en v1.0.1:
- Corregido bug: uso incorrecto de `random.sin(...)`. La función trigonométrica
  pertenece al módulo `math`, no a `random`. Se importó `math` y se reemplazó
  `random.sin` por `math.sin`.
- Actualizado docstring y metadata de versión.
- Pequeña nota de registro: este cambio evita el error
  "module 'random' has no attribute 'sin'".

Uso:
    # Modo simulación (no requiere hardware)
    python src/run_acquisition.py --mode sim

    # Modo serial (leer desde puerto serie, requiere sketch en Wokwi o Arduino)
    python src/run_acquisition.py --mode serial --port COM3 --baud 115200
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
import random
import math
import statistics
import tempfile

# Dependencias opcionales para graficar
try:
    import matplotlib.pyplot as plt
    import numpy as np
except Exception:
    plt = None
    np = None

# -------------------------
# Configuración por defecto
# -------------------------
DEFAULT_DURATION = 60          # segundos
DEFAULT_INTERVAL = 1           # segundos entre muestras
RESULTS_DIR = "results"

# -------------------------
# Utilidades
# -------------------------
def iso_now_utc():
    """Devuelve timestamp ISO 8601 en UTC (ej: 2026-03-24T09:00:00Z)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_results_dir():
    """Crea la carpeta results si no existe."""
    os.makedirs(RESULTS_DIR, exist_ok=True)


def safe_write_atomic(path, text, mode="w", encoding="utf-8"):
    """
    Escribe de forma atómica: escribe en archivo temporal y renombra.
    Evita archivos CSV corruptos si el proceso se interrumpe.
    """
    dirpath = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp_")
    try:
        with os.fdopen(fd, mode, encoding=encoding) as f:
            f.write(text)
        os.replace(tmp_path, path)
    except Exception:
        # Si falla, intentar eliminar temporal
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


# -------------------------
# Simulación y lectura
# -------------------------
def simulate_reading(t_seconds):
    """
    Genera una lectura simulada de temperatura y LDR.
    t_seconds: tiempo transcurrido desde inicio (s) para modelar tendencias.
    Retorna (temp_c, ldr_raw)

    Nota sobre el bug corregido:
    - En versiones anteriores se usó `random.sin(...)`, lo cual provocaba:
      "module 'random' has no attribute 'sin'".
    - La función trigonométrica correcta es `math.sin(...)`. Aquí se usa `math`.
    """
    # Temperatura base con ligera deriva y ruido
    temp_base = 22.0 + 0.01 * (t_seconds / 1.0)  # deriva muy lenta
    temp_noise = random.gauss(0, 0.2)            # ruido gaussiano
    temp = temp_base + temp_noise

    # LDR simulado: valor ADC 0-1023 con variaciones y picos ocasionales
    # Usar math.sin en lugar de random.sin (corrección v1.0.1)
    ldr_base = 400 + 50 * (0.5 * (1 + math.sin(t_seconds / 5.0)))
    ldr_noise = random.gauss(0, 10)
    # ocasional pico de luz
    if random.random() < 0.02:
        ldr_noise += random.uniform(100, 300)
    ldr = int(max(0, min(1023, ldr_base + ldr_noise)))

    return round(temp, 2), ldr


def parse_serial_line(line):
    """
    Parsea una línea proveniente del serial.
    Se espera formato: temp,ldr  (ej: "23.5,512")
    Devuelve (temp_float, ldr_int) o lanza ValueError.
    """
    parts = line.strip().split(",")
    if len(parts) < 2:
        raise ValueError("Formato inválido, se esperaban dos valores separados por coma")
    temp = float(parts[0])
    ldr = int(float(parts[1]))
    return round(temp, 2), ldr


# -------------------------
# Adquisición
# -------------------------
def acquire_data(mode="sim", port=None, baud=115200, duration_seconds=DEFAULT_DURATION, sample_interval_s=DEFAULT_INTERVAL):
    """
    Ejecuta la adquisición de datos.
    mode: "sim" o "serial"
    Retorna lista de tuplas: (timestamp_iso, temp, ldr)
    """
    readings = []
    start_time = time.time()
    elapsed = 0.0
    sample_count = 0
    errors = 0

    serial_obj = None
    if mode == "serial":
        try:
            import serial
            serial_obj = serial.Serial(port, baud, timeout=1)
            serial_obj.reset_input_buffer()
        except Exception as e:
            print(f"[WARN] No se pudo abrir puerto serial {port}: {e}", file=sys.stderr)
            print("[INFO] Cambiando a modo simulación.")
            mode = "sim"

    print(f"[INFO] Inicio adquisición: modo={mode}, duración={duration_seconds}s, intervalo={sample_interval_s}s")
    try:
        while elapsed < duration_seconds:
            t_now = iso_now_utc()
            try:
                if mode == "sim":
                    temp, ldr = simulate_reading(elapsed)
                else:
                    raw_line = serial_obj.readline().decode("utf-8", errors="ignore")
                    if not raw_line:
                        raise IOError("Timeout o línea vacía desde serial")
                    temp, ldr = parse_serial_line(raw_line)
            except Exception as e:
                errors += 1
                print(f"[ERROR] lectura fallida en t={elapsed:.1f}s: {e}", file=sys.stderr)
                temp, ldr = float("nan"), -1

            readings.append((t_now, temp, ldr))
            sample_count += 1

            time.sleep(sample_interval_s)
            elapsed = time.time() - start_time

    finally:
        if serial_obj:
            try:
                serial_obj.close()
            except Exception:
                pass

    print(f"[INFO] Adquisición finalizada: muestras={sample_count}, errores={errors}")
    return readings


# -------------------------
# Procesamiento y estadísticas
# -------------------------
def compute_basic_stats(values):
    """
    Calcula estadísticas básicas (mean, min, max, std) ignorando NaN.
    values: lista de números (puede contener float('nan')).
    Retorna diccionario con keys: mean, min, max, std, count
    """
    clean = [v for v in values if isinstance(v, (int, float)) and not (isinstance(v, float) and (v != v))]
    if not clean:
        return {"mean": None, "min": None, "max": None, "std": None, "count": 0}
    return {
        "mean": round(statistics.mean(clean), 3),
        "min": round(min(clean), 3),
        "max": round(max(clean), 3),
        "std": round(statistics.pstdev(clean), 3),
        "count": len(clean)
    }


# -------------------------
# Guardado CSV y metadata
# -------------------------
def save_csv(readings, csv_path):
    """
    Guarda readings en CSV con encabezado.
    readings: lista de tuplas (timestamp_iso, temp, ldr)
    Implementa escritura atómica.
    """
    header = ["timestamp", "temp_raw", "ldr_raw"]
    lines = [",".join(header) + "\n"]
    for ts, temp, ldr in readings:
        temp_str = "" if (isinstance(temp, float) and temp != temp) else str(temp)
        ldr_str = "" if ldr == -1 else str(ldr)
        lines.append(f"{ts},{temp_str},{ldr_str}\n")
    text = "".join(lines)
    safe_write_atomic(csv_path, text)
    print(f"[INFO] CSV guardado en {csv_path}")


def save_metadata(config, stats_temp, stats_ldr, metadata_path):
    """
    Guarda metadata en JSON (config + stats).
    """
    payload = {
        "timestamp": iso_now_utc(),
        "config": config,
        "stats": {
            "temperature": stats_temp,
            "ldr": stats_ldr
        }
    }
    safe_write_atomic(metadata_path, json.dumps(payload, indent=2))
    print(f"[INFO] Metadata guardada en {metadata_path}")


def save_environment(env_path):
    """
    Guarda información básica del entorno en results/environment.txt
    """
    try:
        py_ver = sys.version.replace("\n", " ")
        libs = {}
        
        # Manejar matplotlib de forma más segura
        if plt is not None:
            try:
                # Intentar obtener versión de matplotlib
                import matplotlib
                libs["matplotlib"] = matplotlib.__version__
            except (AttributeError, ImportError):
                libs["matplotlib"] = "desconocida (error al obtener versión)"
        
        # Manejar numpy de forma más segura
        if np is not None:
            try:
                libs["numpy"] = np.__version__
            except AttributeError:
                libs["numpy"] = "desconocida (error al obtener versión)"
        
        text = f"timestamp: {iso_now_utc()}\npython: {py_ver}\n"
        for k, v in libs.items():
            text += f"{k}: {v}\n"
        
        safe_write_atomic(env_path, text)
        print(f"[INFO] Entorno guardado en {env_path}")
    except Exception as e:
        print(f"[WARN] No se pudo guardar environment.txt: {e}", file=sys.stderr)
        
        
# -------------------------
# Graficado
# -------------------------
def plot_readings(readings, plot_path):
    """
    Genera una gráfica con temperatura y LDR en función del tiempo.
    Guarda en plot_path (PNG).
    Requiere matplotlib; si no está disponible, imprime advertencia.
    """
    if plt is None or np is None:
        print("[WARN] matplotlib o numpy no disponibles; se omite la generación de la gráfica.")
        return

    timestamps = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts, _, _ in readings]
    temps = [temp if not (isinstance(temp, float) and temp != temp) else np.nan for _, temp, _ in readings]
    ldrs = [ldr if ldr != -1 else np.nan for _, _, ldr in readings]

    t_nums = np.array([t.timestamp() for t in timestamps])
    temps_arr = np.array(temps, dtype=float)
    ldrs_arr = np.array(ldrs, dtype=float)

    t0 = t_nums[0] if len(t_nums) > 0 else 0
    x = t_nums - t0

    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(x, temps_arr, color="tab:red", marker="o", label="Temperatura (°C)")
    ax1.set_xlabel("Tiempo (s desde inicio)")
    ax1.set_ylabel("Temperatura (°C)", color="tab:red")
    ax1.tick_params(axis="y", labelcolor="tab:red")

    ax2 = ax1.twinx()
    ax2.plot(x, ldrs_arr, color="tab:blue", marker="x", label="LDR (ADC)")
    ax2.set_ylabel("LDR (ADC)", color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right")

    plt.title("Lecturas: Temperatura y LDR")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    try:
        plt.savefig(plot_path, dpi=150)
        plt.close(fig)
        print(f"[INFO] Gráfica guardada en {plot_path}")
    except Exception as e:
        print(f"[WARN] No se pudo guardar la gráfica: {e}", file=sys.stderr)


# -------------------------
# CLI y flujo principal
# -------------------------
def build_argparser():
    p = argparse.ArgumentParser(description="Adquisición de temperatura y LDR (simulación o serial).")
    p.add_argument("--mode", choices=["sim", "serial"], default="sim", help="Modo de adquisición: sim (simulación) o serial")
    p.add_argument("--port", type=str, default=None, help="Puerto serial (ej: COM3 o /dev/ttyUSB0)")
    p.add_argument("--baud", type=int, default=115200, help="Baudrate para serial")
    p.add_argument("--duration", type=int, default=DEFAULT_DURATION, help="Duración total en segundos")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help="Intervalo entre muestras en segundos")
    return p


def main():
    parser = build_argparser()
    args = parser.parse_args()

    ensure_results_dir()

    config = {
        "mode": args.mode,
        "port": args.port,
        "baud": args.baud,
        "duration_seconds": args.duration,
        "sample_interval_s": args.interval,
        "script": os.path.basename(__file__),
        "version": "1.0.1"
    }

    save_environment(os.path.join(RESULTS_DIR, "environment.txt"))

    readings = acquire_data(mode=args.mode, port=args.port, baud=args.baud,
                            duration_seconds=args.duration, sample_interval_s=args.interval)

    temps = [t for _, t, _ in readings]
    ldrs = [l for _, _, l in readings]
    stats_temp = compute_basic_stats(temps)
    stats_ldr = compute_basic_stats(ldrs)

    csv_path = os.path.join(RESULTS_DIR, "raw_readings.csv")
    metadata_path = os.path.join(RESULTS_DIR, "metadata.json")
    save_csv(readings, csv_path)
    save_metadata(config, stats_temp, stats_ldr, metadata_path)

    plot_path = os.path.join(RESULTS_DIR, "plot.png")
    plot_readings(readings, plot_path)

    print("\n--- Resumen ---")
    print(f"Muestras: {len(readings)}")
    print("Estadísticas Temperatura:", stats_temp)
    print("Estadísticas LDR:", stats_ldr)
    print(f"Archivos generados en: {RESULTS_DIR}/")
    print("----------------\n")


if __name__ == "__main__":
    main()
