import csv
import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "nckh_ctdlgt_2026")

# 85 canh tien quyet khoi tao (A -[:REQUIRES]-> B nghia la: de hoc A can nam vung B)
INITIAL_REQUIRES_EDGES = [
    # Chuong 1
    ("C01_02", "C01_01"),
    ("C01_03", "C01_01"),
    ("C01_04", "C01_03"),
    ("C01_05", "C01_03"),
    ("C01_06", "C01_05"),
    ("C01_07", "C01_06"),
    ("C01_08", "C01_03"),
    ("C01_09", "C01_04"),
    ("C01_10", "C01_08"),
    ("C01_10", "C01_09"),
    ("C01_11", "C01_08"),
    ("C01_11", "C01_09"),
    # Chuong 2
    ("C02_01", "C01_02"),
    ("C02_02", "C02_01"),
    ("C02_03", "C02_01"),
    ("C02_03", "C01_05"),
    ("C02_04", "C02_01"),
    ("C02_05", "C02_04"),
    ("C02_06", "C02_02"),
    ("C02_06", "C02_05"),
    ("C02_07", "C02_02"),
    ("C02_07", "C02_04"),
    ("C02_08", "C02_04"),
    ("C02_08", "C02_03"),
    # Chuong 3
    ("C03_01", "C01_02"),
    ("C03_02", "C03_01"),
    ("C03_03", "C03_02"),
    ("C03_03", "C02_01"),
    ("C03_04", "C03_02"),
    ("C03_04", "C02_01"),
    ("C03_05", "C03_03"),
    ("C03_05", "C03_04"),
    ("C03_05", "C01_09"),
    ("C03_06", "C03_01"),
    ("C03_07", "C03_06"),
    ("C03_07", "C02_01"),
    ("C03_08", "C03_07"),
    ("C03_09", "C03_01"),
    ("C03_09", "C01_02"),
    ("C03_10", "C03_09"),
    ("C03_11", "C03_10"),
    ("C03_12", "C03_10"),
    ("C03_13", "C03_09"),
    ("C03_14", "C03_13"),
    ("C03_14", "C03_11"),
    ("C03_14", "C03_12"),
    # Chuong 4
    ("C04_01", "C01_01"),
    ("C04_02", "C04_01"),
    ("C04_03", "C04_02"),
    ("C04_03", "C02_01"),
    ("C04_03", "C03_09"),
    ("C04_04", "C04_02"),
    ("C04_04", "C01_09"),
    ("C04_05", "C04_02"),
    ("C04_05", "C01_09"),
    ("C04_06", "C04_02"),
    ("C04_06", "C01_09"),
    ("C04_07", "C04_02"),
    ("C04_08", "C04_07"),
    ("C04_08", "C01_09"),
    ("C04_09", "C04_08"),
    ("C04_10", "C04_09"),
    ("C04_10", "C04_03"),
    # Chuong 5
    ("C05_01", "C01_01"),
    ("C05_02", "C05_01"),
    ("C05_03", "C05_01"),
    ("C05_03", "C02_04"),
    ("C05_04", "C05_01"),
    ("C05_04", "C03_09"),
    ("C05_05", "C05_01"),
    ("C05_05", "C02_01"),
    ("C05_06", "C05_03"),
    ("C05_06", "C05_04"),
    ("C05_06", "C03_02"),
    ("C05_06", "C01_09"),
    ("C05_07", "C05_03"),
    ("C05_07", "C05_04"),
    ("C05_07", "C03_06"),
    ("C05_08", "C05_02"),
    ("C05_08", "C05_03"),
    ("C05_08", "C01_11"),
    ("C05_09", "C05_02"),
    ("C05_09", "C05_05"),
    ("C05_09", "C01_11"),
    # Chuong 6
    ("C06_01", "C02_03"),
    ("C06_01", "C01_06"),
    ("C06_02", "C06_01"),
    ("C06_03", "C06_01"),
    ("C06_04", "C06_01"),
    ("C06_05", "C06_01"),
    ("C06_05", "C01_10"),
    ("C06_06", "C06_01"),
    ("C06_06", "C01_10"),
    ("C06_07", "C06_02"),
    ("C06_07", "C04_10"),
    ("C06_08", "C06_02"),
    ("C06_08", "C06_03"),
    ("C06_08", "C06_04"),
    ("C06_08", "C06_05"),
    ("C06_08", "C06_06"),
    ("C06_08", "C06_07"),
    # Chuong 7
    ("C07_01", "C02_03"),
    ("C07_02", "C07_01"),
    ("C07_03", "C07_01"),
    ("C07_03", "C06_01"),
    ("C07_03", "C01_10"),
    ("C07_04", "C07_01"),
    ("C07_04", "C04_08"),
    ("C07_05", "C07_01"),
    ("C07_05", "C02_02"),
    ("C07_06", "C07_05"),
    ("C07_06", "C03_09"),
    # Chuong 8
    ("C08_01", "C01_02"),
    ("C08_02", "C08_01"),
    ("C08_03", "C08_02"),
    ("C08_03", "C01_05"),
    ("C08_04", "C08_03"),
    ("C08_04", "C06_06"),
    ("C08_04", "C07_04"),
]


def run_init():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        # 1. Xoa cac nut demo C01..C10 cu (neu co) de do thi sach se
        session.run(
            "MATCH (c:Concept) WHERE size(c.concept_id) = 3 DETACH DELETE c"
        )

        # 2. Chay db/schema.cypher
        if os.path.exists("db/schema.cypher"):
            with open("db/schema.cypher", "r", encoding="utf-8") as f:
                stmts = [s.strip() for s in f.read().split(";") if s.strip()]
            for stmt in stmts:
                lines = [
                    l
                    for l in stmt.splitlines()
                    if not l.strip().startswith("//")
                ]
                q = "\n".join(lines).strip()
                if q:
                    session.run(q)
            print("[OK] Da khoi tao Schema & Constraints tu db/schema.cypher")

        # 3. Nap 70 khai niem tu data/concepts_v0.csv
        csv_path = "data/concepts_v0.csv"
        query_node = """
        MERGE (c:Concept {concept_id: $concept_id})
        SET c.name_vi = $name_vi,
            c.name_en = $name_en,
            c.definition = $definition,
            c.chapter = $chapter,
            c.course = 'TIHT1101_CTDL_GT'
        """
        count = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                session.run(query_node, **row)
                count += 1
        print(f"[OK] Da nap {count} khai niem CTDL&GT (NEU - TIHT1101) vao Neo4j.")

        # 4. Nap cac canh tien quyet khoi tao (:REQUIRES)
        query_edge = """
        MATCH (a:Concept {concept_id: $src})
        MATCH (b:Concept {concept_id: $dst})
        MERGE (a)-[:REQUIRES]->(b)
        """
        for src, dst in INITIAL_REQUIRES_EDGES:
            session.run(query_edge, src=src, dst=dst)
        print(
            f"[OK] Da tao {len(INITIAL_REQUIRES_EDGES)} canh tien quyet (:REQUIRES) giua cac khai niem."
        )

    driver.close()


if __name__ == "__main__":
    run_init()