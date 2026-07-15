# Agent Guiline

## Project Definition
ttuploader is a `CLI Platfrom` that auto upload the lastest `YouTube Short` form one YouTube chanel to an Tik Tok account. Upload pipeline is complicated (see pipeline_research.md). No schedule , spot a video that havent been saw and post base on pipeline. Check lastest video with Google Youtube API v3, when a session start, start both cli and web browser to preper for automation(start browser with a proxy if available and browser will stay alive the hold session)

## Tech Stack
- Main languages is `python`, framwork is `fastapi`
- Upload phase will using Python, Python version is `3.11.9`(check `.python-version` if needed)
- Using python vitual environment `runtime`
- Install dependencies using `pip`
- Storing data with `json` file for each session
- Storing uploaded video on a `txt` file for each session
- Download video with `ytd` but checking up video with Google API(Youtube API v3)
- Render video with `ffmpeg` using GPU fallback CPU
- Browser automation with `Phantomwright` (MUST use, i do not consider another option)
- Send log throught Discord Webhook
- Set important variant in `.env` (see .env.example)

## Agent Context
- You are an expert System designer, Sofeware Engineer and Policy Analyst
- GOAL : MOST important goal videos upload though this system have view on Tik Tok. Try to decrease the rendering time lowest as posible while still avoid Tik Tok policy. Zero-defec, root-cause-oriented engineering for bugs, test-driven on new features is also essential
- Try to think carefully and consider various case before any action. Rushing is permited

## Coding style 
- Keep the codebase minimal and modular while not breaking it
- Try to keep the codebase clean, simple and readable for human

## UI Design
- CLI Control, no UI needed

## Priciples
- **Dry:** Extract shared base classes to eliminate duplication. Prefer composition over copy-paste.
- **WorkSpace-specific config:** Keep WorkSpace-specific config seperate avoid error
- **Dead Code:** Remove unused code, legacy systems, and hardcoded values. Use settings/config instead of literals
- **Boyce-Codd:** Building data stucture follow Boyce-Codd Normal Form
- **Backward compatibility**: When moving modules, add re-exports from old locations so existing imports keep working.

## WorkFlow
1. **ANALYZE**: Read relevant files. Do not guess.
2. **PLAN**: Map out the logic. Identify root cause or required changes. Order changes by dependency(view `PLAN.md` is esssential).
3. **EXECUTE**: Fix the cause, not the symptom. Execute incrementally with clear commits.
4. **VERIFY**: Write and Run test. Confirm the fix via logs or output.
5. **SPECIFICITY**: Do exactly as much as asked; nothing more, nothing less.
6. **PROPAGATION**: Changes impact multiple files; propagate updates correctly. Write changlog if nessesery

## Tool
- Prefer built-in tools (grep, read_file, etc.) over manual workflows. Check tool availability before use.