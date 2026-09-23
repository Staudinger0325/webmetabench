# WebMetaBench

WebMetaBench is a benchmark for black-box testing of complex interactive web applications. Given a project's English checklist, a model autonomously browses the website, performs interactions, and collects visual evidence to report behaviors that do not meet the requirements. The dataset supports both the evaluation of browser agents and research on multimodal meta-evaluation of generated web applications.

## Release Contents

WebMetaBench contains **120 single-defect samples and 19 multi-defect samples**. Sample information is provided in `dataset/single_defect.json` and `dataset/multi_defect.json`. The latter also identifies the single-defect samples combined to form each multi-defect sample.

In addition, `dataset/prompts` provides the evaluation input for each sample, including the complete checklist, while `dataset/annotations` provides the corresponding gold answers in English.

We provide both prebuilt web artifacts and source snapshots of the original and modified versions of each sample, allowing users to install dependencies and build from source. Source packages include project code, build configurations, lockfiles, and assets, but exclude Git history, installed dependencies, local caches, and private environment variables. Chinese content native to the projects is preserved; annotations and metadata added by the dataset are in English.

## Directory Structure

```text
dataset/
  single_defect.json     # Single-defect samples and web version mappings
  multi_defect.json      # Multi-defect samples and web version mappings
  prompts/              # Model-facing English prompts with complete checklists
  annotations/          # Gold answers for scoring only; do not expose to evaluated agents
  gold_videos.json       # Gold video archive URL and per-sample file index
  provenance.json       # Project origins and download URLs for static and source packages
  build_recipes.json    # Working directories, install/build commands, and output directories
scripts/
  download_projects.py
  build_sources.py
  build_image.py
  serve.py
  install_runtime.sh
docker/
  Dockerfile.projects
  Dockerfile.runtime
```

## Quick Start

Python 3.10+ and `curl` are required. Building container images also requires a working Docker installation.

```bash
git clone https://github.com/Staudinger0325/webmetabench.git
cd webmetabench
python3 scripts/download_projects.py --all
```

To try a single project, download it by its project ID:

```bash
python3 scripts/download_projects.py --project martinlaxenaire__portfolio-2025
```

### Install Dependencies and Rebuild from Source

Source code is packaged separately for each project and downloaded independently of the static artifacts:

```bash
# Download all original, single-defect, and multi-defect source versions
python3 scripts/download_projects.py --all --kind sources

# Or download the source code for a single project
python3 scripts/download_projects.py --project martinlaxenaire__portfolio-2025 --kind sources

# Build the modified version of a sample into its corresponding projects/ directory
python3 scripts/build_sources.py \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --variant defect
```

Replace `--variant defect` with `--variant gold` to build the unmodified original version, or with `--variant both` to build both versions. The same command supports multi-defect samples. To build all versions in a batch:

```bash
python3 scripts/build_sources.py --all --variant both
```

To overwrite existing build artifacts, explicitly add `--replace` to the command.

Before building from source, install Node.js 22, version 22.12 or later within the 22.x series, which includes npm. The build script installs dependencies and generates web artifacts according to each project's configuration; there is no need to install pnpm or Yarn manually. Static HTML projects do not require compilation: the script simply copies their pages and assets.

### Build a Single Combined Image

Due to resource constraints, our experiments deployed the evaluation environment using one combined image. After downloading all resources, run:

```bash
python3 scripts/build_image.py --all --tag webmetabench-projects:local
```

This image contains the web resources and a static server. Updating the agent harness does not require repackaging these resources.

The image contains all projects, but each server instance exposes only one version of a selected sample. The following example deploys a single-defect sample:

```bash
docker run --rm --name webmetabench-page \
  --read-only --cap-drop=ALL --security-opt=no-new-privileges \
  -p 127.0.0.1:8080:8080 \
  webmetabench-projects:local \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --variant defect
```

