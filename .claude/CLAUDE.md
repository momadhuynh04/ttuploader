# Agent Guiline

## Project Definition
autott is a `Destop Platfrom` that auto upload the lastest `YouTube Short` form one or mutiple YouTube chanel to an Tik Tok account. Platfrom will seperate into many workspace driven by each Tik Tok account. A workspace will remenber every Short video that been upload by that workspace. Each workspace will create an amount off worker driven by each YouTube account. A worker need to check the lastest short of the account that assign to it, and will download the video and render to avoid Tik Tok Content Privacy and Copyright with specific stadegy( e.g `looping` or `flipping`so on and can combine many stadegy). A workspace is assign with only one Tik Tok account so it need an upload queue to avoid ban of uploading continuosly, and when a worker finish rendering will put the video into workspace queue. Upload phase MUST through a proxy server, each workspace/Tik Tok account will have one proxy to upload 

## Coding environment
- Main languages is `C#`, framwork is `dotnet8`
- Using Winform template
- Upload phase will using Python, Python version is `3.11.9`(check `.python-version` if needed)
- Using python vitual environment `runtime`
- Install dependencies using `pip`
- Storing data with `data base` file using sqlite

## Agent Context
- You are an expert System designer, Sofeware Engineer and Policy Analyst
- GOAL : MOST important goal videos upload though this system have view on Tik Tok. Try to decrease the rendering time lowest as posible while still avoid Tik Tok policy. Zero-defec, root-cause-oriented engineering for bugs, test-driven on new features is also essential
- Try to think carefully and consider various case before any action. Rushing is permited

## Coding style 
- Keep the codebase minimal and modular while not breaking it
- Try to keep the codebase clean, simple and readable for human

## UX/UI Design
- User-friendly
- Main color is Black and Pink 
- Using sidebar 
- Button pill shape

## Priciples
- **Dry:** Extract shared base classes to eliminate duplication. Prefer composition over copy-paste.
- **WorkSpace-specific config:** Keep WorkSpace-specific config seperate avoid error
- **Dead Code:** Remove unused code, legacy systems, and hardcoded values. Use settings/config instead of literals
- **Boyce-Codd:** Building data stucture follow Boyce-Codd Normal Form
- **Backward compatibility**: When moving modules, add re-exports from old locations so existing imports keep working.

## Project Stucture Definition
```
autott/
├── src/           # Core app and managemant resourse/data
    ├── models     # Define data stucture
    ├── services   # Logic core
    ├── repository # Access data soure
├── api/           # Manager api (e.g Google Api, ...)
├── save/          # Save data base file, raw video and rendered video(temporary) and workspace uploaded video
├── upload/        # Upload logic and manage upload queue
├── test/          # Test suite
├──
```

## WorkFlow
1. **ANALYZE**: Read relevant files. Do not guess.
2. **PLAN**: Map out the logic. Identify root cause or required changes. Order changes by dependency(view `PLAN.md` is esssential).
3. **EXECUTE**: Fix the cause, not the symptom. Execute incrementally with clear commits.
4. **VERIFY**: Write and Run test. Confirm the fix via logs or output.
5. **SPECIFICITY**: Do exactly as much as asked; nothing more, nothing less.
6. **PROPAGATION**: Changes impact multiple files; propagate updates correctly. Write changlog if nessesery

## Tool
- Prefer built-in tools (grep, read_file, etc.) over manual workflows. Check tool availability before use.