# Parses scratch/lectionary_tables.json (raw docx table dump) into a clean
# app/src/data/dailyOfficeLectionary.json used by the app at runtime.
#
# Design decisions (per user instructions):
# - Psalms come from the 30-day Traditional Psalm Cycle (table 0), keyed by day-of-month,
#   same every month/year. The 60-day alternate psalter columns embedded in the lesson
#   tables are intentionally ignored.
# - Each date has two independent two-lesson tracks: "yearI" (from the "(I)"/Morning
#   Prayer heading tables) and "yearII" (from the "(II)"/Evening Prayer heading tables).
#   Per user: calendar year even => yearI, odd => yearII. Lesson 1 -> Morning Prayer,
#   Lesson 2 -> Evening Prayer (regardless of which track supplied them).
# - The dagger (†) "optional abbreviation" verse-range annotations are dropped; we always
#   read the full chapter/reference given as the primary citation.
# - Movable feasts (Ash Wednesday, Maundy Thursday, Good Friday, Holy Saturday, Easter Day,
#   Ascension, Pentecost) are parsed separately and are NOT split by year (same reading both years).

param(
    [string]$InPath = "$PSScriptRoot\lectionary_tables.json",
    [string]$OutPath = "$PSScriptRoot\..\app\src\data\dailyOfficeLectionary.json"
)

$raw = Get-Content -Raw -Encoding UTF8 $InPath | ConvertFrom-Json
$tables = @($raw)

# ---- Book abbreviation map: pattern fragment (without numeral prefix) -> canonical book name ----
# Order doesn't matter for correctness (word-boundaried), but longer/more specific first is tidier.
$bookMap = [ordered]@{
    'Gen'              = 'Genesis'
    'Exod'             = 'Exodus'
    'Lev'              = 'Leviticus'
    'Num'              = 'Numbers'
    'Deut'             = 'Deuteronomy'
    'Josh'             = 'Joshua'
    'Judg'             = 'Judges'
    'Ruth'             = 'Ruth'
    'Sam'              = 'Samuel'          # numeral-prefixed: 1 Sam / 2 Sam
    'Kings'            = 'Kings'           # numeral-prefixed
    'Chron'            = 'Chronicles'      # numeral-prefixed
    'Ezra'             = 'Ezra'
    'Neh'              = 'Nehemiah'
    'Esth'             = 'Esther'
    'Job'              = 'Job'
    'Prov'             = 'Proverbs'
    'Eccl'             = 'Ecclesiastes'
    'Song of Songs'    = 'Song Of Songs'
    'Isa'              = 'Isaiah'
    'Jer'              = 'Jeremiah'
    'Lam'              = 'Lamentations'
    'Ezek'             = 'Ezekiel'
    'Dan'              = 'Daniel'
    'Hos'              = 'Hosea'
    'Joel'             = 'Joel'
    'Amos'             = 'Amos'
    'Obadiah'          = 'Obadiah'
    'Obad'             = 'Obadiah'
    'Jonah'            = 'Jonah'
    'Mic'              = 'Micah'
    'Nahum'            = 'Nahum'
    'Hab'              = 'Habakkuk'
    'Zeph'             = 'Zephaniah'
    'Hag'              = 'Haggai'
    'Zech'             = 'Zechariah'
    'Mal'              = 'Malachi'
    'Matt'             = 'Matthew'
    'Mark'             = 'Mark'
    'Luke'             = 'Luke'
    'John'             = 'John'            # numeral-prefixed for epistles: 1/2/3 John
    'Acts'             = 'Acts'
    'Rom'              = 'Romans'
    'Cor'              = 'Corinthians'     # numeral-prefixed
    'Gal'              = 'Galatians'
    'Eph'              = 'Ephesians'
    'Phil'             = 'Philippians'
    'Col'              = 'Colossians'
    'Thess'            = 'Thessalonians'   # numeral-prefixed
    'Tim'              = 'Timothy'         # numeral-prefixed
    'Titus'            = 'Titus'
    'Philem'           = 'Philemon'
    'Philemon'         = 'Philemon'
    'Heb'              = 'Hebrews'
    'Jas'              = 'James'
    'James'            = 'James'
    'Pet'              = 'Peter'           # numeral-prefixed
    'Jude'             = 'Jude'
    'Rev'              = 'Revelation'
    'Tobit'            = 'Tobit'
    'Judith'           = 'Judith'
    'Wisdom'           = 'Wisdom Of Solomon'
    'Ecclesiasticus'   = 'Sirach'
    'Baruch'           = 'Baruch'
    'Susanna'          = 'Susanna'
    'Macc'             = 'Maccabees'       # numeral-prefixed
}

