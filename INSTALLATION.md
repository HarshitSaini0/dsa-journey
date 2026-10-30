# Installation & Setup Guide

This guide covers setting up your local environment to run the **DSA Forge Workbench** (`server.py`) and the AI-powered drafting agent.

---

## Prerequisites

* **Python 3.10+** (Recommended)
* A valid **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/apikey).

---

## Step-by-Step Installation

### 1. Clone the Repository
If you haven't already cloned or initialized your local repository, navigate to your workspace and open the project folder:
```bash
cd ~/Desktop/dsa-daily

```

### 2. Install Required Python Packages

Install the required dependencies (`google-genai` and `requests`) using pip:

```bash
python3 -m pip install google-genai requests

```

### 3. Configure Your Environment Secrets

Create a `.env` file in the root directory of your repository to securely store your Gemini API key:

```bash
touch .env

```

Open `.env` in your text editor and add your API key:

```env
GEMINI_API_KEY=AIzaSyYourActualAPIKeyHere

```

*(Note: Your `.env` file is protected by `.gitignore` and will never be committed to GitHub).*

---

## Running the Workbench

### Start the Local Bridge Server

Run the unified bridge server from your repository root:

```bash
python3 server.py

```

### Access the Web UI

Open your browser and navigate to:

```text
http://localhost:8080

```

* **Tab 01 (Solutions Index):** Browse your solved problems, filter by pattern or review status (`🔴`/`🟡`/`🟢`), inspect code files, and push updates to GitHub with one click.
* **Tab 02 (New Entry Forge):** Paste a LeetCode URL and your solution code, click **Generate AI Draft**, review/edit `problem_draft.txt`, and click **Forge Solution** to automatically create your patterned folder, populate your reflection docstring + code, and update `README.md`.
