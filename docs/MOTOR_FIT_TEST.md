# Motor fit test

Use [`out/motor_fit_coupon.stl`](../out/motor_fit_coupon.stl) to find out which motors you have and which grip suits your printer, before printing the frame. Why this matters, and what the `+.15` on the card means: [TOLERANCES.md](TOLERANCES.md).

![coupon](images/motor_fit_coupon_iso.png)

## The card
- **79 x 89 x 8.5 mm**, open lattice base: bars, a rim, and pads under the labels. The open base saves about a third of the filament; reducing infill wouldn't, because thin parts print solid anyway.
- **Rows** (raised label on the left): motor diameter.

  | row | motor class |
  |---|---|
  | 6.0 | 0615 |
  | 7.0 | 0716 / **0720** (what the Pluto 1.2 kit motors turned out to be) |
  | 8.0 | 0820 / 816 |
  | 8.5 | 8520 |
  | 10.0 | 1020 |

- **Columns** (raised label on top): squeeze, meaning how much smaller than the motor the 4 crush ribs are, on the diameter. `0` is a slip fit to compare against, then `0.1`, `0.2`, `0.3`.
- **Corner label `+.15`:** every sleeve is also opened up by the 0.15 mm shrink allowance.
- Each sleeve is the frame's exact motor tube: 0.9 mm wall, 8.5 mm tall, 1 mm bottom lip, 4 crush ribs.

## Print
- **Same printer, filament and settings as the frame.** The test only means something if it prints the same way. Our settings: PETG, 0.4 mm nozzle, 0.16 mm layers, 3 walls, no supports, 4 mm brim.
- **Don't scale it.**
- About 43 min and 9.5 g on a Bambu P1S.
- Let it cool completely before testing. PETG is slightly soft while warm.

## Test
1. **Find the row.** Drop a motor (no prop) into the `0` sleeve of each row:
   - it won't go in: too small;
   - it slides in with almost no force and doesn't wobble: **your row**;
   - it rattles: too big.

   Calipers on the can help too.
2. **Find the column.** In your row, press a motor into `0.1`, `0.2` and `0.3` with the prop tool. The right column is the tightest one where:
   - the motor goes **all the way down onto the lip**, without the sleeve cracking or turning white;
   - turned upside down and shaken, the motor stays put;
   - with a prop pushed on and pulled off, the motor doesn't creep up.
3. **Get it out** by pushing up on the motor's end cap through the hole underneath, with a toothpick or a 2 mm hex key. The leads come out through that same hole, so rest the card on an open box while testing.
4. Repeat with all 4 motors and pick the column where every one passes.

## Use the result
- **7.0 row, `0.2` column:** print [`out/pluto_frame.stl`](../out/pluto_frame.stl) as it is.
- **Anything else:** edit `src/p_params.py` (`MOTOR_D` = row, `SQUEEZE` = column; `HOLE_COMP` stays 0.15, since the card already includes it), then run `python tools/export.py`.

Motor length matters too: the props sit on top of the motor. 0720 and 8520 motors are 20 mm long, 0615 and 0716 are 15–16 mm. If you change the motor size, recheck the prop clearance with `kerf_scripts/frame.py` and rerun `tools/sim.py`.
