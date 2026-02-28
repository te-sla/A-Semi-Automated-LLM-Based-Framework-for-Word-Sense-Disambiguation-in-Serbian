# Reorganize output/ into output/round_X/Model/ structure using git mv
# Files without a round indicator are assumed to be Round I
# Files without a clear round/model go to misc/

Set-Location "e:\Github\A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian"

$base = "output"

# --- Create directory structure ---
$dirs = @(
    "$base/round_I/ChatGPT",
    "$base/round_I/Gemini",
    "$base/round_I/Llama",
    "$base/round_I/SimpleWSD",
    "$base/round_I/SimpleWSD_Tesla",
    "$base/round_I/GPT-5",
    "$base/round_II/GPT-5",
    "$base/round_III/GPT-5",
    "$base/round_III/SimpleWSD",
    "$base/round_III/SimpleWSD_Tesla",
    "$base/misc"
)

foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

# --- Helper function ---
function Move-Git {
    param([string]$src, [string]$dst)
    if (Test-Path $src) {
        git mv $src $dst 2>&1 | Out-Null
        Write-Host "  $src -> $dst"
    } else {
        Write-Host "  SKIP (not found): $src" -ForegroundColor Yellow
    }
}

# ========== ROUND I / ChatGPT ==========
Write-Host "`n=== Round I / ChatGPT ===" -ForegroundColor Cyan

# Chat test outputs
Move-Git "$base/Chat_test_out.tsv" "$base/round_I/ChatGPT/"
Move-Git "$base/Chat_test_out_incept.tsv" "$base/round_I/ChatGPT/"

# filtered_first_origin ChatGPT-4-1 (no round = Round I)
Get-ChildItem "$base/filtered_first_origin_*.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/ChatGPT/"
}

# LexiSense ChatGPT test files (no round = Round I)
Move-Git "$base/LexiSense_test_1_10_ChatGPT.tsv" "$base/round_I/ChatGPT/"
Move-Git "$base/LexiSense_Inception_test_1_10_ChatGPT.tsv" "$base/round_I/ChatGPT/"

Get-ChildItem "$base/LexiSense_Inception_test_*_ChatGPT-*.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/ChatGPT/"
}

# ========== ROUND I / Gemini ==========
Write-Host "`n=== Round I / Gemini ===" -ForegroundColor Cyan

Get-ChildItem "$base/gemini_*.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/Gemini/"
}

# ========== ROUND I / Llama ==========
Write-Host "`n=== Round I / Llama ===" -ForegroundColor Cyan

Get-ChildItem "$base/llama_*.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/Llama/"
}

# ========== ROUND I / SimpleWSD (round1) ==========
Write-Host "`n=== Round I / SimpleWSD ===" -ForegroundColor Cyan

Get-ChildItem "$base/LexiSense_*_simple_wsd_round1.*" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/SimpleWSD/"
}
Get-ChildItem "$base/LexiSense_Inception_*_simple_wsd_round1.*" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/SimpleWSD/"
}

# ========== ROUND I / SimpleWSD_Tesla (round1) ==========
Write-Host "`n=== Round I / SimpleWSD_Tesla ===" -ForegroundColor Cyan

Get-ChildItem "$base/LexiSense_*_tesla_wsd_round1.*" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/SimpleWSD_Tesla/"
}
Get-ChildItem "$base/LexiSense_Inception_*_tesla_wsd_round1.*" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/SimpleWSD_Tesla/"
}

# ========== ROUND I / GPT-5 (test files, no round = Round I) ==========
Write-Host "`n=== Round I / GPT-5 ===" -ForegroundColor Cyan

Get-ChildItem "$base/LexiSense_*_gpt-5_test.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/GPT-5/"
}
Get-ChildItem "$base/LexiSense_Inception_*_gpt-5_test.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_I/GPT-5/"
}

# ========== ROUND II / GPT-5 ==========
Write-Host "`n=== Round II / GPT-5 ===" -ForegroundColor Cyan

Get-ChildItem "$base/LexiSense_*_IIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_II/GPT-5/"
}
Get-ChildItem "$base/LexiSense_Inception_*_IIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_II/GPT-5/"
}

# ========== ROUND III / GPT-5 ==========
Write-Host "`n=== Round III / GPT-5 ===" -ForegroundColor Cyan

Get-ChildItem "$base/LexiSense_*_gpt-5_IIIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_III/GPT-5/"
}
Get-ChildItem "$base/LexiSense_Inception_*_gpt-5_IIIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_III/GPT-5/"
}

# ========== ROUND III / SimpleWSD ==========
Write-Host "`n=== Round III / SimpleWSD ===" -ForegroundColor Cyan

Get-ChildItem "$base/LexiSense_*_simple_wsd_IIIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_III/SimpleWSD/"
}
Get-ChildItem "$base/LexiSense_Inception_*_simple_wsd_IIIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_III/SimpleWSD/"
}

# ========== ROUND III / SimpleWSD_Tesla ==========
Write-Host "`n=== Round III / SimpleWSD_Tesla ===" -ForegroundColor Cyan

Get-ChildItem "$base/LexiSense_*_simple_wsd_tesla_IIIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_III/SimpleWSD_Tesla/"
}
Get-ChildItem "$base/LexiSense_Inception_*_simple_wsd_tesla_IIIround.tsv" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Git $_.FullName "$base/round_III/SimpleWSD_Tesla/"
}

# ========== MISC (no clear round/model) ==========
Write-Host "`n=== Misc ===" -ForegroundColor Cyan

Move-Git "$base/LexiSense.tsv" "$base/misc/"
Move-Git "$base/LexiSense_Debug.tsv" "$base/misc/"
Move-Git "$base/ai_generated_senses.jsonl" "$base/misc/"
Move-Git "$base/new_senses_df.xlsx" "$base/misc/"
Move-Git "$base/updated_filtered_sentences_with_senses.tsv" "$base/misc/"
Move-Git "$base/updated_senses_df.xlsx" "$base/misc/"

# prompt_examples folder
if (Test-Path "$base/prompt_examples") {
    git mv "$base/prompt_examples" "$base/misc/prompt_examples" 2>&1 | Out-Null
    Write-Host "  $base/prompt_examples/ -> $base/misc/prompt_examples/"
}

Write-Host "`n=== Done! ===" -ForegroundColor Green

# Show final structure
Write-Host "`nFinal structure:" -ForegroundColor Cyan
Get-ChildItem "$base" -Directory | ForEach-Object {
    Write-Host "`n  $($_.Name)/"
    Get-ChildItem $_.FullName -Directory | ForEach-Object {
        $count = (Get-ChildItem $_.FullName -File -Recurse).Count
        Write-Host "    $($_.Name)/ ($count files)"
    }
    $rootFiles = (Get-ChildItem $_.FullName -File).Count
    if ($rootFiles -gt 0) {
        Write-Host "    ($rootFiles loose files)"
    }
}
