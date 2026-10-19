#!/usr/bin/env python3
"""Generate a clean-replacement MySQL location import from rwanda-locations."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path
from typing import Any, Iterator


PACKAGE_VERSION = "1.2.2"
PACKAGE_URL = (
    "https://registry.npmjs.org/rwanda-locations/-/"
    f"rwanda-locations-{PACKAGE_VERSION}.tgz"
)
PACKAGE_SHA256 = "6cc2d3120a87f8274068b23ab5492535f9d9210f82e186cb288b0766014e68b3"
PACKAGE_DATA_PATH = "package/dist/data/locations.json"

EXPECTED_COUNTS = {
    "provinces": 5,
    "districts": 30,
    "sectors": 416,
    "cells": 2148,
    "villages": 14840,
}
EXPECTED_SKIPPED_EMPTY_VILLAGES = 1
EXPECTED_DISTRICTS = {
    "Kigali City": 3,
    "Southern Province": 8,
    "Western Province": 7,
    "Northern Province": 5,
    "Eastern Province": 7,
}
PROVINCE_NAMES = {
    "City Of Kigali": "Kigali City",
    "Southern": "Southern Province",
    "Western": "Western Province",
    "Northern": "Northern Province",
    "Eastern": "Eastern Province",
}
ROMAN_NUMERAL = re.compile(r"\b(?:ii|iii|iv|vi|vii|viii|ix|x)\b", re.IGNORECASE)


def download_package() -> bytes:
    request = urllib.request.Request(
        PACKAGE_URL,
        headers={"User-Agent": "Enatha location SQL generator"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = response.read()

    digest = hashlib.sha256(archive).hexdigest()
    if digest != PACKAGE_SHA256:
        raise ValueError(
            f"Package checksum mismatch: expected {PACKAGE_SHA256}, got {digest}"
        )
    return archive


def read_package_data(archive: bytes) -> dict[str, Any]:
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
        member = package.getmember(PACKAGE_DATA_PATH)
        extracted = package.extractfile(member)
        if extracted is None:
            raise ValueError(f"{PACKAGE_DATA_PATH} is missing from the package")
        return json.load(extracted)


def normalize_name(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{path} name must be a string")
    name = ROMAN_NUMERAL.sub(lambda match: match.group(0).upper(), value.strip())
    if not name:
        raise ValueError(f"{path} name must not be empty")
    if len(name) > 120:
        raise ValueError(f"{path} name exceeds the database limit of 120 characters")
    return name


def hierarchy_rows(data: dict[str, Any]) -> tuple[list[tuple[str, ...]], dict[str, int]]:
    provinces = data.get("provinces")
    if not isinstance(provinces, list):
        raise ValueError("Package data must contain a provinces array")

    rows: list[tuple[str, ...]] = []
    counts = {key: 0 for key in EXPECTED_COUNTS}
    district_counts: dict[str, int] = {}
    seen_paths = {level: set() for level in EXPECTED_COUNTS}
    skipped_empty_villages = 0

    for province_item in provinces:
        source_province = normalize_name(province_item.get("name"), "province")
        if source_province not in PROVINCE_NAMES:
            raise ValueError(f"Unexpected province name: {source_province}")
        province = PROVINCE_NAMES[source_province]
        province_path = (province.casefold(),)
        seen_paths["provinces"].add(province_path)

        districts = province_item.get("districts")
        if not isinstance(districts, list) or not districts:
            raise ValueError(f"{province} has no districts")
        district_counts[province] = len(districts)

        for district_item in districts:
            district = normalize_name(
                district_item.get("name"), f"{province}/district"
            )
            district_path = province_path + (district.casefold(),)
            if district_path in seen_paths["districts"]:
                raise ValueError(f"Duplicate district path: {province}/{district}")
            seen_paths["districts"].add(district_path)

            sectors = district_item.get("sectors")
            if not isinstance(sectors, list) or not sectors:
                raise ValueError(f"{province}/{district} has no sectors")
            for sector_item in sectors:
                sector = normalize_name(
                    sector_item.get("name"), f"{province}/{district}/sector"
                )
                sector_path = district_path + (sector.casefold(),)
                if sector_path in seen_paths["sectors"]:
                    raise ValueError(
                        f"Duplicate sector path: {province}/{district}/{sector}"
                    )
                seen_paths["sectors"].add(sector_path)

                cells = sector_item.get("cells")
                if not isinstance(cells, list) or not cells:
                    raise ValueError(
                        f"{province}/{district}/{sector} has no cells"
                    )
                for cell_item in cells:
                    cell = normalize_name(
                        cell_item.get("name"),
                        f"{province}/{district}/{sector}/cell",
                    )
                    cell_path = sector_path + (cell.casefold(),)
                    if cell_path in seen_paths["cells"]:
                        raise ValueError(
                            "Duplicate cell path: "
                            f"{province}/{district}/{sector}/{cell}"
                        )
                    seen_paths["cells"].add(cell_path)

                    villages = cell_item.get("villages")
                    if not isinstance(villages, list) or not villages:
                        raise ValueError(
                            f"{province}/{district}/{sector}/{cell} has no villages"
                        )
                    for village_item in villages:
                        raw_village = village_item.get("name")
                        if isinstance(raw_village, str) and not raw_village.strip():
                            skipped_empty_villages += 1
                            continue
                        village = normalize_name(
                            raw_village,
                            f"{province}/{district}/{sector}/{cell}/village",
                        )
                        village_path = cell_path + (village.casefold(),)
                        if village_path in seen_paths["villages"]:
                            raise ValueError(
                                "Duplicate village path: "
                                f"{province}/{district}/{sector}/{cell}/{village}"
                            )
                        seen_paths["villages"].add(village_path)
                        rows.append((province, district, sector, cell, village))

    for level, paths in seen_paths.items():
        counts[level] = len(paths)
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"Unexpected hierarchy counts: {counts}")
    if district_counts != EXPECTED_DISTRICTS:
        raise ValueError(f"Unexpected province/district counts: {district_counts}")
    if skipped_empty_villages != EXPECTED_SKIPPED_EMPTY_VILLAGES:
        raise ValueError(
            "Unexpected number of empty village names: "
            f"{skipped_empty_villages}"
        )
    return rows, counts


def sql_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def chunks(items: list[tuple[str, ...]], size: int) -> Iterator[list[tuple[str, ...]]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def render_sql(rows: list[tuple[str, ...]], counts: dict[str, int]) -> str:
    lines = [
        "-- Complete Rwanda administrative hierarchy for Enatha.",
        f"-- Source: rwanda-locations npm package v{PACKAGE_VERSION} (MIT license).",
        f"-- Package: https://www.npmjs.com/package/rwanda-locations/v/{PACKAGE_VERSION}",
        f"-- SHA-256 (npm archive): {PACKAGE_SHA256}",
        "-- Generated by scripts/generate_rwanda_locations_sql.py.",
        "--",
        "-- CLEAN REPLACEMENT: all existing location rows are deleted first.",
        "-- Back up the database before importing this file.",
        "-- Select the Enatha database in phpMyAdmin before importing this file.",
        "-- The five destination tables from database/schema.sql must already exist.",
        "",
        "SET NAMES utf8mb4;",
        "",
        "DROP TEMPORARY TABLE IF EXISTS tmp_rwanda_locations;",
        "CREATE TEMPORARY TABLE tmp_rwanda_locations (",
        "    province VARCHAR(120) NOT NULL,",
        "    district VARCHAR(120) NOT NULL,",
        "    sector VARCHAR(120) NOT NULL,",
        "    cell VARCHAR(120) NOT NULL,",
        "    village VARCHAR(120) NOT NULL,",
        "    UNIQUE KEY uk_tmp_location (province, district, sector, cell, village)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
        "",
    ]

    for batch in chunks(rows, 500):
        lines.append(
            "INSERT INTO tmp_rwanda_locations "
            "(province, district, sector, cell, village) VALUES"
        )
        lines.append(
            ",\n".join(
                "(" + ", ".join(sql_string(value) for value in row) + ")"
                for row in batch
            )
            + ";"
        )
        lines.append("")

    lines.extend(
        [
            "START TRANSACTION;",
            "",
            "-- Delete children before parents to satisfy the hierarchy foreign keys.",
            "DELETE FROM villages;",
            "DELETE FROM cells;",
            "DELETE FROM sectors;",
            "DELETE FROM districts;",
            "DELETE FROM provinces;",
            "",
            "INSERT INTO provinces (name, status)",
            "SELECT DISTINCT province, 'active' FROM tmp_rwanda_locations;",
            "",
            "INSERT INTO districts (province_id, name, status)",
            "SELECT DISTINCT p.id, t.district, 'active'",
            "FROM tmp_rwanda_locations t",
            "JOIN provinces p ON p.name = t.province;",
            "",
            "INSERT INTO sectors (district_id, name, status)",
            "SELECT DISTINCT d.id, t.sector, 'active'",
            "FROM tmp_rwanda_locations t",
            "JOIN provinces p ON p.name = t.province",
            "JOIN districts d ON d.province_id = p.id AND d.name = t.district;",
            "",
            "INSERT INTO cells (sector_id, name, status)",
            "SELECT DISTINCT s.id, t.cell, 'active'",
            "FROM tmp_rwanda_locations t",
            "JOIN provinces p ON p.name = t.province",
            "JOIN districts d ON d.province_id = p.id AND d.name = t.district",
            "JOIN sectors s ON s.district_id = d.id AND s.name = t.sector;",
            "",
            "INSERT INTO villages (cell_id, name, status)",
            "SELECT DISTINCT c.id, t.village, 'active'",
            "FROM tmp_rwanda_locations t",
            "JOIN provinces p ON p.name = t.province",
            "JOIN districts d ON d.province_id = p.id AND d.name = t.district",
            "JOIN sectors s ON s.district_id = d.id AND s.name = t.sector",
            "JOIN cells c ON c.sector_id = s.id AND c.name = t.cell;",
            "",
            "COMMIT;",
            "",
            "-- matched_rows should equal source_rows (14,840).",
            "SELECT COUNT(*) AS source_rows, COUNT(v.id) AS matched_rows",
            "FROM tmp_rwanda_locations t",
            "LEFT JOIN provinces p ON p.name = t.province",
            "LEFT JOIN districts d ON d.province_id = p.id AND d.name = t.district",
            "LEFT JOIN sectors s ON s.district_id = d.id AND s.name = t.sector",
            "LEFT JOIN cells c ON c.sector_id = s.id AND c.name = t.cell",
            "LEFT JOIN villages v ON v.cell_id = c.id AND v.name = t.village;",
            "",
            "-- Destination totals must equal the validated source counts below.",
            "SELECT 'provinces' AS level_name, COUNT(*) AS row_count FROM provinces",
            "UNION ALL SELECT 'districts', COUNT(*) FROM districts",
            "UNION ALL SELECT 'sectors', COUNT(*) FROM sectors",
            "UNION ALL SELECT 'cells', COUNT(*) FROM cells",
            "UNION ALL SELECT 'villages', COUNT(*) FROM villages;",
            "",
            "DROP TEMPORARY TABLE tmp_rwanda_locations;",
            "",
            "-- Validated source counts:",
        ]
    )
    lines.extend(f"-- {level}: {count}" for level, count in counts.items())
    lines.append(
        "-- Skipped one package record with an empty village name at "
        "Eastern Province/Ngoma/Gashanda/Cyerwa."
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    default_output = (
        project_root
        / "database"
        / "locations"
        / f"replace_rwanda_locations_{PACKAGE_VERSION.replace('.', '_')}.sql"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"SQL output path (default: {default_output})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    archive = download_package()
    data = read_package_data(archive)
    rows, counts = hierarchy_rows(data)
    sql = render_sql(rows, counts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(sql, encoding="utf-8", newline="\n")
    print(f"Wrote {args.output}")
    print(", ".join(f"{level}={count}" for level, count in counts.items()))


if __name__ == "__main__":
    main()