# Books that take a leading numeral (1/2/3/4) -- matched WITHOUT the numeral here;
# the numeral is resolved separately by Parse-LessonRow to avoid stealing a digit
# that actually belongs to the *previous* lesson's chapter number (e.g. "Gen 1 John..."
# is Genesis chapter 1 + the Gospel of John, not Genesis + "1 John").
$numeralBooks = @('Sam','Kings','Chron','John','Cor','Thess','Tim','Pet','Macc')

# Build one big alternation regex of BARE roots only, longest keys first.
$sortedKeys = $bookMap.Keys | Sort-Object { $_.Length } -Descending
$alternatives = foreach ($k in $sortedKeys) { [regex]::Escape($k) }
$bookPattern = '(?<!\w)(' + ($alternatives -join '|') + ')(?!\w)'
$bookRegex = New-Object System.Text.RegularExpressions.Regex($bookPattern)

function Get-DateColumn($dataRows) {
    $maxCols = ($dataRows | ForEach-Object { $_.Count } | Measure-Object -Maximum).Maximum
    $bestCol = -1; $bestScore = -1
    for ($c = 0; $c -lt $maxCols; $c++) {
        $score = 0
        $prevDay = 0
        foreach ($row in $dataRows) {
            if ($c -ge $row.Count) { continue }
            $val = $row[$c]
            if ($val -match '^\s*(\d{1,2})\b') {
                $day = [int]$matches[1]
                if ($day -ge 1 -and $day -le 31) {
                    if ($day -ge $prevDay) { $score++ }
                    $prevDay = $day
                }
            }
        }
        if ($score -gt $bestScore) { $bestScore = $score; $bestCol = $c }
    }
    return $bestCol
}

function Strip-DaggerClause($s) {
    # A dagger clause is an "optional shorter abbreviation" of the same chapter
    # (e.g. "† 1-9,16-18,21-40") -- we always keep the full-chapter reading, so remove
    # just that clause. It is NOT always the last thing before the next book: a split-cell
    # numeral prefix for the next book (e.g. the "1" in "...† 1-9,16-18,21-40 1 Cor 8")
    # can follow it, so we must excise the clause in place rather than truncate at the dagger.
    # (U+2020 DAGGER via code point -- see the dash note above about literal-char corruption)
    $dagger = [char]0x2020
    $clausePattern = "$dagger\s*\d+(?:-\d+)?(?:\s*,\s*\d+(?:-\d+)?)*"
    return (($s -replace $clausePattern, ' ') -replace '\s+', ' ').Trim()
}

function Clean-Citation($s) {
    # Keep only a single leading well-formed citation (chapter[:verse][-chapter[:verse]|-end][&chapter]);
    # this strips trailing junk such as a leftover 60-day-psalter number that has nothing
    # (no 3rd book match) to bound it on the right.
    # Use Unicode code points, not literal dash chars: PowerShell 5.1 reads .ps1 files without a
    # BOM using the system codepage, which silently mangles literal en/em-dash characters here.
    $s = ($s -replace "[$([char]0x2013)$([char]0x2014)]", '-').Trim()
    $s = $s.TrimStart(':')  # source has a couple of "Luke:23:26-49" typos (colon instead of space)
    $s = $s.Trim()
    if ($s -match '^(\d+(?::\d+)?(?:-(?:end|\d+(?::\d+)?))?(?:\s*&\s*\d+)?)') {
        return $matches[1].Trim()
    }
    return $s
}

