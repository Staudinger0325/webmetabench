# WebMetaBench

WebMetaBench 是面向复杂交互式前端的黑盒测试评测数据集。模型根据项目的英文 checklist，自主浏览网页、执行交互并收集视觉证据，报告不满足需求的行为。数据同时适用于评估浏览器 Agent，以及研究前端生成结果的多模态元评估。

## 发布内容

WebMetaBench 包含 **120 个单缺陷样本、19 个多缺陷样本**。我们在 `dataset/single_defect.json` 和 `dataset/multi_defect.json` 中披露了样本的相关信息。其中，`dataset/multi_defect.json` 提供了每个多缺陷样本由哪些单缺陷样本合并而来。

此外，`dataset/prompts` 提供每个样本的评测输入（包含完整 checklist），`dataset/annotations` 提供对应的英文金标答案。

我们同时提供构建好的网页产物，以及各样本对应的原版和修改版源码快照，便于使用者从头安装依赖、编译。源码包保留项目代码、构建配置、锁文件及素材，不包含 Git 历史、已安装的依赖、本机缓存或私密环境变量。项目自身的中文内容保留；数据集新增的标注和元数据使用英文。

## 目录结构

```text
dataset/
  single_defect.json     # 单缺陷样本及网页版本映射
  multi_defect.json      # 多缺陷样本及网页版本映射
  prompts/               # 模型可见的英文 prompt，包含完整 checklist
  annotations/           # 金标；仅供评分端使用，不能提供给被测 Agent
  provenance.json        # 项目来源，以及静态资源包和源码包的下载地址
  build_recipes.json     # 各源码版本的工作目录、安装命令、构建命令和产物目录
scripts/
  download_projects.py
  build_sources.py
  build_image.py
  serve.py
  install_runtime.sh
docker/
  Dockerfile.projects
  Dockerfile.runtime
projects/                # 下载解压后产生，不提交到 Git
sources/                 # 按需下载的原版和修改版源码，不提交到 Git
```

## 快速开始

需要 Python 3.10+、`curl`；构建镜像另需可用的 Docker。

```bash
git clone https://github.com/Staudinger0325/webmetabench.git
cd webmetabench
python3 scripts/download_projects.py --all
```

也可以只下载一个项目：

```bash
python3 scripts/download_projects.py --project martinlaxenaire__portfolio-2025
```

下载脚本支持中断续传和跳过已经安装的同一发布版本，不进行内容哈希校验。单个压缩包过大时会分片，脚本自动合并解压。下载缓存位于 `downloads/`，静态产物解压到 `projects/`。

### 从源码安装依赖并重新编译

源码按项目独立打包，与静态产物分开下载：

```bash
# 下载全部原版、单缺陷版和多缺陷版源码
python3 scripts/download_projects.py --all --kind sources

# 或者只下载一个项目的源码
python3 scripts/download_projects.py --project martinlaxenaire__portfolio-2025 --kind sources

# 从源码构建指定样本的修改版，并写入对应的 projects/ 目录
python3 scripts/build_sources.py \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --variant defect
```

将 `--variant defect` 改为 `--variant gold` 可构建原版，改为 `--variant both` 可构建两版。多缺陷样本使用相同入口。批量构建示例：

```bash
python3 scripts/build_sources.py --all --variant both
```

构建命令逐项记录在 `dataset/build_recipes.json` 中，用户也可以进入对应的 `sources/` 目录手动执行。脚本会打印工作目录和命令，在 `outputs/build_logs/` 保存日志，并在成功后将产物复制到 `projects/`。覆盖已经存在的对应产物需要显式添加 `--replace`。

请安装 Node.js 22（AFFiNE 要求 22.12 及以上、低于 23）和 npm；需要 pnpm/Yarn 的项目通过配方指定的 `npx` 命令启动。原生依赖可能还需要 Python、编译工具及项目自身声明的 Rust 工具链。静态 HTML 项目不需要 npm 编译，直接复制源码资源即可。

