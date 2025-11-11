#!/usr/bin/env python3
import argparse
import json
import hashlib
import re
import shutil
from pathlib import Path
import datetime
import fnmatch
import os
import sys

DEFAULT_IGNORE = [
    "index.html",
    "style.css",
    "archive/**",
    "change_log.json",
    "chat_history.json",
    "meta.json",
    "snapshot_manager.py"
]

ARCHIVE_DIRNAME = "archive"

### 보조
# 파일 내용의 해시값을 계산
def sha256_of_file(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

### 보조
# 어떤 파일이 무시해도 되는 케이스인지 판단
def matches_any_pattern(relpath: str, patterns):
    # normalize to POSIX style for matching
    p = relpath.replace(os.sep, '/')
    for pat in patterns:
        if fnmatch.fnmatch(p, pat):
            return True
    return False

### 보조
def scan_tree(root: Path, ignore_patterns):
    files = {}
    for p in root.rglob('*'):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            # skip archive folder entirely
            if rel.startswith(ARCHIVE_DIRNAME + "/") or rel == ARCHIVE_DIRNAME:
                continue
            if matches_any_pattern(rel, ignore_patterns):
                continue
            files[rel] = {
                "path": p,
                "hash": sha256_of_file(p),
                "mtime": p.stat().st_mtime,
                "size": p.stat().st_size
            }
    return files

### 보조
def find_latest_version(archive_root: Path):
    if not archive_root.exists():
        return None
    candidates = []
    for p in archive_root.iterdir():
        if p.is_dir() and p.name.startswith('V'):
            # expect Vn-i-YYYY...
            candidates.append(p)
    if not candidates:
        return None
    # choose the directory with latest timestamp in the name (fallback to mtime)
    def extract_ts(dirpath: Path):
        # try to parse trailing 14-digit timestamp
        name = dirpath.name
        parts = name.split('-')
        try:
            ts = parts[-1]
            dt = datetime.datetime.strptime(ts, "%Y%m%d%H%M%S")
            return dt
        except Exception:
            return datetime.datetime.fromtimestamp(dirpath.stat().st_mtime)
    candidates.sort(key=extract_ts, reverse=True)
    return candidates[0]

### 보조
def read_meta(version_dir: Path):
    meta_file = version_dir / "meta.json"
    if not meta_file.exists():
        return None
    return json.loads(meta_file.read_text(encoding='utf-8'))





### 보조
def make_new_version_name2(archive_root: Path):
    # simple linear scheme: n = 1, i = count+1
    existing = [p for p in archive_root.iterdir() if p.is_dir() and p.name.startswith('V')]
    i = len(existing) + 1
    n = 1
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"V{n}-{i}-{ts}"






def make_new_version_name(archive_root: Path, parent_name: str | None):
    # version 형식: v{generation}-{index}
    version_dirs = [p.name for p in archive_root.iterdir() if p.is_dir()]
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    if parent_name is None:
        # 최초 버전
        return "v1-1"# + f"-{ts}"

    # 부모 세대 번호 추출
    match = re.match(r"v(\d+)-(\d+)", parent_name)
    if not match:
        raise ValueError(f"Invalid parent name format: {parent_name}")

    parent_gen = int(match.group(1))

    # 자식들은 generation + 1
    child_gen = parent_gen + 1

    # 현재 같은 세대(child_gen)의 기존 버전들 찾기
    same_gen = [
        p for p in version_dirs if re.match(fr"v{child_gen}-\d+", p)
    ]

    # 같은 세대에서 index 번호 중 최대값 + 1
    max_index = 0
    for name in same_gen:
        m = re.match(fr"v{child_gen}-(\d+)", name)
        if m:
            idx = int(m.group(1))
            max_index = max(max_index, idx)

    new_index = max_index + 1

    return f"v{child_gen}-{new_index}"# + f"-{ts}"





# 주요 함수
def create_version(root: Path, ignore_patterns, parent_name = None, chat=None, summary=""):
    archive_root = root / ARCHIVE_DIRNAME
    archive_root.mkdir(exist_ok=True)
    
    # parent_dir = find_latest_version(archive_root)
    # parent_meta = None
    # parent_files = {}
    # parent_name = None
    # if parent_dir:
    #     parent_meta = read_meta(parent_dir)
    #     parent_name = parent_dir.name
    #     if parent_meta and "file_index" in parent_meta:
    #         parent_files = parent_meta["file_index"]
    # else:
    #     parent_name = None


    parent_meta = None
    parent_files = {}
    if parent_name:
        parent_dir = archive_root / parent_name
        if os.path.exists(parent_dir):
            parent_meta = read_meta(parent_dir)
            if parent_meta and "file_index" in parent_meta:
                parent_files = parent_meta["file_index"]
    else:
        parent_name = None




    current_files = scan_tree(root, ignore_patterns)

    added = []
    deleted = []
    changed = []
    no_changes = []

    # Determine deleted: in parent but not in current
    for rel, info in parent_files.items():
        if rel not in current_files:
            deleted.append({"name": Path(rel).name, "path": rel, "type": "Delete"})

   # Determine added/changed/nochange
    for rel, info in current_files.items():
        if rel not in parent_files:
            added.append({"name": Path(rel).name, "path": rel, "type": "Add"})
        else:
            parent_hash = parent_files[rel]["hash"]
            if parent_hash != info["hash"]:
                # 파일이 변경된 경우 → 현재 버전이 최신 버전
                changed.append({"name": Path(rel).name, "path": rel, "type": "Change"})
            else:
                # 파일이 그대로인 경우 → 부모의 last_version 계승
                last_version = parent_name
                if parent_meta:
                    # 부모의 meta에서 이 파일의 last_version 찾아 계승
                    prev_nochange = next((f for f in parent_meta.get("no_changes", [])
                                        if f["path"] == rel), None)
                    if prev_nochange:
                        last_version = prev_nochange.get("last_version", parent_name)
                    else:
                        # 부모에서 새로 추가되었거나 변경된 파일이었다면 부모가 마지막 버전
                        last_version = parent_name

                no_changes.append({
                    "name": Path(rel).name,
                    "path": rel,
                    "last_version": last_version
                })

    # create version folder and copy changed/added files
    version_name = make_new_version_name(archive_root, parent_name)
    version_dir = archive_root / version_name
    files_store = version_dir / "files"
    files_store.mkdir(parents=True, exist_ok=True)

    # Copy Add and Change files
    for item in added + changed:
        rel = item["path"]
        src = root / rel
        dst = files_store / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # build file_index for meta: map rel -> {hash, size, mtime}
    file_index = {}
    for rel, info in current_files.items():
        file_index[rel] = {"hash": info["hash"], "size": info["size"], "mtime": info["mtime"]}

    meta = {
        "version": version_name,
        "parent": parent_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": summary,
        "chat": chat or {},
        "changes": added + changed + deleted,
        "no_changes": no_changes,
        "file_index": file_index,
    }

    # write meta.json
    version_dir.mkdir(parents=True, exist_ok=True)
    meta_path = version_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=4, ensure_ascii=False), encoding='utf-8')

    print(f"Created version {version_name} at {version_dir}")

    update_change_log(root, version_name, summary, parent_name=parent_name, is_current=True)

    return version_name