# Commemoration-name cells that happen to collide with a book name/abbreviation.
# Compound labels (contain punctuation/extra words) are always safe to drop outright.
$compoundCommemorationDenylist = @('Pet. & Paul', 'James Jer.', 'Sim. & Jude', 'Nat. Bap.')
# Single-word labels are only dropped when NOT immediately preceded by a bare numeral cell
# (which would mean they're really a split "1/2/3 <Book>" reference, e.g. "2","John").
# NOTE: "Jude" is never used bare as a commemoration in this table (only inside the compound
# "Sim. & Jude", handled above) -- a bare "Jude" cell is always the one-chapter Epistle of Jude.
$ambiguousSingleWordLabels = @('James', 'John', 'Luke')

function Parse-LessonRow($row, $dateColIdx) {
    $dateCell = $row[$dateColIdx]
    if ($dateCell -notmatch '^\s*(\d{1,2})\b') { return $null }
    $day = [int]$matches[1]

    $rawCells = @()
    for ($i = 0; $i -lt $row.Count; $i++) {
        if ($i -eq $dateColIdx) { continue }
        $rawCells += $row[$i]
    }
    $refCells = @()
    for ($j = 0; $j -lt $rawCells.Count; $j++) {
        $trimmed = $rawCells[$j].Trim()
        if ($compoundCommemorationDenylist -contains $trimmed) { continue }
        if ($ambiguousSingleWordLabels -contains $trimmed) {
            $prevVal = if ($j -gt 0) { $rawCells[$j - 1].Trim() } else { '' }
            if ($prevVal -notmatch '^[1-4]$') { continue }
        }
        $refCells += $rawCells[$j]
    }
    $joined = ($refCells -join ' ')
    $joined = ($joined -replace '\s+', ' ').Trim()

    $matchesFound = $bookRegex.Matches($joined)
    if ($matchesFound.Count -lt 2) {
        return [pscustomobject]@{ day = $day; ok = $false; raw = $joined; lesson1 = $null; lesson2 = $null }
    }

    $m0 = $matchesFound[0]
    $m1 = $matchesFound[1]
    $root1 = $m0.Value
    $root2 = $m1.Value

    # Resolve book1's own leading numeral (text before m0 in the whole joined string)
    $before1 = $joined.Substring(0, $m0.Index)
    $num1 = $null
    if (($numeralBooks -contains $root1) -and ($before1.Trim() -match '([1-4])\s*$')) {
        $num1 = $matches[1]
    }

    # Text strictly between book1 and book2 -- candidate ref1 text, possibly with book2's numeral prefix stuck to its tail
    $between = $joined.Substring($m0.Index + $m0.Length, $m1.Index - ($m0.Index + $m0.Length))
    $between = Strip-DaggerClause $between
    $num2 = $null
    $ref1Text = $between
    if (($numeralBooks -contains $root2) -and ($between -match '(?:^|\s)([1-4])$')) {
        $candidate = $matches[1]
        $withoutCandidate = $between.Substring(0, $between.Length - $candidate.Length).Trim()
        if ($withoutCandidate -ne '') {
            # book1 already has its own chapter content; the trailing digit belongs to book2's numeral prefix
            $num2 = $candidate
            $ref1Text = $withoutCandidate
        }
        # else: the lone digit is book1's only chapter number -- leave it with book1, book2 gets no numeral
    }
    $ref1Text = Clean-Citation $ref1Text

    $endIdx = if ($matchesFound.Count -gt 2) { $matchesFound[2].Index } else { $joined.Length }
    $ref2Raw = $joined.Substring($m1.Index + $m1.Length, $endIdx - ($m1.Index + $m1.Length))
    $ref2Raw = Strip-DaggerClause $ref2Raw
    $ref2Text = Clean-Citation $ref2Raw

    $canon1 = $bookMap[$root1]
    $canon2 = $bookMap[$root2]
    $book1 = if ($num1) { "$num1 $canon1" } else { $canon1 }
    $book2 = if ($num2) { "$num2 $canon2" } else { $canon2 }

    $lesson1 = if ($canon1) { "$book1 $ref1Text".Trim() } else { $null }
    $lesson2 = if ($canon2) { "$book2 $ref2Text".Trim() } else { $null }
    # ref text may legitimately be empty for single-chapter books cited by name alone
    # (Philemon, Jude, 2/3 John, Obadiah, Susanna): that means "read the whole book".
    $ref1Valid = ($ref1Text -eq '' -or $ref1Text -match '^\d')
    $ref2Valid = ($ref2Text -eq '' -or $ref2Text -match '^\d')
    $ok = ($canon1 -and $canon2 -and $ref1Valid -and $ref2Valid)

    [pscustomobject]@{
        day     = $day
        ok      = $ok
        raw     = $joined
        lesson1 = $lesson1
        lesson2 = $lesson2
    }
}