Nuxt 等项目在生成过程中可能访问外部 CMS；源码中的环境变量模板需要按项目说明填写。源码快照和锁文件被保留，但远程数据及依赖服务可能变化，因此不承诺未来重新构建的字节结果与已发布产物完全一致。本次整理没有重新执行所有项目的编译。

### 多缺陷样本的组成

`dataset/multi_defect.json` 中每条样本的 `single_defect_components` 列出参与合并的单缺陷样本 ID、原始缺陷 ID、对应的 requirement ID 和类别；`source_single_sample_ids` 提供简洁的 ID 列表。合并关系来自最终多缺陷清单，而不是根据文件名猜测。具体金标仍位于 `dataset/annotations/multi_defect.json`。

### 如何构建统一的大镜像环境

我们论文的实验由于计算资源限制，采用统一构建大镜像的方式部署评测环境。下载全部资源后执行：

```bash
python3 scripts/build_image.py --all --tag webmetabench-projects:local
```

该镜像包含网页资源和静态服务程序，如果您需要更新 Harness，不需要重新打包这些资源。

镜像包含全部项目，但每个服务实例只公开一个选定样本的一个版本。以下示例部署一个单缺陷样本：

```bash
docker run --rm --name webmetabench-page \
  --read-only --cap-drop=ALL --security-opt=no-new-privileges \
  -p 127.0.0.1:8080:8080 \
  webmetabench-projects:local \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --variant defect
```

浏览地址为 `http://127.0.0.1:8080/`。将 `--variant defect` 改为 `--variant gold` 可部署该样本对应的原版。多缺陷样本同样可以通过 `--sample` 选择。

多个并发实例可以使用同一个镜像，各自选择样本并映射不同端口。Docker 共享只读镜像层，不需要为每个容器重新复制一份完整镜像。

### 可选方式：分别构建小镜像

**如果各位的实验环境支持，也可以自行构建独立的小镜像。** 脚本支持按项目或按样本筛选：

```bash
# 一个项目的小镜像，包含该项目被选入数据集的各版本
python3 scripts/build_image.py \
  --project martinlaxenaire__portfolio-2025 \
  --tag webmetabench-martin:local

# 一个样本的小镜像，仅包含该样本的原版和修改版
python3 scripts/build_image.py \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --tag webmetabench-sample:local
```

大镜像与小镜像使用相同的静态产物和样本映射，区别仅在于镜像包含的资源范围，不改变 checklist 或金标。

## 不使用 Docker 的部署方式

```bash
python3 scripts/serve.py \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --variant defect --host 127.0.0.1 --port 8080
```

每个实例指定不同端口即可并发部署。默认只绑定本机；同机评测不需要 SSH 转发。只有明确需要其他机器访问时才设置 `--host 0.0.0.0`，并自行配置访问控制。

服务支持 SPA 路由回退和视频 Range 请求，不提供目录列表，不暴露数据集金标目录。已有产物可能仍引用第三方远程字体、图片或服务；本发布并不承诺每个页面都能在完全断网时工作。

## Harness 与运行依赖：由使用者自行安装

**本仓库不分发我们实验时安装的 Harness 本体。** 使用者自行下载所需的 Claude Code/Codex 版本，并基于自己安装的版本运行评测或构建运行环境镜像。可以选用 `latest`，也可以显式固定版本。

### 直接安装

先准备 Node.js 22+、npm、Python 3.10+。在 Debian/Ubuntu 上安装浏览器、视频处理与基础字体依赖：

```bash
sudo apt-get update
sudo apt-get install -y chromium ffmpeg python3-venv fonts-liberation fonts-noto-cjk
```

然后安装 CLI 与模型调用/浏览器库：

```bash
bash scripts/install_runtime.sh
```

脚本等价于在本仓库忽略的 `.runtime/` 下执行：

```bash
python3 -m venv .runtime/python
.runtime/python/bin/pip install --upgrade pip
.runtime/python/bin/pip install litellm openai tqdm
npm install --prefix .runtime/node --no-save \
  @anthropic-ai/claude-code@latest @openai/codex@latest \
  playwright-core@latest @modelcontextprotocol/sdk@latest zod@latest
```

