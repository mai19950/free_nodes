Param([switch]$commit)

# $modules = @("abshare", "mksshare", "tolinkshare2")
$modules_dir = "./submodules"
$updated_submodules=@()

foreach ($sub in (Get-ChildItem $modules_dir -Directory)) {
  if (-not (test-path "$($sub.fullname)/.git")) {
    continue
  }
  Push-location $sub.fullname
  write-host "check $($sub.name)" -ForegroundColor "Cyan"
  # 获取本地和远程的commit ID
  git fetch
  $localCommit = git rev-parse HEAD
  $remoteCommit = git rev-parse origin/main
  # 比较两个commit
  if ($localCommit -ne $remoteCommit) {
    git fetch origin
    git reset --hard origin/main
    Write-Host "$($sub.Name) has updates." -ForegroundColor "Green"
    $updated_submodules += $sub.name
  }
  pop-location
}

if ($commit -and ($updated_submodules.count -gt 0)) {
  foreach ($sub in $updated_submodules) {
    Write-Host "python main.py $sub" -ForegroundColor "yellow"
    python main.py $sub
  }
  git add .
  # 设置时区
  $timeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById("China Standard Time")
  # 获取当前时间并转换为指定时区
  $currentDateTime = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $timeZone)
  # 格式化输出
  $c = $currentDateTime.ToString('yyyy-MM-dd HH:mm:ss')
  git commit -m "update node from $updated_submodules at $c"

  $currentBranch = git rev-parse --abbrev-ref HEAD
  if ($currentBranch -eq "main") {
    git push --force;
  }  
}