$months = @('01','02','03','04','05','06','07','08','09','10','11','12')
$monthNames = @('January','February','March','April','May','June','July','August','September','October','November','December')
$monthIIdx = @(1,3,7,12,14,16,18,20,22,24,26,28)
$monthIIIdx = @(2,6,8,13,15,17,19,21,23,25,27,29)

$byDate = [ordered]@{}
$failures = @()

for ($mi = 0; $mi -lt 12; $mi++) {
    $monthNum = $months[$mi]

    foreach ($track in @('yearI', 'yearII')) {
        $tblIdx = if ($track -eq 'yearI') { $monthIIdx[$mi] } else { $monthIIIdx[$mi] }
        $table = $tables | Where-Object { $_.index -eq $tblIdx } | Select-Object -First 1
        $rows = @($table.rows)

        # data rows = rows that contain a valid day-like cell somewhere
        $dataRows = @($rows | Where-Object {
            $r = $_
            ($r | Where-Object { $_ -match '^\s*\d{1,2}\b' }).Count -gt 0
        })
        $dateColIdx = Get-DateColumn $dataRows

        foreach ($row in $dataRows) {
            $parsed = Parse-LessonRow $row $dateColIdx
            if (-not $parsed) { continue }
            $dateKey = "$monthNum-{0:D2}" -f $parsed.day
            if (-not $byDate.Contains($dateKey)) {
                $byDate[$dateKey] = [ordered]@{}
            }
            if ($parsed.ok) {
                $byDate[$dateKey][$track] = [ordered]@{ lesson1 = $parsed.lesson1; lesson2 = $parsed.lesson2 }
            } else {
                $failures += [pscustomobject]@{ date = $dateKey; track = $track; tblIdx = $tblIdx; raw = $parsed.raw }
            }
        }
    }
}

Write-Output "Parsed $($byDate.Count) calendar dates. Failures: $($failures.Count)"
if ($failures.Count -gt 0) {
    $failOut = "$PSScriptRoot\lectionary_failures.json"
    $failures | ConvertTo-Json -Depth 4 | Set-Content -Path $failOut -Encoding utf8
    Write-Output "Wrote failure detail to $failOut"
}

# ---- Psalm 30-day cycle (table 0) ----
$psalmTable = $tables | Where-Object { $_.index -eq 0 } | Select-Object -First 1
$psalms30 = [ordered]@{}
foreach ($row in $psalmTable.rows) {
    if ($row.Count -lt 3) { continue }
    if ($row[0] -notmatch '^\d{1,2}$') { continue }
    $d = [int]$row[0]
    $psalms30["$d"] = [ordered]@{ morning = $row[1]; evening = $row[2] }
}
# Day 31: not in the traditional table; BCP says use Songs of Ascents (120-134) split across offices
$psalms30["31"] = [ordered]@{ morning = "120, 121, 122, 123, 124, 125, 126"; evening = "127, 128, 129, 130, 131, 132, 133, 134" }

# ---- Movable feasts ----
function Cell($row, $i) { if ($i -lt $row.Count) { return $row[$i] } else { return '' } }

