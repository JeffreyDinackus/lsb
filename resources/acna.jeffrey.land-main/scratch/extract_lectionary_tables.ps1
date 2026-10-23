param(
    [string]$DocxXmlPath = "$PSScriptRoot\..\..\..\..\..\AppData\Local\Temp\claude\C--Users-reformed-Desktop-git-acna-jeffrey-land\39b2ed23-6656-4e81-930e-323c07ceeedc\scratchpad\lect_unpacked\word\document.xml",
    [string]$OutPath = "$PSScriptRoot\lectionary_tables.json"
)

# Read as proper UTF-8 so special chars (dagger, em-dash, double-dagger) decode correctly
$text = [System.IO.File]::ReadAllText($DocxXmlPath, [System.Text.Encoding]::UTF8)
[xml]$xml = $text
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("w", "http://schemas.openxmlformats.org/wordprocessingml/2006/main")

function Get-Text($node) {
    $ts = $node.SelectNodes(".//w:t", $ns)
    ($ts | ForEach-Object { $_.InnerText }) -join ""
}

$tbls = $xml.SelectNodes("//w:tbl", $ns)
$allTables = @()
for ($ti = 0; $ti -lt $tbls.Count; $ti++) {
    $t = $tbls[$ti]
    $rows = $t.SelectNodes(".//w:tr", $ns)
    $rowsData = @()
    foreach ($r in $rows) {
        $cells = $r.SelectNodes(".//w:tc", $ns)
        $cellTexts = @()
        foreach ($cell in $cells) {
            $cellTexts += (Get-Text $cell)
        }
        $rowsData += , @($cellTexts)
    }
    $allTables += , @{ index = $ti; rows = $rowsData }
}
$json = $allTables | ConvertTo-Json -Depth 6 -Compress
[System.IO.File]::WriteAllText($OutPath, $json, [System.Text.Encoding]::UTF8)
Write-Output "wrote $($allTables.Count) tables to $OutPath"
