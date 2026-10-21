# Printing

These settings were tested on a **Bambu Lab P1S** with a 0.4 mm nozzle. Any printer that handles PETG should work, but if yours isn't a P1S, print the [fit coupon](MOTOR_FIT_TEST.md) first, since the motor fit depends on how your printer sizes holes ([TOLERANCES.md](TOLERANCES.md)).

## Material
**PETG.** It's tougher and more flexible than PLA, so it survives crashes instead of shattering, and it doesn't creep under the press-fit motors in a warm room. Avoid PLA for a frame that will crash. ABS and ASA work too, but they'll shrink differently, so redo the fit test.

## Settings

| setting | value | why |
|---|---|---|
| Layer height | 0.16 mm | crisp engraved labels, good bridges |
| Walls | 3 | the arms and tubes are only 0.9–1.2 mm thick, so they print solid anyway |
| Top / bottom layers | 5 / 4 | |
| Infill | 40% gyroid | only the posts and deck have any infill; it barely changes the weight |
| Supports | **off** | none needed: the only bridges are short (arm tops 4.4 mm, window tops, deck bars over the battery bay 25–35 mm) |
| Brim | outer only, 4 mm | the tube and post feet are small; peel it off after |
| Nozzle / bed | 240–250 C / 70–80 C | |
| Part cooling | about 40% | more fan helps the bridges |
| Bed | textured PEI, or glue stick on smooth PEI | PETG can bond too hard to bare smooth PEI |
| Enclosure (P1S) | door closed, lid on | PETG prints better warm |
| Scale | **100%** | scaling breaks the motor fit and the screw holes |

In Bambu Studio: printer `Bambu Lab P1S 0.4 nozzle`, filament `Bambu PETG Basic`, process `0.16mm Optimal`, then change walls, top/bottom layers, infill, supports and brim as in the table.

## Estimates (Bambu Studio, P1S)

| part | time | filament (incl. brim) |
|---|---|---|
| Frame | about 39 min | 9.3 g (about 9.0 g after removing the brim) |
| Motor fit coupon | about 43 min | 9.5 g |

## After printing
- Let it cool fully before pressing motors in.
- Peel the brim off cleanly, especially around the motor tube feet.
- Clear any stringing from inside the motor tubes and the bottom keyholes with a hobby knife. Don't shave the 4 ribs, they're the grip.
- Check the labels are readable and the deck arrow points to the front: the open end of the battery bay, next to the small lead hook.