function Canonicalize-SingleRef($s) {
    # These movable-feast cells are already a single clean "Book chapter[:verse]" citation
    # (no dagger clauses, no second lesson to disambiguate against) -- just swap the
    # abbreviation for the canonical book name used throughout byDate.
    $s = $s.Trim()
    $m = $bookRegex.Match($s)
    if (-not $m.Success) { return $s }
    $root = $m.Value
    $before = $s.Substring(0, $m.Index).Trim()
    $num = $null
    if (($numeralBooks -contains $root) -and ($before -match '([1-4])$')) { $num = $matches[1] }
    $canon = $bookMap[$root]
    if (-not $canon) { return $s }
    $book = if ($num) { "$num $canon" } else { $canon }
    $rest = Clean-Citation ($s.Substring($m.Index + $m.Length))
    return "$book $rest".Trim()
}

$ashTbl = ($tables | Where-Object { $_.index -eq 4 }).rows
$ashRow = $ashTbl[1]
$movable = [ordered]@{
    ashWednesday = [ordered]@{
        morningPsalm = (Cell $ashRow 0); morningLesson1 = (Canonicalize-SingleRef (Cell $ashRow 1)); morningLesson2 = (Canonicalize-SingleRef (Cell $ashRow 2))
        eveningPsalm = (Cell $ashRow 4); eveningLesson1 = (Canonicalize-SingleRef (Cell $ashRow 5)); eveningLesson2 = (Canonicalize-SingleRef (Cell $ashRow 6))
    }
}

$holyWeekTbl = ($tables | Where-Object { $_.index -eq 9 }).rows
# rows: label, data, label, data, ... (label rows carry names split across two lines: "MAUNDY"/"THURSDAY" etc.)
$hwEntries = @{}
$labelMap = @{ 'MAUNDY' = 'maundyThursday'; 'GOOD' = 'goodFriday'; 'HOLY' = 'holySaturday'; 'EASTER' = 'easterDay' }
for ($i = 0; $i -lt $holyWeekTbl.Count; $i++) {
    $row = $holyWeekTbl[$i]
    $label = (Cell $row 0).Trim()
    if ($labelMap.ContainsKey($label)) {
        $key = $labelMap[$label]
        $hwEntries[$key] = [ordered]@{
            morningPsalm = (Cell $row 1); morningLesson1 = (Canonicalize-SingleRef (Cell $row 2)); morningLesson2 = (Canonicalize-SingleRef (Cell $row 3))
            eveningPsalm = (Cell $row 5); eveningLesson1 = (Canonicalize-SingleRef (Cell $row 6)); eveningLesson2 = (Canonicalize-SingleRef (Cell $row 7))
        }
    }
}
foreach ($k in $hwEntries.Keys) { $movable[$k] = $hwEntries[$k] }

$ascTbl = ($tables | Where-Object { $_.index -eq 10 }).rows
$ascRow = $ascTbl[1]
$movable['ascensionDay'] = [ordered]@{
    morningPsalm = (Cell $ascRow 1); morningLesson1 = (Canonicalize-SingleRef (Cell $ascRow 2)); morningLesson2 = (Canonicalize-SingleRef (Cell $ascRow 3))
    eveningPsalm = (Cell $ascRow 5); eveningLesson1 = (Canonicalize-SingleRef (Cell $ascRow 6)); eveningLesson2 = (Canonicalize-SingleRef (Cell $ascRow 7))
}

$penTbl = ($tables | Where-Object { $_.index -eq 11 }).rows
$penRow = $penTbl[1]
$movable['pentecost'] = [ordered]@{
    morningPsalm = (Cell $penRow 1); morningLesson1 = (Canonicalize-SingleRef (Cell $penRow 2)); morningLesson2 = (Canonicalize-SingleRef (Cell $penRow 3))
    eveningPsalm = (Cell $penRow 5); eveningLesson1 = (Canonicalize-SingleRef (Cell $penRow 6)); eveningLesson2 = (Canonicalize-SingleRef (Cell $penRow 7))
}

$final = [ordered]@{
    psalms30Day = $psalms30
    byDate      = $byDate
    movable     = $movable
}

$outJson = $final | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($OutPath, $outJson, [System.Text.Encoding]::UTF8)
Write-Output "Wrote $OutPath"
