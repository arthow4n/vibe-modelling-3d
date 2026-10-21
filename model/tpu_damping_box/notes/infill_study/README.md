# N1 infill configurations — actual sliced paths

[Current concept comparison](../preformed_surface_concepts.md) ·
[Consecutive-layer paths](../../renders/concepts/infill_study_paths.svg) ·
[Full wall paths](../../renders/concepts/infill_study_full.svg) ·
[Roof/support-layer paths](../../renders/concepts/infill_study_roofs.svg)

The user explicitly authorizes exploring infill configurations and requires the
**actual sliced print paths**. These images come from fresh OrcaSlicer **2.4.2**
G-code, not generic infill artwork. They show deposited centerlines in real mm:
blue outer walls, grey inner walls, orange sparse infill, purple bridge/solid
fill. All material is black TPU. Display stroke widths are illustrative; travel
and retraction moves are omitted from the plots and retained in the G-code.

The proxy is a **60 × 6 × 16 mm straight wall**, its 60 × 6 mm edge on the bed.
It answers whether ordinary Classic produces substantial surface paths with a
sparse core, how that core changes between layers, and how its top closes.
It is not a new full-box design or a proposed print batch. It has no real cup
corners, contents, solid-corner modifiers, matching lid, complex pockets or tall
walls. It cannot qualify those features or demonstrate smoother prints.

## Three concrete candidate configurations

| ID / supplied study profile | Infill | Intended comparison | Native slice / G-code |
| --- | --- | --- | --- |
| **G20** · [JSON](G20_process.json) | Gyroid, **20%** | Preferred first infill candidate: curved sparse core with less material than G30. | [Receipt](G20_review.json) · [G-code.gz](G20_paths.gcode.gz) |
| **G30** · [JSON](G30_process.json) | Gyroid, **30%** | More core support/contact versus G20; may be stiffer and transmit more impact. | [Receipt](G30_review.json) · [G-code.gz](G30_paths.gcode.gz) |
| **X20** · [JSON](X20_process.json) | Cross Hatch, **20%** | Different run/corner geometry at the same requested percentage. Lower priority than gyroid. | [Receipt](X20_review.json) · [G-code.gz](X20_paths.gcode.gz) |

Hold these shared settings constant:

| Setting | Effective value in all three slices |
| --- | --- |
| Printer / filament setup | Qidi Q2C, 0.4 mm nozzle; retained Generic TPU 95A profile |
| Wall generator / thin-wall detection | **Classic / off** |
| Layer height / initial layer | **0.20 / 0.20 mm** |
| Wall loops | **3**, creating three perimeter paths along each long face |
| Wall widths | Outer **0.42 mm**, inner **0.45 mm** |
| Wall order | **Inner/Outer/Inner**, infill first **off** |
| Sparse infill width / overlap | **0.42 mm / 15%** |
| Top / bottom closure | **6 / 6 layers**, nominal **1.2 mm** each |
| Gyroid optimization / multiline | Off / one line |
| Wall and sparse-fill speed / bridge speed | Retained **25 / 15 mm/s** settings |
| Supports | Off for actual slice; separate automatic probe found none |

These are diagnostic study profiles, not a calibrated spool/printer recipe.
They derive from the existing ordinary-Classic process; the existing B/S/C
profiles remain unchanged. Keep all shared settings fixed when comparing these
three cores. A later skin-count or overlap experiment would be a separate factor.
The [profile attribution/licence](../../profiles/ATTRIBUTION.md) also applies here.

## What the paths establish and change

All three native slices complete with **no reported notices and no proposed
automatic supports**. Their effective settings match the table. The plots at
Z **4.0, 4.2 and 4.4 mm** contain actual sparse infill, surrounded by one outer
and two inner perimeter contours. Thus this 6 mm wall does leave space for the
proposed core; it is not merely an infill label on a solid thin wall.

G20 visibly changes from an along-wall wave to cross-gap lobes in those three
layers. G30 has more closely spaced core runs; X20 has more angular runs that
also change with height. The core-to-skin attachment is **not eliminated**, and
none is a single uninterrupted nozzle run. A wave that appears detached in one
2D crop can connect elsewhere or through adjacent layers; this is a 3D core. Numerous G1 segments on a gyroid
curve do not mean numerous starts, travels or strings; these plots do not count
such events. This study does not establish fewer starts than B.