### 보조
def update_change_log(root: Path, version_name, summary, parent_name=None, is_current=True):
    log_path = root / ARCHIVE_DIRNAME / "change_log.json"
    if log_path.exists():
        log_data = json.loads(log_path.read_text(encoding="utf-8"))
    else:
        log_data = {"versions": []}

    # 이전 최신 버전은 is_latest=False로
    for v in log_data["versions"]:
        v["is_latest"] = False
        if is_current:
            v["is_current"] = False

    log_data["versions"].append({
        "version": version_name,
        "parent": parent_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": summary,
        "is_latest": True,
        "is_current": is_current
    })

    log_path.write_text(json.dumps(log_data, indent=4, ensure_ascii=False), encoding="utf-8")

# 주요 함수
def list_versions(root: Path):
    archive_root = root / ARCHIVE_DIRNAME
    if not archive_root.exists():
        print("No archive found.")
        return
    for p in sorted(archive_root.iterdir()):
        if p.is_dir():
            print(p.name)

# 주요 함수
def restore_version2(root: Path, version_name: str, overwrite=False):
    archive_root = root / ARCHIVE_DIRNAME
    version_dir = archive_root / version_name
    if not version_dir.exists():
        print("Version not found:", version_name)
        return False
    meta = read_meta(version_dir)
    if not meta:
        print("meta.json missing in version:", version_name)
        return False

    # Prepare a restore folder to assemble files
    restore_tmp = root / f"_restore_{version_name}"
    if restore_tmp.exists():
        shutil.rmtree(restore_tmp)
    restore_tmp.mkdir()

    # First, for files listed in file_index:
    file_index = meta.get("file_index", {})
    for rel, info in file_index.items():
        # check if this file was included (changed/added) in this version's files
        src_in_version = version_dir / "files" / rel
        if src_in_version.exists():
            dst = restore_tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_in_version, dst)
        else:
            # find in last_version chain: use meta.parent to locate in archive
            last_ver = meta.get("parent")
            found = False
            while last_ver:
                last_dir = archive_root / last_ver
                last_meta = read_meta(last_dir)
                if last_meta and rel in last_meta.get("file_index", {}):
                    candidate = last_dir / "files" / rel
                    if candidate.exists():
                        dst = restore_tmp / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(candidate, dst)
                        found = True
                        break
                last_ver = last_meta.get("parent") if last_meta else None
            if not found:
                # file may have existed in parent workspace (initial) - cannot restore
                print("Warning: couldn't find historical copy for", rel)

    # Also, ensure ignored files like index.html are left alone; we restore only tracked files.
    # Move/replace to root
    for p in restore_tmp.rglob('*'):
        if p.is_file():
            rel = p.relative_to(restore_tmp)
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and not overwrite:
                print(f"Skipping existing {dst} (use --overwrite to force)")
            else:
                shutil.copy2(p, dst)

    shutil.rmtree(restore_tmp)
    print("Restore complete (files copied to root).")
    return True



