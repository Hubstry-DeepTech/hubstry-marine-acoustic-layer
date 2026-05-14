#!/usr/bin/env python3
# fix_toml.py - Cria pyproject.toml SEM BOM usando escrita bin?ria ASCII
content = b"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "hmal"
version = "0.1.0-alpha"
description = "HMAL: protocolo acustico harmonico"
requires-python = ">=3.10"
dependencies = ["numpy>=1.24", "scipy>=1.10", "ply>=3.11"]

[project.optional-dependencies]
dev = ["pytest>=7.4", "black", "mypy"]
"""
with open("pyproject.toml", "wb") as f:
    f.write(content)
print("OK: pyproject.toml criado sem BOM")
