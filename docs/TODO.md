# TODO — deferred

Items deferred from the DB-fixes round — the speaker cabinet UI.
`tg_bot/` only (no model changes, no migrations).

## Networking — persist favorites & viewed profiles

The networking flow (`tg_bot/handlers/networking.py`) currently stores
**favorites** and **skipped/viewed** profile ids in `context.user_data`
(keys `net_favorites`, `net_skipped`). This is session-only, in-memory
state: it is lost on bot restart and not shared across devices.

To make networking durable, add models + migrations:

1. A `NetworkingFavorite` model (viewer → profile, unique together) so a
   user's favorites survive restarts and can be listed back to them.
2. A `NetworkingView` (or `NetworkingSkip`) model to remember which
   profiles a viewer has already seen, so the feed does not replay the
   same cards on every visit.
3. A "favorites" screen — today favoriting only increments a counter on
   the card button (`⭐ В избранное (N)`); the favorited contacts are not
   retrievable until a list screen exists.
4. Move the `net_*` `context.user_data` logic in `networking.py` behind
   `metup_bot/services/networking.py` calls once the models land.

## Speaker cabinet — start/end talk buttons

The speaker cabinet handler (`tg_bot/handlers/speaker_cabinet.py`) is
stub-only: `enter`/`start_talk`/`end_talk` each call
`main_menu.show_stub`. The data layer is already in place:
`metup_bot/services/talks.py` exposes `get_speaker_talk`,
`get_active_talk`, `start_talk`, `end_talk` (the latter two enforce the
per-event "only one active talk" invariant), and callbacks
`SPK_START`/`SPK_END` are already wired in
`tg_bot/handlers/state_machines.py`. The UI is what's missing.

Behaviour to implement (see `docs/PythonMeetup.md`, speaker scenarios,
plus the "one active talk per event" rule):

1. Add `get_speaker_cabinet(...)` to `tg_bot/keyboards.py` — an
   `InlineKeyboardMarkup` showing **Start** (`SPK_START`) when the talk
   is `planned` and not blocked, **End** (`SPK_END`) when `active`, and
   no action button when `finished`. Always include a Back/Menu button.
   When another talk in the same event is already active, suppress Start
   and surface a notice.
2. Implement `enter`/`start_talk`/`end_talk` in
   `tg_bot/handlers/speaker_cabinet.py`. Fetch the speaker's talk via
   `talks.get_speaker_talk(tg_id)`, re-render the cabinet in place via
   `edit_current`. Wrap `talks.start_talk`/`end_talk` in try/except
   `ValueError` so "another talk is already active" shows a friendly
   message instead of crashing.
3. Add Russian strings to `tg_bot/strings.py` (cabinet text, the
   active-conflict message, the finished message). Follow the existing
   Russian wording.
4. Leave `list_questions`/`show_question`/`mark_answered` as stubs —
   out of scope for this round.

Notes:

- Everything stays within `State.MAIN_MENU`; no new state and no routing
  changes (the callbacks are already registered).
- The handler can use `Talk.State.*` directly — the model choices landed
  in the DB-fixes round.
