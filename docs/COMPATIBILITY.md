# Compatibility: what this version supports

## Works best with: a plain Pluto 1.2
The current version (v1) is designed and checked for the **standard Pluto 1.2 kit with no extra modules**:

| part | supported | how |
|---|---|---|
| Primus V5 flight controller | yes | stock dampers and screws on 4 posts, 41 x 41 mm pattern |
| 4 x 0720 coreless motors | yes | crush-ribbed tubes, fit-tested ([TOLERANCES.md](TOLERANCES.md)) |
| 55 mm A/B props | yes | 10.2 mm clear of the frame, 6.5 mm clear of the board |
| Pluto 600 battery | yes | battery bay with rails and a rear stop |
| Stock canopy | yes | same screw and damper stack as stock |
| Stock prop guards | **no** | they clip onto lugs on the stock motor mounts, which this frame doesn't copy |
| **Add-on modules** (camera, sensors, LEDs, buzzer, payload holders, extra motor modules) | **not supported in v1** | no mounting points, cable routing or strain relief; see below |

Everything the 49 design checks cover (clearances, fits, the board touching only the dampers, prop clearance, battery fit) was checked with **only these stock parts in place**. Nothing else was included in the checks or the simulation.

## Why add-on modules aren't supported yet
The Primus V5 has ports for extra hardware: a camera connector, I²C, SPI, PPM, ADC, PWM and GPIO. Drona offers add-ons that use them, such as the Wi-Fi camera, sensor and motor modules for the MagisV2 add-on firmware, and printed holders for a buzzer, LED, gas sensor (MQ), motion sensor (PIR) and sound sensor. **This frame has no support system for any of them.** It has no mounting points, no cable routing and no strain relief. A module can still be plugged in, but nothing on the frame carries it. That causes the following problems:

### 1. The module's weight hangs on the board and its connectors
With nothing to bolt to, a module ends up hanging from its cable, sitting on the board, or taped somewhere near it. Either way, its weight and every jolt of flight, landing and crashing go through:
- **the board's small connectors and header pins**, and the solder joints holding them to the board. These parts are made to carry signals, not loads;
- **the cable and its crimped contacts**, which can work loose over time.

A 5 g module that's fine sitting still pulls on its connector with roughly 5–10 times its weight during a hard landing, and more in a crash. Repeated over many flights, that can crack solder joints, pull connectors loose or cause intermittent faults, which in a drone can mean a mid-air reset.

### 2. The board floats on soft dampers
The board sits on rubber dampers so the motors' vibration doesn't reach its motion sensors. Adding mass to the board, or tugging on it through a cable:
- **changes how the dampers isolate vibration**, which can put more motor buzz into the gyro and accelerometer and lead to drift, twitchiness or poor height hold;
- **can tilt the board on the dampers** if the weight is off-centre, which makes the drone think it's leaning, so it drifts.

### 3. Less thrust left over
With 0720 motors the simulation gives about 22 g of thrust per motor, about 90 g in total. At the bare build's 55 g, the thrust-to-weight is about 1.6 and it hovers at about 61% throttle ([SIMULATION.md](SIMULATION.md)). With the manual's full 10 g payload:

| | all-up | thrust-to-weight | hover throttle |
|---|---|---|---|
| bare frame build | about 55 g | about 1.6 | about 61% |
| + 5 g module | about 60 g | about 1.5 | about 67% |
| + 10 g payload | about 65 g | about 1.4 | about 73% |

Less spare thrust means slower recovery from gusts and bumps, faster battery drain and hotter motors.

### 4. Balance and props
A module mounted off-centre moves the centre of gravity, so the motors on one side work harder. Loose cables can drift into the props, which sit only a few centimetres from the board.

### 5. Drona's add-on mounts were made for the stock frame
The printed holders Drona publishes were designed around the stock frame and canopy. **They haven't been tested with this frame**, and may not fit or may sit somewhere that blocks the props or the battery.

## If you add a module anyway (at your own risk)
It **may work**, especially with a small, light module. But in this version it **may also put stress on the board and its connectors**. If you try:
1. **Keep it light**, well under the 10 g payload limit. Lighter is safer.
2. **Hold the module with something other than its connector.** Tape or zip-tie it to the frame: the deck bars, a battery-bay wall or the canopy. Never let it hang from its cable or rest on the board.
3. **Leave a small slack loop in the cable** right before the connector, so it can't be pulled tight. Don't glue anything to the board or connectors.
4. **Keep it centred** and route the cables away from the props.
5. **Recalibrate the accelerometer** after fitting it, then hover low and check that it still holds steady.
6. **Check the connectors and cables after each session.** Stop if anything gets loose, warm or intermittent.

## Planned for future versions
Module support will be improved in future versions. Planned:
- **An accessory mount:** a deck or rail with M2 bosses, carried by the frame, not the board, so modules bolt to the structure and the board stays isolated on its dampers;
- **A camera mount** at the front, angled, with a protected cable path to the board's camera connector;
- **Cable routing and strain relief:** clips and zip-tie slots so no cable pulls on a connector;
- **Mount positions placed for balance**, so modules sit close to the centre of gravity;
- **Updated checks and simulation with modules fitted:** clearances to props and board, weight, balance and thrust margin;
- **Prop guard attachment points** on the motor tubes;
- **An option for 8520 motors**, for more payload margin. The tube sizes already follow `MOTOR_D`, see [TOLERANCES.md](TOLERANCES.md).

If you need a specific module supported, open an issue with the module, its weight and dimensions, and where its connector plugs in. That decides what goes into the next version.
