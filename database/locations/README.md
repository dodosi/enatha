# Rwanda administrative locations

## Complete national hierarchy (clean replacement)

`replace_rwanda_locations_1_2_2.sql` contains the complete hierarchy supplied by
version 1.2.2 of the MIT-licensed
[`rwanda-locations`](https://www.npmjs.com/package/rwanda-locations) package.

The import:

- deletes every existing village, cell, sector, district, and province;
- inserts a brand-new national hierarchy without `Unspecified` placeholders;
- normalizes province names to the names used by Enatha;
- trims whitespace and normalizes Roman numerals such as `Ii` to `II`;
- skips the package's single blank village record.

### Import with phpMyAdmin

1. Back up the database.
2. Select the Enatha database in the phpMyAdmin left panel.
3. Open **Import** and choose `replace_rwanda_locations_1_2_2.sql`.
4. Click **Go**.
5. Confirm that the final result shows `source_rows = matched_rows = 14840`.
6. Confirm the totals are exactly 5 provinces, 30 districts, 416 sectors,
   2,148 cells, and 14,840 villages.

To regenerate the SQL from the pinned, checksum-verified npm package:

```powershell
python scripts/generate_rwanda_locations_sql.py
```

This community package is not an official Government of Rwanda source. Validate
locations used for study reporting against current official administrative data.

## Study district locations (Gasabo / Bugesera / Gakenke)

Full cascade: **Province → District → Sector → Cell → Village**

## phpMyAdmin (no CLI)

1. In the **left panel**, click **your real database**  
   (example: `u924861691_enatha` — **not** `enatha_survey` if that name is denied)
2. Open **Import** (or **SQL**)
3. Choose / paste `reload_study_districts.sql`
4. Click **Go**

Do **not** keep a line like `USE enatha_survey;` on shared hosting — your user only has access to your own DB name.

### Verify in SQL tab

```sql
SELECT p.name AS province, d.name AS district, s.name AS sector,
       c.name AS cell, v.name AS village
FROM provinces p
JOIN districts d ON d.province_id = p.id
JOIN sectors s ON s.district_id = d.id
JOIN cells c ON c.sector_id = s.id
JOIN villages v ON v.cell_id = c.id
ORDER BY province, district, sector, cell, village;
```

You should see sectors, cells, and villages — not only districts.

## In the survey

Select in order: Province → District → Sector → Cell → Village.  
Each step unlocks the next. Hard-refresh (Ctrl+F5) after JS updates.

## Note

Where the facility list had no village, the CSV uses `Unspecified`. Replace with the official full hierarchy when available.
