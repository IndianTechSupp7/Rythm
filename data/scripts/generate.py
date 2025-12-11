import sys
import os
import json
import numpy as np
import librosa
from scipy.signal import butter, lfilter
from demucs.separate import main as demucs_main
import shutil
import psutil  # Új import

from multiprocessing import Process, Queue

# === Tunable parameters ===
ONSET_SENSITIVITY = 0.15


# === Bandpass filter function (Marad) ===
def bandpass_filter(data, sr, lowcut, highcut):
    """Butterworth bandpass szűrő alkalmazása az adatokra."""
    nyquist = 0.5 * sr
    low = max(0.001, lowcut / nyquist)
    high = min(0.999, highcut / nyquist)
    if high <= low:
        high = low + 0.001
    b, a = butter(4, [low, high], btype="band")
    return lfilter(b, a, data)


# === A MUNKAFOLYAMAT FÜGGVÉNYE (Módosítva) ===
def _generate_beatmap_worker(
    raw_song_path, beatmap_base_dir, song_base_dir, temp_base_dir, queue
):
    """
    A teljes beatmap generáló logika, ami KÜLÖN FOLYAMATBAN fut.
    NEM menti el külön a drums.mp3 fájlt a végső kimeneti mappába.
    """

    def send_progress(p, msg):
        queue.put(
            {"status": "RUNNING", "progress": float(max(0, min(1, p))), "message": msg}
        )

    send_progress(0.05, "Demucs: initializing...")
    try:
        # === CPU Prioritás csökkentése a játék kedvéért ===
        current_process = psutil.Process(os.getpid())

        # A nice érték megadása. Minél nagyobb a szám, annál alacsonyabb a prioritás.
        # Windowson az 1 alacsony, Lin/Mac-en 19 nagyon alacsony.
        # if os.name == "nt":  # Windows
        #     current_process.nice = psutil.BELOW_NORMAL_PRIORITY_CLASS
        #     print("   -> CPU prioritás beállítva: ALACSONY")
        # else:  # Linux/macOS
        #     current_process.nice = 10  # 0 és 19 között, a 10 közepesen alacsony
        #     print("   -> CPU prioritás beállítva: 10 (ALACSONY)")
        # ===================================================

        song_name = os.path.splitext(os.path.basename(raw_song_path))[0]
        temp_drums_dir = os.path.join(temp_base_dir, "htdemucs", song_name)
        drums_path_temp = os.path.join(temp_drums_dir, "drums.mp3")

        # A forrásfájl másolatának helye a feldolgozási mappában (kötelező, mert Demucs átnevezi)
        destination = os.path.join(song_base_dir, os.path.basename(raw_song_path))

        # Belső takarítási funkció (Most már a dobfájl törlését is tartalmazza)
        def cleanup():
            if os.path.exists(temp_drums_dir):
                # Töröljük a Demucs ideiglenes kimeneti mappáját, ami tartalmazza a drums.mp3-at
                shutil.rmtree(temp_drums_dir, ignore_errors=True)
                print(f"   -> ✅ Ideiglenes Demucs mappa törölve: {temp_drums_dir}")

            # Töröljük a separated_temp/htdemucs/ mappa fölötti mappát is, ha üres
            if os.path.exists(temp_base_dir) and not os.listdir(
                os.path.join(temp_base_dir, "htdemucs")
            ):
                try:
                    shutil.rmtree(temp_base_dir)
                except OSError:
                    pass

        # A forrásfájl másolatát megtarthatjuk, de ha nem akarod, ezt is törölheted:
        # if os.path.exists(destination):
        #     os.remove(destination)
        #     print(f"   -> ✅ Másolt forrásfájl törölve: {destination}")

        # --- Előkészületek ---
        # os.makedirs(output_folder, exist_ok=True)
        shutil.copy(raw_song_path, destination)
        send_progress(0.10, "Demucs: copying source...")

        # === Step 1: Separate drums using Demucs ===

        print(f"   -> Demucs: Dobok szétválasztása: {song_name}")

        demucs_args = [
            "--mp3",
            "-n",
            "htdemucs",
            "-o",
            temp_base_dir,
            "--two-stems",
            "drums",
            destination,
        ]
        send_progress(0.15, "Demucs: separating drums...")
        demucs_main(demucs_args)
        send_progress(0.50, "Demucs kész!")

        if not os.path.exists(drums_path_temp):
            raise FileNotFoundError(f"Demucs nem generált dob fájlt: {drums_path_temp}")

        # !!! ITT KÖZVETLENÜL TÖLTJÜK BE A FÁJLT A MEMÓRIÁBA !!!
        send_progress(0.55, "Librosa: audio betöltése...")
        y, sr = librosa.load(drums_path_temp)  # <-- Itt van a kulcsa!
        print(f"   -> Librosa: Dob audio betöltve a temp mappából (sr={sr}).")
        send_progress(0.60, "Librosa: kész.")

        # === Step 2 & 3: Bandpass szűrés, onset detektálás ===

        bands = {
            "Kick": bandpass_filter(y, sr, 30, 120),
            "Snare": bandpass_filter(y, sr, 120, 2500),
            "Tom": bandpass_filter(y, sr, 200, 1000),
            "Cymbal": bandpass_filter(y, sr, 4000, 10000),
        }
        instrument_list = list(bands.keys())
        total = len(instrument_list)

        onsets = {}
        strengths = {}

        queue.put(
            {
                "status": "RUNNING",
                "message": "3/3: Ütés detektálás és JSON generálás...",
            }
        )

        for i, (name, data) in enumerate(bands.items()):
            send_progress(0.60 + (i / total) * 0.30, f"Onset detektálás: {name}")
            y_h, y_p = librosa.effects.hpss(data)
            onset_env = librosa.onset.onset_strength(y=y_p, sr=sr)
            onset_frames = librosa.onset.onset_detect(
                onset_envelope=onset_env,
                sr=sr,
                units="frames",
                delta=ONSET_SENSITIVITY,
                backtrack=False,
                pre_max=10,
                post_max=10,
                pre_avg=30,
                post_avg=30,
                wait=0,
            )
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            s_values = (
                np.take(onset_env, onset_frames) if len(onset_frames) else np.array([])
            )
            if len(s_values) > 0:
                s_values = (s_values - np.min(s_values)) / (np.ptp(s_values) + 1e-6)
            onsets[name] = onset_times
            strengths[name] = s_values

        # === Step 4: Save beatmap JSON ===
        send_progress(0.95, "JSON export...")
        beatmap = {
            "song": os.path.basename(raw_song_path),
            "bpm": float(librosa.beat.tempo(y=y, sr=sr, aggregate=np.mean)[0]),
            "sample_rate": int(sr),
            "tracks": {},
        }

        for name in onsets.keys():
            # ... (A beatmap létrehozás logikája változatlan)
            beatmap["tracks"][name] = []
            for i, t in enumerate(onsets[name]):
                s = float(strengths[name][i]) if len(strengths[name]) > i else 1.0
                beatmap["tracks"][name].append(
                    {"time": round(float(t), 3), "strength": round(s, 3)}
                )
            beatmap["tracks"][name] = sorted(
                beatmap["tracks"][name], key=lambda x: x["time"]
            )

        beatmap_path = os.path.join(beatmap_base_dir, f"{song_name}.json")
        with open(beatmap_path, "w", encoding="utf-8") as f:
            json.dump(beatmap, f, indent=4)

        # Sikeres befejezés jelzése
        queue.put(
            {
                "status": "COMPLETED",
                "result_path": beatmap_path,
                "message": f"Beatmap exportálva: {beatmap_path}",
                "progress": 1,
            }
        )

    except Exception as e:
        # Hiba jelzése
        queue.put({"status": "ERROR", "error_message": f"Hiba a generálás során: {e}"})
    finally:
        # FONTOS: Törlés a végén!
        cleanup()
        print("Munkás folyamat befejeződött.")


