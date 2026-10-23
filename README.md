# Lutheran Prayer Book — Daily Office

The Lutheran Daily Office online, following the orders of the *Lutheran Service Book*:
Matins, Vespers, Morning Prayer, Evening Prayer, Compline, the Responsive Prayers, the Litany,
and Daily Prayer for Individuals and Families. The day's lectionary readings are loaded
automatically from the RSV-UE. Part of [prayernetwork.christ.software](https://prayernetwork.christ.software).

Built the same way as the ACNA prayer book (`acna.jeffrey.land`): React + Vite, with the
liturgy compiled to JSON by the scripts in `scratch/`.

## Layout

- `app/` — the site (`npm --prefix app run dev`, port 5184; deployed by Netlify from `app/dist`)
  - `src/data/content.json` — every office as typed blocks (generated)
  - `src/data/lsbLectionary.json` — LSB Daily Lectionary (generated)
  - `src/data/psalter30Day.json` — psalms by day of the month (until the LSB psalm table is added)
  - `public/bibles/rsvue-bible.json` — RSV-UE text, fetched lazily for readings
- `scratch/build_content.py` — defines the offices; pulls canticles and fixed psalms from `bibles/rsvue-bible.json`
- `scratch/build_lectionary.py` — extracts the Daily Lectionary (OT, NT, Additional Reading) from the lectionary PDF (needs `pymupdf`)

## Regenerating data

```bash
python3 scratch/build_content.py
python3 scratch/build_lectionary.py resources/lutheran-main/LSB-Daily-Lectionary.pdf
```