def restore_version(root: Path, version_name: str, overwrite=True):
    archive_root = root / ARCHIVE_DIRNAME
    version_dir = archive_root / version_name
    if not version_dir.exists():
        print("Version not found:", version_name)
        return False

    meta = read_meta(version_dir)
    if not meta:
        print("meta.json missing in version:", version_name)
        return False

    ignore_patterns = DEFAULT_IGNORE
    file_index = meta.get("file_index", {})
    no_changes = meta.get("no_changes", [])
    nochange_map = {item["path"]: item["last_version"] for item in no_changes}

    # 현재 폴더 스캔
    current_files = scan_tree(root, ignore_patterns)

    # 1️⃣ 현재 폴더에만 있는 파일 삭제
    current_rels = set(current_files.keys())
    target_rels = set(file_index.keys())
    extra_files = current_rels - target_rels
    for rel in extra_files:
        p = root / rel
        if p.exists():
            p.unlink()
            print(f"🗑 Deleted extra file: {rel}")

    # 2️⃣ 복원용 임시폴더
    restore_tmp = root / f"_restore_{version_name}"
    if restore_tmp.exists():
        shutil.rmtree(restore_tmp)
    restore_tmp.mkdir(parents=True)

    # 3️⃣ 복원 파일 복사
    for rel, info in file_index.items():
        dst = restore_tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        # 우선 이 버전에서 변경된 파일 확인
        src_in_version = version_dir / "files" / rel
        if src_in_version.exists():
            shutil.copy2(src_in_version, dst)
            continue

        # 변경되지 않았으면 last_version에서 복사
        if rel in nochange_map:
            last_ver = nochange_map[rel]
            candidate = archive_root / last_ver / "files" / rel
            if candidate.exists():
                shutil.copy2(candidate, dst)
            else:
                print(f"⚠️ Warning: {rel} not found in {last_ver}")

    # 4️⃣ 실제 루트로 반영
    for p in restore_tmp.rglob('*'):
        if p.is_file():
            rel = p.relative_to(restore_tmp)
            if matches_any_pattern(str(rel), ignore_patterns):
                continue
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and not overwrite:
                print(f"Skipping {dst} (use overwrite=True to force)")
            else:
                if dst.exists():
                    dst.unlink()  # 기존 파일을 먼저 제거 (명시적 덮어쓰기)
                shutil.copy2(p, dst)

    shutil.rmtree(restore_tmp)
    print(f"✅ Restore complete: {version_name}")
    return True





### 보조
def load_chat_history(root: Path):
    chat_file = root / "chat_history.json"
    if chat_file.exists():
        try:
            return json.loads(chat_file.read_text(encoding='utf-8'))
        except Exception:
            return {"warning":"chat_history.json exists but failed to parse"}
    return {}

def main():
    parser = argparse.ArgumentParser(description="Simple snapshot manager")
    sub = parser.add_subparsers(dest='cmd')

    p_create = sub.add_parser('create', help='Create a new version snapshot')
    p_create.add_argument('--summary', '-s', default='', help='Short summary for this snapshot')
    p_create.add_argument('--parent', '-p', default='', help='Node name of creating new node')
    p_create.add_argument('--ignore-file', '-i', help='Path to a JSON file with ignore patterns (list)')
    p_create.add_argument('--chat-file', '-c', help='Path to a JSON chat file to include (defaults to chat_history.json)')

    p_list = sub.add_parser('list', help='List versions in archive')

    p_restore = sub.add_parser('restore', help='Restore a version to current root (copies files)')
    p_restore.add_argument('version', help='Version name to restore (e.g. V1-1-YYYY...)')
    p_restore.add_argument('--overwrite', action='store_true', help='Overwrite existing files when restoring')

    args = parser.parse_args()
    root = Path.cwd()

    if args.cmd == 'create':
        ignore = DEFAULT_IGNORE.copy()
        if args.ignore_file:
            try:
                ignore = json.loads(Path(args.ignore_file).read_text(encoding='utf-8'))
            except Exception as e:
                print("Failed to read ignore file:", e)
                sys.exit(1)
        chat = {}
        if args.chat_file:
            try:
                chat = json.loads(Path(args.chat_file).read_text(encoding='utf-8'))
            except Exception as e:
                print("Failed to read chat file:", e)
                sys.exit(1)
        else:
            chat = load_chat_history(root)

        if args.parent:
            parent = args.parent
        else:
            parent = None

        version = create_version(root, ignore, chat=chat, parent_name=parent, summary=args.summary)
        print("Version created:", version)
    elif args.cmd == 'list':
        list_versions(root)
    elif args.cmd == 'restore':
        restore_version(root, args.version, overwrite=args.overwrite)
    else:
        parser.print_help()

# if __name__ == '__main__':
#     main()




root = Path.cwd() / "snapshot_test" /"test"
ignore = DEFAULT_IGNORE.copy()




create_version(root, ignore)
#create_version(root, ignore, parent_name="v1-1")




#restore_version(root, "v1-1")
