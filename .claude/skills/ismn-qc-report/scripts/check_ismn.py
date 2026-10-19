"""ISMN 일자료 CSV(ismn_daily.py 출력) 점검표 생성.

사용: python check_ismn.py <csv_dir_or_file> [--start 1980-01-01 --end 2025-12-31]
      [--sm-max 0.6] [--flat-days 10] [--jump 0.15] [--out qc_table.csv]
값을 고치지 않는다. 플래그만 단다.
"""
import argparse, glob, os
import numpy as np
import pandas as pd

REQ_COLS = ["date_time", "latitude", "longitude", "sm_corrected"]
LAT_RANGE = (-60.0, 90.0)       # 전지구, 남극 제외
LON360_RANGE = (0.0, 360.0)     # 0–360 표기, 360 미포함


def longest_flat_run(x):
    if len(x) < 2:
        return 0
    same = np.isclose(np.diff(x), 0.0, atol=1e-6)
    best = cur = 0
    for s in same:
        cur = cur + 1 if s else 0
        best = max(best, cur)
    return best + 1 if best else 0


def check(path, a):
    r = {"file": os.path.basename(path)}
    try:
        df = pd.read_csv(path)
    except Exception as e:
        r["error"] = f"read: {e}"
        return r
    miss = [c for c in REQ_COLS if c not in df.columns]
    if miss:
        r["error"] = f"missing columns: {miss}"
        return r
    df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
    r["n_bad_date"] = int(df["date_time"].isna().sum())
    df = df.dropna(subset=["date_time"])
    if df.empty:
        r["error"] = "empty"
        return r

    r["n_dup_date"] = int(df["date_time"].duplicated().sum())
    r["sorted"] = bool(df["date_time"].is_monotonic_increasing)

    # 위치
    r["lat"] = float(df["latitude"].iloc[0])
    r["lon"] = float(df["longitude"].iloc[0])
    r["coord_varies"] = bool(df["latitude"].nunique() > 1 or df["longitude"].nunique() > 1)
    lon360 = r["lon"] + 360 if r["lon"] < 0 else r["lon"]
    r["in_domain"] = bool(LAT_RANGE[0] <= r["lat"] <= LAT_RANGE[1]
                          and LON360_RANGE[0] <= lon360 < LON360_RANGE[1])

    # 결측(기간 내 빠진 날)
    d0, d1 = df["date_time"].min(), df["date_time"].max()
    r["first"], r["last"] = d0.date().isoformat(), d1.date().isoformat()
    span = (d1 - d0).days + 1
    r["n_days"] = int(df["date_time"].nunique())
    r["missing_pct_in_span"] = round(100 * (1 - r["n_days"] / span), 1)
    if a.start and a.end:
        win = pd.date_range(a.start, a.end, freq="D")
        r["coverage_pct_window"] = round(100 * df["date_time"].isin(win).sum() / len(win), 1)
    r["n_nan_sm"] = int(df["sm_corrected"].isna().sum())

    # 단위·범위
    sm = df["sm_corrected"].dropna().to_numpy(dtype=float)
    if len(sm):
        r["sm_min"], r["sm_max"] = round(sm.min(), 4), round(sm.max(), 4)
        r["sm_median"] = round(float(np.median(sm)), 4)
        r["n_neg"] = int((sm < 0).sum())
        r["n_gt_smmax"] = int((sm > a.sm_max).sum())
        r["unit_suspect"] = bool(np.median(sm) > 1.0)   # % 단위 의심
        r["flat_run_max"] = longest_flat_run(sm)
        r["n_jump"] = int((np.abs(np.diff(sm)) > a.jump).sum())

    flags = []
    if r["n_bad_date"] or r["n_dup_date"] or not r["sorted"]: flags.append("date")
    if r["coord_varies"]: flags.append("coord_varies")
    if not r["in_domain"]: flags.append("out_of_domain")
    if r.get("unit_suspect"): flags.append("unit")
    if r.get("n_neg") or r.get("n_gt_smmax"): flags.append("range")
    if r.get("flat_run_max", 0) >= a.flat_days: flags.append("flatline")
    if r.get("n_jump"): flags.append("jump")
    r["flags"] = ";".join(flags)
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--start"); p.add_argument("--end")
    p.add_argument("--sm-max", type=float, default=0.6)
    p.add_argument("--flat-days", type=int, default=10)
    p.add_argument("--jump", type=float, default=0.15)
    p.add_argument("--out", default="qc_table.csv")
    a = p.parse_args()

    files = sorted(glob.glob(os.path.join(a.path, "*.csv"))) if os.path.isdir(a.path) else [a.path]
    rows = [check(f, a) for f in files]
    t = pd.DataFrame(rows)

    # 같은 좌표를 쓰는 파일(다른 센서·깊이 가능성)
    if {"lat", "lon"} <= set(t.columns):
        key = t["lat"].round(5).astype(str) + "," + t["lon"].round(5).astype(str)
        t["n_files_same_coord"] = key.map(key.value_counts())
    t.to_csv(a.out, index=False)

    print(f"files: {len(t)}")
    if "error" in t: print(f"error/empty: {t['error'].notna().sum()}")
    if "flags" in t:
        f = t["flags"].fillna("").str.split(";").explode()
        print("flag counts:"); print(f[f != ""].value_counts().to_string())
    if "n_files_same_coord" in t:
        print(f"files sharing coordinates: {(t['n_files_same_coord'] > 1).sum()}")
    print(f"saved: {a.out}")


if __name__ == "__main__":
    main()
