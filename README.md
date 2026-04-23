# fastapichallenge

The same small **FastAPI** project is kept in three folders to compare different open models (local inference with [LM Studio](https://lmstudio.ai/)) and an [OpenCode](https://opencode.ai/)–driven build.

## `tasks.md` (the challenge brief)

Each app folder is meant to be produced from a **single spec**: the **`tasks.md`** file (requirements, API shape, tests, and UI expectations). You hand that file to an open-weights model and ask it to **implement the project**; this repo’s three copies are different models’ **responses to the same `tasks.md`**. Use your workflow (e.g. LM Studio + OpenCode) to run the model against that spec and build out the code.

| Folder | Model (challenge run) |
|--------|------------------------|
| `fastapiexample-qwen27b/` | Qwen 2.7B |
| `fastapiexample-qwen36bmoe/` | Qwen 3 6B MoE |
| `fastapiexample-gemma4-26b-a4b/` | Gemma 4 26B A4B |

## Run

Choose one directory, then:

```bash
cd fastapiexample-qwen27b
pip install -r requirements.txt
python main.py
```

- App: <http://localhost:8000>
- Logins: `admin` / `admin123` or `user` / `user123` (see that folder’s `auth.py`)

**Tests:** `pytest test_main.py -v`  
**Docker:** from the same app folder, `docker compose up --build`

OpenAPI docs: <http://localhost:8000/docs> (when the server is running)