Open `http://127.0.0.1:8080/` in your browser. Replace `--variant defect` with `--variant gold` to deploy the corresponding original version.

Multiple concurrent instances can share the same image, each selecting a sample and mapping a different port.

### Build Separate Smaller Images

We also support building a separate, smaller image for each sample:

```bash
# A smaller image containing only the original and modified versions of one sample
python3 scripts/build_image.py \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --tag webmetabench-sample:local
```

## Gold Video Evidence

We provide 120 reference recordings, one for each single-defect sample, in the [gold-videos-v1 release](https://github.com/Staudinger0325/webmetabench/releases/tag/gold-videos-v1). The recordings are distributed as originally recorded, without re-encoding. These are recordings of the defective versions demonstrating the annotated behaviors, not recordings of the unmodified `gold` versions.

`dataset/gold_videos.json` maps each sample ID to its video file within the archive. Download and extract all recordings with:

```bash
mkdir -p downloads
curl --fail --location --continue-at - \
  https://github.com/Staudinger0325/webmetabench/releases/download/gold-videos-v1/webmetabench-gold-videos-v1.tar.gz \
  --output downloads/webmetabench-gold-videos-v1.tar.gz
tar -xzf downloads/webmetabench-gold-videos-v1.tar.gz -C downloads
```

The videos will be available at `downloads/gold_videos/<sample_id>.mp4`. They are reference evidence and should not be supplied to agents in the standard black-box evaluation.

This release contains single-defect recordings only. For multi-defect samples, `dataset/multi_defect.json` identifies the constituent single-defect samples; their recordings are not separate evidence captured from the combined multi-defect versions.

## Agent Harnesses and Runtime Dependencies: User Installation

This repository does not distribute the installed agent harnesses used in our experiments. Users can download their preferred versions and use those installations to run evaluations or build runtime images.

### Direct Installation

First, install Node.js 22+, npm, and Python 3.10+. On Debian/Ubuntu, install the browser, video-processing tools, and basic fonts:

```bash
sudo apt-get update
sudo apt-get install -y chromium ffmpeg python3-venv fonts-liberation fonts-noto-cjk
```

Then install the CLIs and libraries for model API calls and browser automation:

```bash
bash scripts/install_runtime.sh
```

The script is equivalent to running the following commands under `.runtime/`, which is ignored by this repository:

```bash
python3 -m venv .runtime/python
.runtime/python/bin/pip install --upgrade pip
.runtime/python/bin/pip install litellm openai tqdm
npm install --prefix .runtime/node --no-save \
  @anthropic-ai/claude-code@latest @openai/codex@latest \
  playwright-core@latest @modelcontextprotocol/sdk@latest zod@latest
```

Alternatively, follow the [official Claude Code installation guide](https://code.claude.com/docs/en/setup) or the [official Codex CLI documentation](https://developers.openai.com/codex/cli/) to install them yourself.

To specify versions:

```bash
CLAUDE_CODE_VERSION=latest CODEX_VERSION=latest \
LITELLM_VERSION=latest PLAYWRIGHT_VERSION=latest \
bash scripts/install_runtime.sh
```

Replace `latest` with explicit version numbers to pin dependencies.

### Build a Runtime Image

```bash
docker build -f docker/Dockerfile.runtime \
  --build-arg CLAUDE_CODE_VERSION=latest \
  --build-arg CODEX_VERSION=latest \
  --build-arg LITELLM_VERSION=latest \
  --build-arg PLAYWRIGHT_VERSION=latest \
  -t webmetabench-runtime:local .
```

This Dockerfile downloads the CLIs, Chromium, FFmpeg, LiteLLM, and other dependencies when users build the image.

## Dataset Updates and Scoring Data

The judge prompts used in our experiments are provided in the paper. Given the straightforward judging procedure, we have omitted this component from the repository; users can configure their own judge service. Our prompts achieve high judging accuracy, although occasional errors remain. Using models with stronger general reasoning capabilities may further improve accuracy.
