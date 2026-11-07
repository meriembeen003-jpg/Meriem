"""Fetch candidate astronomical images from public GitHub repos via the blobs API.

Downloads are stored under archive/raw/<repo-slug>/<basename>.
Only observational/space imagery is requested; instrument/diagram shots are excluded.
"""
import json
import os
import sys
import time
import base64
import urllib.request
import concurrent.futures as cf

TOK = os.popen("gh auth token").read().strip()
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")

# (repo, branch, path)
SOURCES = [
    # WebbCompare (NASA/STScI/ESA press imagery, full-frame)
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/webb/deep_field.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/webb/carina.jpg"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/webb/tarantula.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/webb/cartwheel.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/webb/stephans_quintet.jpg"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/webb/southern_nebula.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/hubble/deep_field.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/hubble/carina.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/hubble/cartwheel.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/hubble/tarantula.png"),
    ("JohnEdChristensen/WebbCompare", "gh-pages", "img/hubble/southern_nebula.png"),
    # unit511/space-wallpapers : 4K renders of NASA / STScI press images
    ("unit511/space-wallpapers", "master", "4K/webb_first_deep_field_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_carina_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_carina_miri_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_tarantula.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_cartwheel.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_stephans_quintet_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_southern_ring_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_ring.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_pillars.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_cassiopeia_a.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_ic_348.png"),
    ("unit511/space-wallpapers", "master", "4K/webb_chamaeleon.png"),
    ("unit511/space-wallpapers", "master", "1440p/webb_ice_1440p.png"),
    ("unit511/space-wallpapers", "master", "4K/andromeda_4K.png"),
    ("unit511/space-wallpapers", "master", "1440p/whirlpool_galaxy_1440p.png"),
    ("unit511/space-wallpapers", "master", "1440p/m81_galaxy_1440p.png"),
    ("unit511/space-wallpapers", "master", "4K/spiral_galaxy_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/two_galaxies_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/rainbow_galaxy_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/ufo_galaxy_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/faint_compact_galaxy_4K.png"),
    ("unit511/space-wallpapers", "master", "1080p/galaxy_pair_1080p.png"),
    ("unit511/space-wallpapers", "master", "4K/crab_nebula_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/carina_nebula_4K.png"),
    ("unit511/space-wallpapers", "master", "1080p/cats_paw_nebula_1080p.png"),
    ("unit511/space-wallpapers", "master", "4K/na_nebula_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/na_nebula_2_4K.png"),
    ("unit511/space-wallpapers", "master", "1440p/lagoon_nebula_1440p.png"),
    ("unit511/space-wallpapers", "master", "4K/cepheus_bc_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/life_and_death_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/cygnus_x_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/w5_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/lmc_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/milky_way_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/orion_hearth_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/orion_dreamy_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/orion_sword_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/superbubble_4K.png"),
    ("unit511/space-wallpapers", "master", "4K/triton.png"),
    ("unit511/space-wallpapers", "master", "1224x2700/pluto.png"),
    # Planck CMB (microwave) face 0 and 2 of 6 cubemap faces
    ("hannorein/planck_cmb_cubemaps", "master", "0_cmb_planck_1024.png"),
    ("hannorein/planck_cmb_cubemaps", "master", "2_cmb_planck_1024.png"),
    # Calibrated science FITS products
    ("lucy-clews/NGC1044-MeerKAT-data-products", "main", "L_7arc-StokesI-MFS-image.fits"),
    ("tomasplsek/CADET", "main", "example/NGC4778.fits"),
    # NASA 3D Resources: star maps + supernova remnant reference imagery
    ("nasa/NASA-3D-Resources", "master", "3D Printing/IC 443 (Jellyfish Nebula)/IC 443 (Jellyfish Nebula).png"),
    ("nasa/NASA-3D-Resources", "master", "3D Printing/Tycho Supernova Remnant/Tycho Supernova Remnant.png"),
    ("nasa/NASA-3D-Resources", "master", "3D Printing/Westerlund 2/Westerlund 2.png"),
    ("nasa/NASA-3D-Resources", "master", "3D Printing/NGC3344/NGC3344.png"),
]


def slug(repo):
    return repo.split("/")[1]


def subdir(path):
    """Keep telescope/collection sub-folders so files never collide."""
    parts = path.split("/")
    if len(parts) > 1 and parts[-2] in {"webb", "hubble"}:
        return parts[-2]
    return None


def blob_sha(repo, branch, path):
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOK}",
                                              "Accept": "application/vnd.github+json",
                                              "User-Agent": "archive"})
    tree = json.load(urllib.request.urlopen(req, timeout=90))["tree"]
    for t in tree:
        if t["path"] == path:
            return t["sha"], t.get("size", 0)
    raise KeyError(f"{repo}:{path}")


TREES = {}


def get_tree(repo, branch):
    key = (repo, branch)
    if key not in TREES:
        url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOK}",
                                                  "Accept": "application/vnd.github+json",
                                                  "User-Agent": "archive"})
        TREES[key] = {t["path"]: t for t in json.load(urllib.request.urlopen(req, timeout=120))["tree"]}
    return TREES[key]


def fetch(item):
    repo, branch, path = item
    sub = subdir(path)
    outdir = os.path.join(RAW, slug(repo), sub) if sub else os.path.join(RAW, slug(repo))
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, os.path.basename(path))
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return f"skip {os.path.basename(path)}"
    tree = get_tree(repo, branch)
    if path not in tree:
        return f"MISSING {repo}:{path}"
    sha = tree[path]["sha"]
    url = f"https://api.github.com/repos/{repo}/git/blobs/{sha}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOK}",
                                                       "Accept": "application/vnd.github+json",
                                                       "User-Agent": "archive"})
            j = json.load(urllib.request.urlopen(req, timeout=180))
            data = base64.b64decode(j["content"])
            with open(out, "wb") as fh:
                fh.write(data)
            return f"ok {len(data)/1e6:6.2f}MB {os.path.basename(path)}"
        except Exception as exc:  # noqa: BLE001
            if attempt == 3:
                return f"FAIL {path}: {exc}"
            time.sleep(2 + attempt * 3)


if __name__ == "__main__":
    todo = SOURCES
    if len(sys.argv) > 1:
        todo = [s for s in SOURCES if any(a in s[2] for a in sys.argv[1:])]
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(fetch, todo):
            print(res, flush=True)