At Z **14.8 mm**, the last sparse layer also has small internal solid regions.
At Z **15.0 mm**, Orca classifies the first closing layer as **Internal Bridge**
in all three configurations. Its direction/layout differs between the patterns.
The [paired roof views](../../renders/concepts/infill_study_roofs.svg) expose that
construction. Slicer classification and a clean support probe do not prove TPU
bridging quality or a smooth top surface. Full-cup floor/pad closure would need
its own geometry and path review.

For the same proxy, deposited **sparse-infill centerline length** over the entire
study is approximately **8.97 m (G20), 13.68 m (G30), 10.97 m (X20)**. Thus X20
uses about 22% more sparse-path length than G20 despite the same requested 20%.
This is a scoped toolpath comparison, not measured mass, print time, stiffness or
damping. Equal requested percentages do not establish equal core material or
physical response. [Machine-readable paths/settings summary](paths.json).

**Recommendation:** keep G20 as the leading infill candidate, G30 as its denser
comparison, and X20 as a secondary pattern comparison. Their purpose is to test
whether normal infill plus multi-path skins can improve the face while retaining
useful damping. The slice does not rank their actual surface finish or quietness.
Do not jump from this short proxy to an application-sized liner.

## Whole-liner requirements left outside this proxy

N1 still needs a thicker volumetric cup, a matching pad and **100% local solid
corner regions** in a prepared project. A rounded CAD corner filled at 20% is
not a solid corner land. The proxy's end perimeters are not a check of that
full corner construction. The current G20/G30/X20 JSON files contain global
settings only; they do not supply those model-specific regions.

Existing B/S geometry has CAD air gaps. Changing its sparse-infill dropdown does
not put gyroid inside those gaps. Conversely, applying the old 100% process to
a new solid-volume wall removes the intended sparse core. A new selected CAD
volume and prepared project would be needed for a complete N1 liner.

## Reproduce and inspect

Proxy source and matching exports: [Python](../../infill_wall_study.py),
[STEP](../../infill_wall_study.step), [STL](../../infill_wall_study.stl).
[Native geometry/export receipt](geometry.json). The exports have matching
placement and units from the same evaluated source; they are a diagnostic proxy.

From the repository root, build the proxy once:

```sh
./evaluate_model.py model/tpu_damping_box/infill_wall_study.py --export \
  --report model/tpu_damping_box/notes/infill_study/geometry.json --summary
```

For each of G20, G30 and X20, substitute the ID in this G20 example:

```sh
./evaluate_model.py --slice-existing model/tpu_damping_box/infill_wall_study.stl \
  --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json \
  --slice-process model/tpu_damping_box/notes/infill_study/G20_process.json \
  --slice-filament model/tpu_damping_box/profiles/tpu95a.json \
  --slice-placement center --slice-keep-run \
  --report model/tpu_damping_box/notes/infill_study/G20_review.json --summary
```

Then run `./execute.py model/tpu_damping_box/review_infill_study.py`. The reader
uses the shared Orca deposition parser, validates the raw input/process against
the native receipt, checks effective settings, archives the G-code and writes
the plots. Its local raw-directory paths refer to this run; compressed G-code
is retained alongside the receipts so the delivered paths survive cleanup of
those temporary run directories. [Reader source](../../review_infill_study.py).

Primary references: Orca's [2.4.2 pattern enumeration](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/v2.4.2/src/libslic3r/PrintConfig.cpp)
includes gyroid and crosshatch; its [pattern guidance](https://github.com/OrcaSlicer/OrcaSlicer/wiki/strength_settings_patterns#cross-hatch)
notes Cross Hatch's angular transitions. No adaptive TPMS/nightly feature is
used. Primary documentation motivates candidate choice, not TPU performance.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Diagnostic proxy | No | `infill_wall_study.py/.step/.stl`; G20/G30/X20 G-code archives | Generated solely to explain paths; no print requested or reported. |
| Final printable liner | N/A | None new | Fit, corner construction, full roof paths, surface quality, damping and tall-wall reliability remain outside this study. |

Attribution, 2026-10-21: GPT-6 family, exact runtime model/reasoning effort not
exposed; Codex shared-workspace CLI/API agent, OpenAI; no subagents. User directs
infill exploration and actual-path delivery; agent authors proxy, study profiles
and path views. Upstream profile licensing remains preserved.
