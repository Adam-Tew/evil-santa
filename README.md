# Evil Santa — a CTFd theme

Christmas has been stolen. Every flag a team captures brings a bit of the
Christmas spirit back. At 0% the site is coal-grey; by 90% Christmas is saved
and there's a secret ending at 100%.

Built on the CTFd 3.8 `core` theme.

## Install

1. Copy this `evil-santa` folder into `CTFd/CTFd/themes/`.
2. Go to **Admin → Config → Theme**, choose `evil-santa`, and save.

## How the spirit system works

| Piece | Where | What it does |
|---|---|---|
| Garland | Along the bottom of the navbar | Same grey-to-green as the wreath; its bulbs light up in a scattered order |
| Falling snow | Every page | Slow grey ash at 0% becomes bright snow with coloured sparkles at 90% |
| Navbar / meter art | Navbar and footer | Your image, grey and dim at 0% and in full colour at 90%; the tint goes from black to red (navbar) and black to pine green (footer) |
| Spirit meter | Footer, on every page | Shows real progress: `floor(solved × 100 / total)` |
| Wreath | Hangs from the navbar | Goes from grey to green, and its 12 bulbs light up stage by stage |
| Ignite the Spirit! | Appears above the meter | Shows up when a new stage is earned. Each click plays the sparks and unlocks **one** stage |
| Scene + story card | Challenge board | Full-screen artwork and chapter text for the current stage |
| Site colours | Every page | Navbar, borders and accents follow `--spirit` (0 → 1) |

- **Teams vs solo:** CTFd's `solved_by_me` already counts the whole team's
  solves in team mode and the player's own solves in user mode. No setup needed.
- **Rounding:** always rounds down. With 45 challenges, 40 solves is 88% and
  41 solves is 91%.
- **Never goes backwards:** releasing new challenges lowers the raw percentage,
  but a stage that has already been earned stays unlocked.
- **Each player gets the ceremony:** unlocked stages are saved per browser, so
  every teammate presses the button on their own device.
- Unsolved challenges are lumps of coal (3 shapes) that smoulder on hover.
  Solved challenges become wrapped presents with a ribbon, bow and gift tag.
  Each challenge always gets the same paper, picked from 8 designs. A fresh
  solve pops with sparkles as the coal turns into a present.
- The theme is dark only. The light/dark toggle has been removed.

### Stages

| % | Chapter | Scene |
|---|---|---|
| 0 | Prologue: A Coal-Black Christmas | Grey town square, sad townsfolk holding coal, castle on the hill |
| 10 | Ch.1: This Way to Santa's Castle | Five kids march off with their candy weapons past an ominous sign |
| 20 | Ch.2: Candy Bomb Away! | Leo fires the gingerbread bazooka at the gate; elves on the walls |
| 30 | Ch.3: Cookies at the Gate | Gate destroyed; a cookie and a lights lasso turn elves good |
| 40 | Ch.4: The Hall of Antlers | Castle corridor, kids and good elves against evil reindeer |
| 50 | Ch.5: The Standoff | Throne room: Evil Santa, Rudolph and Mrs. Claus face the heroes |
| 60 | Ch.6: Mayhem! | Coal, burnt cookies and candy everywhere |
| 70 | Ch.7: The Spirit Wins | Rudolph lassoed, Mrs. Claus gets a good cookie, Santa turns good |
| 80 | Ch.8: The Midnight Ride | Sleigh flies over town decorating house by house |
| 90 | Finale: Christmas Is Saved! | Town square: presents and happy townsfolk |
| 100 | Secret: Krampus Is Not Amused | Krampus sulks on the mountain above the bright town |

The story text lives at the top of `static/spirit/spirit.js` (`STAGES`).

## Optional admin settings

Go to **Admin → Config → Theme → Theme Settings** and paste in JSON:

```json
{
  "spirit_total": 45,
  "spirit_season": "2026",
  "spirit_scene_ext": "webp",
  "spirit_ui_ext": "webp",
  "spirit_snow": true
}
```

- `spirit_total`: a fixed count to divide by. Set this if some challenges are
  hidden behind prerequisites, because hidden challenges are missing from the
  player's list and would otherwise inflate the percentage.
- `spirit_season`: change this value to reset everyone's saved ceremonies,
  for example after test runs before the real event.
- `spirit_scene_ext`: optional. The theme detects the scene file type by itself (webp, png, jpg, then svg), so this is only needed to force one.
- `spirit_ui_ext`: optional. Each UI image's file type is detected separately, so you can replace them one at a time.
- `spirit_scene_fit`: `contain` (default) shows the whole scene in a candy-cane frame; `cover` fills the screen and crops the edges.
- `spirit_snow`: set to `false` to turn off the falling snow.

## Replacing the art

Put the images in `static/spirit/scenes/`, named `stage-000`, `stage-010` …
`stage-100` with the extension set above.

- 16:9, at least 1920×1080, WebP at about 80% quality (aim for under 400 KB each).
- The bottom of the image stays visible (`background-position: center bottom`).
- **Kids and allies on the left, evil on the right.**
- Keep the middle calm. Challenge cards cover roughly the centre 70% of the
  screen, so put the main action in the outer 20% on each side and along the
  bottom.
- The theme already darkens the art a little so text stays readable.
- `tools/make_placeholders.py` regenerates the placeholder SVGs.

### UI images (`static/spirit/ui/`)

| File | Used for | Shape |
|---|---|---|
| `navbar.*` | Navbar background, repeats sideways | Wide seamless band, e.g. 1536×256 (shown about 56 px tall) |
| `meter.*` | Spirit meter background, repeats sideways | Wide seamless band |
| `coal.*` | Fill texture for unsolved challenges | Square seamless tile, shown at 160 px |
| `wrap-0` … `wrap-7.*` | Wrapping papers for solved challenges | Square seamless tile, shown at 120 px |

Use full-colour art. The theme makes it grey itself at low spirit.
Ribbon colours are set per paper in `spirit.css` (`.wrap-N { --ribbon }`).
`tools/make_ui_tiles.py` regenerates the placeholder tiles.

## Testing helpers (browser console)

```js
EvilSanta.preview(7)   // show a stage without saving (0-10)
EvilSanta.reset()      // forget this browser's saved ceremonies
```

`prefers-reduced-motion` is respected: no sparks or pulsing, only a simple fade.
