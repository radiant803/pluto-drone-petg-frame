# Specs the frame is built around (sources and confidence)

**Status key:**
- **PUBLISHED**: stated by Drona Aviation.
- **MEASURED**: taken from the to-scale top-view drawing in Drona's Pluto 1.2 manual, scaled by the known 48 mm board size. The scale checks out: the 55 mm prop measures 54.0 mm.
- **TESTED**: confirmed with printed test parts and real kit parts.
- **ASSUMED**: not published; a typical value.

| item | value | status | source |
|---|---|---|---|
| Flight controller | Primus V5, 48 x 48 mm, 3.6 mm mounting holes, 10.4 g | PUBLISHED | Pluto 1.2 manual, spec page |
| Board mounting | 4 rubber dampers in the board's corner holes, screws into the frame; the canopy's tabs sit between screw head and damper; the board must touch only the dampers | PUBLISHED | manual, assembly section and FAQ |
| Board hole pattern | 41.0 x 41.0 mm square | MEASURED (render: 40.7–41.2), and looked right against a real board | manual render |
| Motor ports | M5 front-left, M8 front-right, M6 rear-left, M7 rear-right | MEASURED | board printing visible in the manual render |
| Motors | **0720** coreless brushed, 7 x 20 mm; 50,000 rpm at 3.7 V, 0.18 A no-load, 0.8 ohm | **TESTED** (fit coupon + test sleeve) + PUBLISHED electrical data | Drona hardware parts page (lists 0615 / 0720 / 8520 / 1020 for Primus) |
| Motor mass | about 3.2 g | ASSUMED | typical 0720 |
| Motor plug | 2-pin, about 4.4 mm wide, about 1.25 mm pitch | MEASURED | manual render |
| Motor positions | (±46.5, ±46.5) mm: 93 x 93 square, 131.5 mm diagonal | MEASURED (all 4 hubs agree within 0.2 mm) | manual render |
| Props | 2-blade, 55 mm; A = clockwise (front-left, rear-right), B = counter-clockwise (front-right, rear-left) | PUBLISHED | manual |
| Motor mixing | QuadX, order REAR_R, FRONT_R, REAR_L, FRONT_L, props-in; matches the A/B layout | PUBLISHED (open source) | MagisV2 firmware, `src/main/flight/mixer.cpp` |
| Battery | Pluto 600: 3.7 V, 600 mAh, 25C, 37 x 24 x 8 mm, 16 g; slides in from the front | PUBLISHED | parts page, manual |
| Battery plug on the board | left edge, middle | MEASURED | manual render |
| Stock drone | 160 mm frame size, 50 mm tall, 60 g with battery, 10 g payload | PUBLISHED | manual |
| Screws | M2, cross head, self-tapping into the post | ASSUMED (consistent with 3.6 mm damper holes and the kit screws) | |
| Dampers | about 5.6 mm flange, about 1.4 mm under the board | ASSUMED (typical M2 flight-controller grommet) | |

## Links
- Pluto 1.2 manual (PDF): [github.com/DronaAviation/Resources](https://github.com/DronaAviation/Resources) (`Manual/Pluto 1.2_Manual.pdf`)
- Drona hardware parts (motors, props, batteries): [dronaaviation.com/hardware/parts](https://dronaaviation.com/hardware/parts)
- Primus V5 product page: [dronaaviation.com/product/primus-v5-flight-controller](https://www.dronaaviation.com/product/primus-v5-flight-controller)
- MagisV2 firmware: [github.com/DronaAviation/MagisV2](https://github.com/DronaAviation/MagisV2)

## What wasn't copied
No Drona images, drawings or files are included in this repository. The measurements above were taken from their public manual, and the frame geometry is an original design.
