# Contributing to PharmaGuard AI

Thank you for your interest in contributing to PharmaGuard AI!

## How to Contribute

### 1. Fork and Clone

```bash
git clone https://github.com/<your-username>/pharmaguard-ai.git
cd pharmaguard-ai
```

### 2. Create a Branch

Always create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Set Up the Environment

```bash
cd src
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

### 4. Make Your Changes

Follow the existing code style:
- Keep functions small and well-documented
- Add docstrings to all new functions and classes
- Use type hints where appropriate
- Follow the existing module structure

### 5. Test Locally

Run the full test suite before committing:

```bash
# From repository root
pytest tests/ -v
```

Run the Streamlit app to verify UI changes:

```bash
cd src
streamlit run app.py
```

### 6. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for Fisher's exact test alongside PRR"
```

Conventional commit prefixes:
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation change
- `test:` — test addition or modification
- `refactor:` — code refactoring
- `chore:` — maintenance tasks

### 7. Push and Open a Pull Request

```bash
git push origin feature/your-feature-name
```

Open a pull request on GitHub. Describe:
- What you changed and why
- How to test the change
- Any known limitations

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## Important Reminders

- **Never commit `.env` or any file containing real credentials**
- **Never add real patient data or real regulatory submissions**
- All data used must be synthetic or publicly available demonstration data
- Do not claim the tool makes clinical or regulatory decisions
- Preserve the official IBM hackathon template structure and validation files
