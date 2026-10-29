# Safe review and integration (no commit or push performed)

The implementation checkout was cloned from `https://github.com/yamke2007/AI-Project-Madhya-Pradesh2` at main `496bbf6`. The original workspace's empty Git repository was left alone. All 19 original tracked files remain; the Phase 1 README is additionally preserved under `docs/Phase1/README_original.md` while the root README documents the runnable project. The original inventory, cleaned inventory, scope PDF/Markdown, frequency summary and schema plans are preserved. `.git` is deliberately excluded from the deliverable.

Prefer a separate clean review checkout. Commands below create no commits, pushes or destructive resets:

```powershell
git clone https://github.com/yamke2007/AI-Project-Madhya-Pradesh2.git C:/review/AgriAgent-review
git -C C:/review/AgriAgent-review status --short --branch
git -C C:/review/AgriAgent-review log -5 --oneline
git -C C:/review/AgriAgent-review switch -c codex/phase2-review
```

Extract the ZIP into `C:/review/package` (not into the checkout). Inspect differences first; git diff --no-index returns 1 when differences exist:

```powershell
git diff --no-index -- C:/review/AgriAgent-review C:/review/package/AgriAgent_MadhyaPradesh
```

If the remote has advanced, inspect all collisions rather than overwriting them. Use the package's `evidence/package_inventory.json` to identify files/hashes, and `evidence/phase1_baseline.json` to identify original Phase 1 content. A safe first copy only adds missing paths and prints every existing path for review:

```powershell
$packageRoot = (Resolve-Path 'C:/review/package/AgriAgent_MadhyaPradesh').Path
$reviewRoot = (Resolve-Path 'C:/review/AgriAgent-review').Path
Get-ChildItem -LiteralPath $packageRoot -File -Recurse | ForEach-Object {
    $relativeName = $_.FullName.Substring($packageRoot.Length).TrimStart([char]92, [char]47)
    $reviewFile = Join-Path $reviewRoot $relativeName
    if (Test-Path -LiteralPath $reviewFile) {
        Write-Host "REVIEW EXISTING: $relativeName"
    } else {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reviewFile) | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $reviewFile
    }
}
git -C C:/review/AgriAgent-review status --short
git -C C:/review/AgriAgent-review diff -- README.md
```

This intentionally leaves an existing root README untouched. Review the package README with `git diff --no-index -- C:/review/AgriAgent-review/README.md C:/review/package/AgriAgent_MadhyaPradesh/README.md`, then merge desired edits in an editor. Review other existing collisions the same way. No deletion, mirroring, blanket overwrite, auto-commit or push is needed. Run the README test/evaluation commands in the review checkout after merging. If integrating into a separate working repository, first inspect `git status --short --branch` there and preserve all unrelated edits; use the clean review checkout for comparison.
