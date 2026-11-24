"""
Converte o MIMIC-IV (.csv.gz) para Parquet UMA vez, com DuckDB, para o notebook ler em segundos.

Uso (no terminal, na pasta do projeto, com o ambiente eng_biomedica):
    python preparar_mimic.py "mimic completo"

Gera "mimic completo/parquet/<tabela>.parquet". O que cada arquivo contém:
  * patients, admissions, icustays, d_items, diagnoses_icd, inputevents: tabela inteira
  * chartevents: SÓ pressão arterial (PAM, PAS, PAD), FC, débito cardíaco, volume sistólico e PVC.
    O original tem ~430 milhões de linhas; o notebook só usa essas.
  * prescriptions: SÓ as linhas de IECA/BRA (a lista é a mesma da seção 6 do notebook).
Se mudar o que o notebook precisa dessas duas tabelas, apague o .parquet e rode de novo.

Pode interromper e rodar de novo: tabelas já convertidas são puladas (use --refazer para refazer tudo).
"""
import os
import sys
import time

import duckdb

PRESSAO = [  # rótulos do d_items usados na seção 5 do notebook
    "Arterial Blood Pressure mean", "Arterial Blood Pressure systolic", "Arterial Blood Pressure diastolic",
    "ART BP Mean", "ART BP Systolic", "ART BP Diastolic",
    "Non Invasive Blood Pressure mean", "Non Invasive Blood Pressure systolic",
    "Non Invasive Blood Pressure diastolic",
    # entradas da planta individual (planta_individual.jl): FC, DC medido, volume sistólico, PVC
    "Heart Rate", "Cardiac Output (thermodilution)", "Cardiac Output (CCO)", "Cardiac Output (CO NICOM)",
    "Stroke Volume (SV NICOM)", "Central Venous Pressure",
]
IECA_BRA = ("lisinopril|enalapril|captopril|ramipril|benazepril|fosinopril|quinapril|perindopril|"
            "losartan|valsartan|candesartan|telmisartan|olmesartan|irbesartan")
INTEIRAS = ["patients", "admissions", "icustays", "d_items", "diagnoses_icd", "inputevents"]


def achar(pasta, nome):
    for sub in ("", "hosp", "icu"):
        for ext in (".csv.gz", ".csv"):
            cam = os.path.join(pasta, sub, nome + ext)
            if os.path.exists(cam):
                return cam.replace(os.sep, "/")
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    refazer = "--refazer" in sys.argv
    pasta = args[0] if args else os.environ.get("MIMIC_DIR", "mimic completo")
    saida = os.path.join(pasta, "parquet")
    os.makedirs(saida, exist_ok=True)

    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{os.path.join(saida, '_tmp').replace(os.sep, '/')}'")
    con.execute("SET preserve_insertion_order = false")   # menos memória em tabelas grandes

    def converter(nome, sql_select):
        destino = os.path.join(saida, f"{nome}.parquet").replace(os.sep, "/")
        if os.path.exists(destino) and not refazer:
            print(f"  {nome}: já existe, pulando")
            return
        t = time.time()
        tmp = destino + ".parcial"
        con.execute(f"COPY ({sql_select}) TO '{tmp}' (FORMAT parquet, COMPRESSION zstd)")
        os.replace(tmp, destino)       # só aparece com o nome final quando terminou
        n = con.execute(f"SELECT count(*) FROM read_parquet('{destino}')").fetchone()[0]
        mb = os.path.getsize(destino) / 1e6
        print(f"  {nome}: {n:,} linhas, {mb:,.0f} MB, {time.time() - t:,.0f} s")

    def csv(nome):
        cam = achar(pasta, nome)
        if cam is None:
            raise FileNotFoundError(f"{nome}.csv(.gz) não está em {pasta}")
        # all_varchar=false + amostra grande: o DuckDB acerta os tipos (datas viram TIMESTAMP)
        return f"read_csv('{cam}', header = true, sample_size = 200000)"

    print(f"Pasta: {pasta}\nSaída: {saida}")
    for nome in INTEIRAS:
        converter(nome, f"SELECT * FROM {csv(nome)}")

    rotulos = ", ".join(f"'{r.lower()}'" for r in PRESSAO)
    ids = [r[0] for r in con.execute(
        f"SELECT itemid FROM {csv('d_items')} WHERE lower(label) IN ({rotulos})").fetchall()]
    print(f"  itemids de pressão: {sorted(ids)}")
    converter("chartevents", f"""
        SELECT subject_id, hadm_id, stay_id, charttime, itemid, valuenum, valueuom
        FROM {csv('chartevents')}
        WHERE itemid IN ({', '.join(map(str, ids))})""")

    converter("prescriptions", f"""
        SELECT * FROM {csv('prescriptions')}
        WHERE regexp_matches(lower(drug), '{IECA_BRA}')""")
    print("Pronto. O notebook usa estes arquivos automaticamente.")


if __name__ == "__main__":
    main()
