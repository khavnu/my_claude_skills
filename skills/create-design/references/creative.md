# Creative reference — signature moments, divergence, guardrails

Load for any *expressive* decision (SKILL.md › Workflow › 1a–1b). Structural
screens don't need it: there, convention wins.

## Contents
1. What creativity is for · 2. Finding the signature moment · 3. Divergence
techniques · 4. Expressive levers by medium · 5. Guardrails · 6. Presenting options

---

## 1. What creativity is for
- The goal is **memorable and still usable**, not "different". A bold idea
  that slows a frequent task is a regression, whatever it looks like.
- **Novelty budget:** spend it in one place per feature, the signature moment.
  Everything around it stays familiar, so the moment reads as intentional
  (Jakob's law protects the rest; Von Restorff makes the one odd thing stand out).
- **Floor vs. ceiling:** popularity research tells you what users expect (the
  floor). Award winners and best-in-class apps show what delights (the
  ceiling). Design to the floor, then add one ceiling idea.

## 2. Finding the signature moment
Ask, in order, and write down the answers in the brief:
1. **What is the emotional peak of this feature?** (finishing a song in Sing,
   the drop kicking in, finding a forgotten favourite). The signature goes there.
2. **What does the user physically do at that moment?** (drag, hold, sing,
   watch). The signature should *respond to that action*, not decorate a
   static state.
3. **What does the content give for free?** (artwork colors, beat, loudness,
   lyrics timing, waveform). Content-driven ideas are unique per song, so they
   never get boring and need no extra assets.
4. **Can it be described in one sentence a user would repeat to a friend?**
   ("the knobs glow with the bass"). If not, it is too subtle or too complex.

## 3. Divergence techniques (use 1–2 per Bold thumbnail)
| Technique | How | Example (music app) |
|---|---|---|
| Metaphor mining | List 5 physical objects tied to the task; borrow one *behaviour*, not the skin | DJ deck: a knob that springs back; vinyl: drag to scrub with inertia; cassette: rewinding shows the tape |
| Constraint flip | Take a "must" and invert it | "EQ needs 5–10 bands" → one 2-D pad (x = bass↔treble, y = warmth) |
| Input change | Same goal, different gesture | Vertical drag instead of circular rotation; tilt; voice; long-press to preview |
| Content as material | Let the data shape the UI | Band curve tinted from the artwork; layout density follows song tempo |
| Time as a dimension | The screen changes over the session | Visualizer calms down during a sleep timer; the screen dims as the song ends |
| Exaggerate one property | Push size, motion or color of ONE element far past the norm | A huge single knob as the hero; the play button morphs into the waveform |
| Remove the obvious | Delete the most expected element and solve the gap | No "Save" button: presets auto-save with an undo history |
| Cross-domain borrow | Copy a pattern from another category | A fitness-ring style progress for "songs sung this week" |

Rules: a Bold thumbnail must name the assumption it breaks. Two techniques at
once is the limit, or the idea stops being readable.

## 4. Expressive levers by medium
- **Motion (strongest):** M3 Expressive springs (spatial for movement, effects
  for color/opacity), shape morphing (circle ↔ squircle ↔ wave), continuity
  between screens (the cover flies into Now Playing). Duration 200–500 ms for
  the peak, never on a frequent action's critical path.
- **Haptics and sound:** a tick per step on a knob, a soft thud at the end of
  a drag, a click when a preset snaps. Cheap, felt rather than seen, and they
  survive reduced-motion settings.
- **Shape:** one signature shape (a wave edge, a cut corner, a pill that
  breathes) reused in 2–3 places makes the app recognizable without a logo.
- **Color:** content-derived tints (`principles.md` §8), a single glow that
  reacts to audio. Glow counts toward the accent budget.
- **Type:** emphasized display weight for one hero number or title per screen
  (M3 Expressive "emphasized" styles).
- **Copy:** a voice for empty states and celebrations ("No songs yet: your
  playlist is waiting for its first hit"). Errors stay plain.

## 5. Guardrails (the creative layer passes the same gate)
- **Reduced motion:** every animated signature has a still equivalent (an
  instant state change, a color shift) when "Remove animations" is on.
- **Disabled / unsupported:** what the moment looks like when the data or
  hardware is missing (no artwork, effect not supported, silence).
- **Every theme mode and both widths:** check at 320 and 412+ dp and in each
  color mode (WMusi: 4.16 Theme modes). A glow tuned for one accent can vanish
  on another.
- **Frequency:** a moment seen 50 times a day must be ≤ 300 ms and skippable;
  only rare moments (first launch, finishing a song in Sing) may run long.
- **Accessibility:** custom controls (knobs, pads) expose standard semantics
  (slider, adjustable) and a non-gesture path (buttons or TalkBack actions).
- **Performance:** audio-reactive effects read a precomputed or throttled
  signal (≤ 30 fps). Never per-frame allocation on the UI thread.

## 6. Presenting options to the user
- 3 thumbnails side by side (Safe / Stretch / Bold), same content, grey boxes
  + the idea only. Each with one line: *gains* · *risks* · *effort* (S/M/L).
- State your recommendation and why, then wait. Mixing is fine ("Stretch
  layout + Bold's knob gesture").
- After the pick, record in the repo docs: the chosen direction, the rejected
  ones and why. The next session must not redo the divergence.
