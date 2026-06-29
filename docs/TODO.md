# TODO — deferred

Items explicitly deferred from the admin-rewrite branch
(`metup_bot/admin.py` only — no model changes, no migrations).

## Talk state — model-level choices

`Talk.state` is a bare `CharField(max_length=20)`. The admin bridges this
with a form-level `TALK_STATE_CHOICES` + `TalkAdminForm`
(`metup_bot/admin.py`), and `services/talks.py` uses raw string literals
(`"planned"`, `"active"`, `"finished"`).

In the "fix models" round:

1. Add `class State(models.TextChoices)` to `Talk`, wire it onto the
   `state` field, generate + apply the migration.
2. Refactor `services/talks.py` to use `Talk.State.*` instead of the
   magic strings.
3. In `metup_bot/admin.py`: drop `TALK_STATE_CHOICES` and the explicit
   `ChoiceField` on `TalkAdminForm` (the model choices make the dropdown
   automatic). Keep `clean_state()` — the transition invariants still
   belong on the form.
4. Wire `TalkInline` (in `EventAdmin`) to use the model form so `state`
   renders as a dropdown and `clean_state()` invariants apply to inline
   edits too. Currently the inline renders `state` as free text with no
   validation, by deliberate deferral.
