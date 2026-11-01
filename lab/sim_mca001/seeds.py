"""Sementes determinísticas, separadas por bloco, cenário, partição e réplica.

A partição ("cal", "ver" ou "val") separa as sementes usadas para escolher parâmetros
das usadas para verificar o desempenho (parecer da Luna sobre a SIM-MCA-001 v0.1).
O espaço é distinto do MASTER_SEED do pré-registro.
"""
import hashlib

import numpy as np

NAMESPACE = "SIM-MCA-001"
PARTITIONS = ("cal", "ver", "val")
# "cal": escolha de parâmetros; "ver": diagnóstico, sem influenciar escolhas; "val": validação
# final com sementes inéditas, usada uma única vez depois de congeladas as regras (auditoria do
# Gemini e parecer da Luna sobre o piloto v2: a partição "ver" do B1 já foi consultada).
EXPLORATORY_PARTITIONS = ("cal", "ver")


def seed_int(*parts) -> int:
    key = "|".join([NAMESPACE, *map(str, parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big")


def rng(block: str, scenario: str, partition: str, replicate: int) -> np.random.Generator:
    if partition not in PARTITIONS:
        raise ValueError(f"partição inválida: {partition!r}")
    return np.random.default_rng(seed_int(block, scenario, partition, replicate))
