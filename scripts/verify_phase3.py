import subprocess, os, sys, tempfile

verify_script = r"e:\Model-Design\c302\scripts\verify-comment-only\verify_comment_only.py"
project_root = r"e:\Model-Design\c302"

files = [
    "project/c302/bioparameters.py",
    "project/c302/parameters_A.py",
    "project/c302/parameters_B.py",
    "project/c302/parameters_C.py",
    "project/c302/parameters_C0.py",
    "project/c302/parameters_C1.py",
    "project/c302/parameters_C2.py",
    "project/c302/parameters_D.py",
    "project/c302/parameters_D1.py",
    "project/c302/parameters_BC1.py",
    "project/c302/parameters_W2D.py",
]

all_ok = True
for rel_path in files:
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel_path}"],
        capture_output=True, cwd=project_root
    )
    if result.returncode != 0:
        print(f"[SKIP] {rel_path}: git error: {result.stderr.decode()}")
        continue
    orig_bytes = result.stdout

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="wb") as f:
        f.write(orig_bytes)
        orig_path = f.name

    modified_path = os.path.join(project_root, rel_path)

    vr = subprocess.run(
        [sys.executable, verify_script, orig_path, modified_path],
        capture_output=True, text=True, cwd=project_root
    )
    os.unlink(orig_path)

    basename = os.path.basename(rel_path)
    if vr.returncode == 0:
        print(f"[OK] {basename}")
    else:
        all_ok = False
        print(f"[FAIL] {basename}")
        print(vr.stdout[-2000:])
        print(vr.stderr[-500:])

print()
print("All OK" if all_ok else "Some files FAILED")
