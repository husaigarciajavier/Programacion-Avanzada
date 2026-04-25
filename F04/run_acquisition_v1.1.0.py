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
    import matplotlib
    import numpy as np
except Exception:
    plt = None
    matplotlib = None
    np = None

# -------------------------
# Configuración por defecto
# -------------------------
DEFAULT_DURATION = 60          # segundos
DEFAULT_INTERVAL = 1           # segundos entre muestras
DEFAULT_CALIBRATION_SAMPLES = 10  # muestras iniciales para calibración
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


def moving_median(values, window_size=5):
    """
    Calcula la mediana móvil sobre una lista de valores.
    values: lista de valores numéricos
    window_size: tamaño de la ventana para la mediana móvil
    Retorna lista de medianas móviles (mismo tamaño que values)
    """
    if not values or window_size < 1:
        return values
    
    result = []
    for i in range(len(values)):
        # Definir ventana
        start = max(0, i - window_size // 2)
        end = min(len(values), i + window_size // 2 + 1)
        window = values[start:end]
        
        # Calcular mediana de la ventana
        sorted_window = sorted(window)
        n = len(sorted_window)
        if n % 2 == 0:
            median = (sorted_window[n//2 - 1] + sorted_window[n//2]) / 2
        else:
            median = sorted_window[n//2]
        result.append(median)
    
    return result


# -------------------------
# Calibración
# -------------------------
class Calibrator:
    """Clase para manejar calibración de sensores"""
    
    def __init__(self, calibration_samples=10):
        self.calibration_samples = calibration_samples
        self.temp_offset = 0.0
        self.ldr_offset = 0
        self.is_calibrated = False
        self.temp_calibration_readings = []
        self.ldr_calibration_readings = []
    
    def add_sample(self, temp_raw, ldr_raw):
        """Agrega una muestra para calibración"""
        if not self.is_calibrated and len(self.temp_calibration_readings) < self.calibration_samples:
            self.temp_calibration_readings.append(temp_raw)
            self.ldr_calibration_readings.append(ldr_raw)
            
            if len(self.temp_calibration_readings) == self.calibration_samples:
                # Calcular offsets usando mediana
                temp_median = statistics.median(self.temp_calibration_readings)
                ldr_median = statistics.median(self.ldr_calibration_readings)
                
                # Asumimos que el valor esperado para temperatura es 22°C (ambiente)
                # y para LDR es 500 (valor típico medio)
                self.temp_offset = 22.0 - temp_median
                self.ldr_offset = 500 - ldr_median
                self.is_calibrated = True
                
                print(f"[INFO] Calibración completada:")
                print(f"  - Temp: offset={self.temp_offset:.2f}°C (media muestras: {temp_median:.2f})")
                print(f"  - LDR: offset={self.ldr_offset} ADC (mediana muestras: {ldr_median})")
    
    def calibrate_temp(self, temp_raw):
        """Aplica calibración a temperatura"""
        if self.is_calibrated:
            return round(temp_raw + self.temp_offset, 2)
        return temp_raw
    
    def calibrate_ldr(self, ldr_raw):
        """Aplica calibración a LDR"""
        if self.is_calibrated and ldr_raw != -1:
            calibrated = ldr_raw + self.ldr_offset
            return int(max(0, min(1023, calibrated)))
        return ldr_raw
    
    def get_stats(self):
        """Retorna estadísticas de calibración"""
        if self.is_calibrated:
            return {
                "calibrated": True,
                "temp_offset": round(self.temp_offset, 2),
                "ldr_offset": self.ldr_offset,
                "calibration_samples": self.calibration_samples
            }
        return {"calibrated": False}


# -------------------------
# Simulación y lectura
# -------------------------
def simulate_reading(t_seconds):
    """
    Genera una lectura simulada de temperatura y LDR.
    t_seconds: tiempo transcurrido desde inicio (s) para modelar tendencias.
    Retorna (temp_c, ldr_raw)
    """
    # Temperatura base con ligera deriva y ruido
    temp_base = 22.0 + 0.01 * (t_seconds / 1.0)  # deriva muy lenta
    temp_noise = random.gauss(0, 0.2)            # ruido gaussiano
    temp = temp_base + temp_noise

    # LDR simulado: valor ADC 0-1023 con variaciones y picos ocasionales
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
def acquire_data(mode="sim", port=None, baud=115200, duration_seconds=DEFAULT_DURATION, 
                 sample_interval_s=DEFAULT_INTERVAL, calibration_samples=DEFAULT_CALIBRATION_SAMPLES):
    """
    Ejecuta la adquisición de datos.
    mode: "sim" o "serial"
    Retorna lista de tuplas: (timestamp_iso, temp_raw, ldr_raw, temp_cal, ldr_cal)
    """
    readings = []
    start_time = time.time()
    elapsed = 0.0
    sample_count = 0
    errors = 0
    
    # Inicializar calibrador
    calibrator = Calibrator(calibration_samples)

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

    print(f"[INFO] Inicio adquisición: modo={mode}, duración={duration_seconds}s, "
          f"intervalo={sample_interval_s}s, muestras_calib={calibration_samples}")
    
    try:
        while elapsed < duration_seconds:
            t_now = iso_now_utc()
            try:
                if mode == "sim":
                    temp_raw, ldr_raw = simulate_reading(elapsed)
                else:
                    raw_line = serial_obj.readline().decode("utf-8", errors="ignore")
                    if not raw_line:
                        raise IOError("Timeout o línea vacía desde serial")
                    temp_raw, ldr_raw = parse_serial_line(raw_line)
            except Exception as e:
                errors += 1
                print(f"[ERROR] lectura fallida en t={elapsed:.1f}s: {e}", file=sys.stderr)
                temp_raw, ldr_raw = float("nan"), -1
            
            # Calibración y filtrado
            # Primero agregar a calibración si aún no está calibrado
            if not calibrator.is_calibrated and not (isinstance(temp_raw, float) and temp_raw != temp_raw):
                calibrator.add_sample(temp_raw, ldr_raw)
            
            # Aplicar calibración
            temp_cal = calibrator.calibrate_temp(temp_raw)
            ldr_cal = calibrator.calibrate_ldr(ldr_raw)
            
            readings.append((t_now, temp_raw, ldr_raw, temp_cal, ldr_cal))
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
    
    # Aplicar mediana móvil después de la adquisición
    if len(readings) > 0:
        temps_cal = [r[3] for r in readings if not (isinstance(r[3], float) and r[3] != r[3])]
        ldrs_cal = [r[4] for r in readings if r[4] != -1]
        
        if len(temps_cal) > 5:
            temps_median = moving_median(temps_cal, window_size=5)
            ldrs_median = moving_median(ldrs_cal, window_size=5)
            
            # Reemplazar valores calibrados con versión mediana móvil
            new_readings = []
            temp_idx = 0
            ldr_idx = 0
            for ts, tr, lr, tc, lc in readings:
                new_tc = temps_median[temp_idx] if not (isinstance(tc, float) and tc != tc) else tc
                new_lc = int(ldrs_median[ldr_idx]) if lc != -1 else lc
                new_readings.append((ts, tr, lr, new_tc, new_lc))
                if not (isinstance(tc, float) and tc != tc):
                    temp_idx += 1
                if lc != -1:
                    ldr_idx += 1
            readings = new_readings
    
    return readings, calibrator


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


def compute_median(values):
    """
    Calcula la mediana de una lista de valores ignorando NaN.
    """
    clean = [v for v in values if isinstance(v, (int, float)) and not (isinstance(v, float) and (v != v))]
    if not clean:
        return None
    return round(statistics.median(clean), 3)


# -------------------------
# Guardado CSV y metadata
# -------------------------
def save_csv(readings, csv_path):
    """
    Guarda readings en CSV con encabezado.
    readings: lista de tuplas (timestamp_iso, temp_raw, ldr_raw, temp_cal, ldr_cal)
    Implementa escritura atómica.
    """
    header = ["timestamp", "temp_raw", "ldr_raw", "temp_calibrated", "ldr_calibrated"]
    lines = [",".join(header) + "\n"]
    for ts, temp_r, ldr_r, temp_c, ldr_c in readings:
        temp_r_str = "" if (isinstance(temp_r, float) and temp_r != temp_r) else str(temp_r)
        ldr_r_str = "" if ldr_r == -1 else str(ldr_r)
        temp_c_str = "" if (isinstance(temp_c, float) and temp_c != temp_c) else str(temp_c)
        ldr_c_str = "" if ldr_c == -1 else str(ldr_c)
        lines.append(f"{ts},{temp_r_str},{ldr_r_str},{temp_c_str},{ldr_c_str}\n")
    text = "".join(lines)
    safe_write_atomic(csv_path, text)
    print(f"[INFO] CSV guardado en {csv_path}")


def save_metadata(config, stats_temp_raw, stats_temp_cal, stats_ldr_raw, stats_ldr_cal, 
                  calibrator_stats, metadata_path):
    """
    Guarda metadata en JSON (config + stats).
    """
    payload = {
        "timestamp": iso_now_utc(),
        "config": config,
        "calibration": calibrator_stats,
        "stats": {
            "temperature_raw": stats_temp_raw,
            "temperature_calibrated": stats_temp_cal,
            "ldr_raw": stats_ldr_raw,
            "ldr_calibrated": stats_ldr_cal
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
        
        if matplotlib is not None:
            try:
                libs["matplotlib"] = matplotlib.__version__
            except (AttributeError, ImportError):
                libs["matplotlib"] = "instalado pero no se pudo obtener versión"
        
        if np is not None:
            try:
                libs["numpy"] = np.__version__
            except AttributeError:
                libs["numpy"] = "instalado pero no se pudo obtener versión"
        
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

    timestamps = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts, _, _, _, _ in readings]
    temps_raw = [temp_r if not (isinstance(temp_r, float) and temp_r != temp_r) else np.nan 
                 for _, temp_r, _, _, _ in readings]
    temps_cal = [temp_c if not (isinstance(temp_c, float) and temp_c != temp_c) else np.nan 
                 for _, _, _, temp_c, _ in readings]
    ldrs_raw = [ldr_r if ldr_r != -1 else np.nan for _, _, ldr_r, _, _ in readings]
    ldrs_cal = [ldr_c if ldr_c != -1 else np.nan for _, _, _, _, ldr_c in readings]

    t_nums = np.array([t.timestamp() for t in timestamps])
    t0 = t_nums[0] if len(t_nums) > 0 else 0
    x = t_nums - t0

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Gráfica de Temperatura
    ax1 = axes[0]
    ax1.plot(x, temps_raw, color="tab:red", marker="o", markersize=3, 
             label="Temperatura Raw", alpha=0.7)
    ax1.plot(x, temps_cal, color="tab:orange", linewidth=2, 
             label="Temperatura Calibrada + Mediana Móvil")
    ax1.set_xlabel("Tiempo (s desde inicio)")
    ax1.set_ylabel("Temperatura (°C)")
    ax1.set_title("Temperatura: Raw vs Calibrada")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.3)
    
    # Gráfica de LDR
    ax2 = axes[1]
    ax2.plot(x, ldrs_raw, color="tab:blue", marker="x", markersize=3, 
             label="LDR Raw", alpha=0.7)
    ax2.plot(x, ldrs_cal, color="tab:cyan", linewidth=2, 
             label="LDR Calibrada + Mediana Móvil")
    ax2.set_xlabel("Tiempo (s desde inicio)")
    ax2.set_ylabel("LDR (ADC)")
    ax2.set_title("LDR: Raw vs Calibrada")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.3)

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
    p = argparse.ArgumentParser(description="Adquisición de temperatura y LDR con calibración y filtrado.")
    p.add_argument("--mode", choices=["sim", "serial"], default="sim", 
                   help="Modo de adquisición: sim (simulación) o serial")
    p.add_argument("--port", type=str, default=None, 
                   help="Puerto serial (ej: COM3 o /dev/ttyUSB0)")
    p.add_argument("--baud", type=int, default=115200, 
                   help="Baudrate para serial")
    p.add_argument("--duration", type=int, default=DEFAULT_DURATION, 
                   help="Duración total en segundos")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, 
                   help="Intervalo entre muestras en segundos")
    p.add_argument("--cal-samples", type=int, default=DEFAULT_CALIBRATION_SAMPLES, 
                   help="Número de muestras iniciales para calibración")
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
        "calibration_samples": args.cal_samples,
        "script": os.path.basename(__file__),
        "version": "1.1.0"
    }

    save_environment(os.path.join(RESULTS_DIR, "environment.txt"))

    readings, calibrator = acquire_data(mode=args.mode, port=args.port, baud=args.baud,
                                        duration_seconds=args.duration, 
                                        sample_interval_s=args.interval,
                                        calibration_samples=args.cal_samples)

    # Extraer datos para estadísticas
    temps_raw = [r[1] for r in readings]
    temps_cal = [r[3] for r in readings]
    ldrs_raw = [r[2] for r in readings]
    ldrs_cal = [r[4] for r in readings]
    
    # Calcular estadísticas
    stats_temp_raw = compute_basic_stats(temps_raw)
    stats_temp_cal = compute_basic_stats(temps_cal)
    stats_ldr_raw = compute_basic_stats(ldrs_raw)
    stats_ldr_cal = compute_basic_stats(ldrs_cal)
    
    # Calcular medianas adicionales
    median_temp_raw = compute_median(temps_raw)
    median_temp_cal = compute_median(temps_cal)
    median_ldr_raw = compute_median(ldrs_raw)
    median_ldr_cal = compute_median(ldrs_cal)
    
    calibrator_stats = calibrator.get_stats()

    csv_path = os.path.join(RESULTS_DIR, "raw_readings.csv")
    metadata_path = os.path.join(RESULTS_DIR, "metadata.json")
    save_csv(readings, csv_path)
    save_metadata(config, stats_temp_raw, stats_temp_cal, stats_ldr_raw, stats_ldr_cal,
                  calibrator_stats, metadata_path)

    plot_path = os.path.join(RESULTS_DIR, "plot.png")
    plot_readings(readings, plot_path)

    print("\n--- Resumen ---")
    print(f"Muestras: {len(readings)}")
    print(f"Calibración: {'Completada' if calibrator_stats.get('calibrated') else 'No realizada'}")
    if calibrator_stats.get('calibrated'):
        print(f"  - Offset Temperatura: {calibrator_stats.get('temp_offset', 0):.2f}°C")
        print(f"  - Offset LDR: {calibrator_stats.get('ldr_offset', 0)}")
    print("\nEstadísticas Temperatura Raw:")
    print(f"  Media: {stats_temp_raw['mean']} | Mediana: {median_temp_raw} | "
          f"Min: {stats_temp_raw['min']} | Max: {stats_temp_raw['max']} | "
          f"Std: {stats_temp_raw['std']}")
    print("Estadísticas Temperatura Calibrada:")
    print(f"  Media: {stats_temp_cal['mean']} | Mediana: {median_temp_cal} | "
          f"Min: {stats_temp_cal['min']} | Max: {stats_temp_cal['max']} | "
          f"Std: {stats_temp_cal['std']}")
    print("\nEstadísticas LDR Raw:")
    print(f"  Media: {stats_ldr_raw['mean']} | Mediana: {median_ldr_raw} | "
          f"Min: {stats_ldr_raw['min']} | Max: {stats_ldr_raw['max']} | "
          f"Std: {stats_ldr_raw['std']}")
    print("Estadísticas LDR Calibrada:")
    print(f"  Media: {stats_ldr_cal['mean']} | Mediana: {median_ldr_cal} | "
          f"Min: {stats_ldr_cal['min']} | Max: {stats_ldr_cal['max']} | "
          f"Std: {stats_ldr_cal['std']}")
    print(f"\nArchivos generados en: {RESULTS_DIR}/")
    print("----------------\n")


if __name__ == "__main__":
    main()