Claude Code 的 npm 安装属于兼容路径；其官方亦提供原生安装方式。用户可以按[官方安装文档](https://code.claude.com/docs/en/setup)安装，而不使用本脚本的 CLI 安装部分。Codex 安装参见[官方 CLI 文档](https://developers.openai.com/codex/cli/)。这些 CLI 需要用户自行登录或配置模型提供商凭据。

指定自己的版本：

```bash
CLAUDE_CODE_VERSION=latest CODEX_VERSION=latest \
LITELLM_VERSION=latest PLAYWRIGHT_VERSION=latest \
bash scripts/install_runtime.sh
```

将 `latest` 换为具体版本即可固定依赖。脚本记录已安装的 CLI 版本、npm 依赖和 Python 依赖；**`latest` 是安装时解析的版本，不会在每次评测前自动升级**。复现实验时应保存实际版本记录，不能把 `latest` 当作实验版本号。

这里的脚本只负责安装运行依赖，不包含历史实验中的私有 API 路由、增强 Agent 逻辑或自动评测 runner；安装 CLI 本身也不会自动配置浏览器 MCP。接入自选 Harness 时，应配置浏览器工具并提供对应样本的 `dataset/prompts/` 内容和部署 URL，不向被测 Agent 提供 `dataset/annotations/`。

### 基于使用者所选版本构建运行环境镜像

```bash
docker build -f docker/Dockerfile.runtime \
  --build-arg CLAUDE_CODE_VERSION=latest \
  --build-arg CODEX_VERSION=latest \
  --build-arg LITELLM_VERSION=latest \
  --build-arg PLAYWRIGHT_VERSION=latest \
  -t webmetabench-runtime:local .
```

这个 Dockerfile 在用户构建时下载 CLI、Chromium、FFmpeg、LiteLLM 等依赖；不会复制发布者的任何实验环境。它与网页资源镜像独立更新。凭据应在运行时配置，不要写入 Dockerfile 或镜像层。

## 关于隔离与实验环境

- 大镜像中的 HTTP 服务只公开当前选定的网页目录，但**这不等于 Agent 在文件系统上也无法读取其他项目**。不能把 Agent 放进同一个大资源镜像后就宣称实现了样本隔离。
- 需要黑盒评测时，应让 Agent 运行在独立环境，仅通过浏览器访问当前网页服务；不要向其挂载全部资源、金标或源码目录，也不要挂载 Docker socket。
- 小镜像能进一步缩小可访问资源范围。容器网络的样本间隔离、Agent 工具权限和外部网络策略仍需结合使用者的实验环境配置。
- 若云平台仅支持构建镜像、不能在开发机内运行容器，可将自行构建的镜像推到平台支持的镜像仓库，并用该镜像创建开发机；或者使用上述非 Docker 静态服务方式。不能把可执行 `docker build` 等同于可执行 `docker run`。
- 本仓库没有预打包 GPU 驱动。GPU 浏览器渲染依赖宿主机驱动、容器运行时及浏览器启动参数；仅安装 Chromium 不代表已经启用 GPU。

## 数据更新与评分端数据

后续发布会更新 `dataset/provenance.json` 中的下载地址和发布版本。更新仓库后重新运行下载脚本，只获取尚未安装的发布版本；镜像由用户选择何时重新构建。

英文 prompt 原样保留，不附加“必有一个缺陷”等额外提示。`dataset/annotations/single_defect.json` 保存单缺陷金标，`dataset/annotations/multi_defect.json` 保存多缺陷的独立金标点及其 requirement ID。一个 requirement 可能包含多个金标点，不能只按 R 编号去重计分。

断点续跑应由使用者的评测 runner 根据样本 ID、数据发布版本、模型及 Harness 配置识别结果；不要仅凭同名结果文件就跳过更新后的样本。

## 发布范围

本次工作是整理并发布现有数据和部署配方，未重新运行全部网页交互实验，也未在发布过程中重新构建并测试全部 Docker 镜像。网页产物、样本方向及英文评测输入沿用现有正式数据；不要将打包成功等同于在所有新环境上的浏览器兼容性保证。