# A BeatmapGenerator osztály interfésze (nem szükséges módosítani)
class BeatmapGenerator:
    """
    Kezelő osztály a Pygame fő folyamatában.
    """

    def __init__(
        self,
        beatmap_base_dir="beatmaps",
        song_base_dir="songs",
        temp_base_dir="separated_temp",
    ):
        self.beatmap_base_dir = beatmap_base_dir
        self.song_base_dir = song_base_dir
        self.temp_base_dir = temp_base_dir
        self.process = None
        self.queue = Queue()
        self.status_data = {"status": "IDLE", "message": "Készenlétben", "progress": 0}

    def start_generation(self, raw_song_path):
        """Elindítja a beatmap generálást egy különálló folyamatban."""
        if self.process and self.process.is_alive():
            print("A generálás már fut. Várj, amíg befejeződik.")
            return False

        self.process = Process(
            target=_generate_beatmap_worker,
            args=(
                raw_song_path,
                self.beatmap_base_dir,
                self.song_base_dir,
                self.temp_base_dir,
                self.queue,
            ),
        )
        self.process.start()
        self.status_data = {"status": "STARTING", "message": "Generálás indítása...", "progress": 0}
        print("Beatmap generálás elindítva külön folyamatban.")
        return True

    def check_status(self):
        """
        Lekéri az állapotot a queue-ból és visszaadja az aktuális állapotot.
        Ezt kell hívnod a Pygame fő ciklusodban!
        """
        while not self.queue.empty():
            self.status_data = self.queue.get()

        if (
            self.process
            and not self.process.is_alive()
            and self.status_data["status"] not in ["COMPLETED", "ERROR"]
        ):
            self.status_data = {
                "status": "ERROR",
                "error_message": "Váratlan hiba: a folyamat leállt.",
            }

        return self.status_data


# === Példa használat (Pygame szimuláció) ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py generate.py <song_file>")
        sys.exit(1)

    song_file = sys.argv[1]

    if not os.path.exists(song_file):
        print(f"Hiba: A fájl nem található: {song_file}")
        sys.exit(1)

    # Inicializálás
    generator = BeatmapGenerator()

    # Generálás indítása
    if generator.start_generation(song_file):
        print("\n--- Pygame fő ciklus szimulálva ---")

        running = True
        while running:
            status = generator.check_status()

            # Képernyő/konzol frissítés
            print(
                f"[{status['status']}] Játék fut. Üzenet: {status['message']}", end="\r"
            )

            if status["status"] == "COMPLETED":
                print(f"\n✅ SIKER! Beatmap mentve ide: {status['result_path']}")
                running = False
            elif status["status"] == "ERROR":
                print(f"\n❌ HIBA: {status['error_message']}")
                running = False

            # Szimuláció
            import time

            time.sleep(0.5)
