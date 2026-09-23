# WebMetaBench

WebMetaBench 是面向复杂交互式前端的黑盒测试评测数据集。模型根据项目的英文 checklist，自主浏览网页、执行交互并收集视觉证据，报告不满足需求的行为。数据同时适用于评估浏览器 Agent，以及研究前端生成结果的多模态元评估。

## 发布内容

本次发布包含 **120 个单缺陷样本、19 个多缺陷样本，涉及 43 个原始前端项目**。样本集合以 `dataset/single_defect.json` 和 `dataset/multi_defect.json` 为准；一个前端项目可以对应多个样本。

- Git 仓库保存样本清单、英文评测 prompt/checklist、独立金标、部署脚本和 Docker 构建配方。
- 编译好的网页资源按前端项目分别打包，上传到**本仓库的 GitHub Release**，不另建数据仓库，也不把大型二进制文件塞入 Git 历史。
- 每个项目包包含清单引用的原版、单缺陷版以及适用的多缺陷版。同一项目内引用同一个静态目录的版本只打包一次；不同样本的原版/修改版对应关系保持原样。
- 不上传实验使用的 Codex/Claude Code 本体、`agent_home`、Python/npm 环境、浏览器安装目录、调用轨迹或 API 密钥。
- 提供的是已构建网页产物，不是完整的上游源码仓库；部署不需要重新运行各项目的 `npm install` 或前端编译。

项目数据、金标和上游资源的许可说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。公开可访问不等于可任意再授权，请保留项目内的原始版权声明。

## 目录结构

```text
dataset/
  manifest.json          # 项目包下载地址、分片大小和 SHA-256
  single_defect.json     # 单缺陷样本及网页版本映射
  multi_defect.json      # 多缺陷样本及网页版本映射
  prompts/               # 模型可见的英文 prompt，包含完整 checklist
  annotations/           # 金标；仅供评分端使用，不能提供给被测 Agent
  provenance.json        # 项目来源信息
scripts/
  download_projects.py
  build_image.py
  serve.py
  install_runtime.sh
docker/
  Dockerfile.projects
  Dockerfile.runtime
projects/                # 下载解压后产生，不提交到 Git
```

## 下载网页资源

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

下载脚本支持中断续传、SHA-256 校验和跳过已经安装的同版本项目。单个压缩包过大时会分片，脚本自动合并解压。下载缓存位于 `downloads/`，解压结果位于 `projects/`。

## 默认方式：构建一整个大镜像

**我们提供将全部网页项目及其各版本构建成“一整个大镜像”的脚本。** 下载全部资源后执行：

```bash
python3 scripts/build_image.py --all --tag webmetabench-projects:local
```

该镜像只包含网页资源和静态服务程序，**不包含 Codex、Claude Code 或模型 API 客户端环境**。更新 Harness 不需要重新打包这些网页资源。

镜像包含全部项目，但每个服务实例只公开一个选定样本的一个版本。以下示例部署一个单缺陷样本：

```bash
docker run --rm --name webmetabench-page \
  --read-only --cap-drop=ALL --security-opt=no-new-privileges \
  -p 127.0.0.1:8080:8080 \
  webmetabench-projects:local \
  --sample martinlaxenaire__portfolio-2025__defect_01__requirements_v1 \
  --variant defect
```

浏览地址为 `http://127.0.0.1:8080/`。将 `--variant defect` 改为 `--variant gold` 可部署该样本对应的原版。多缺陷样本同样通过 `--sample` 选择，不需要另一套镜像。

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

后续发布可替换 manifest 指向的 Release。更新仓库后重新运行下载脚本，只获取发生变化的项目；镜像由用户选择何时重新构建。

英文 prompt 原样保留，不附加“必有一个缺陷”等额外提示。`dataset/annotations/single_defect.json` 保存单缺陷金标，`dataset/annotations/multi_defect.json` 保存多缺陷的独立金标点及其 requirement ID。一个 requirement 可能包含多个金标点，不能只按 R 编号去重计分。

断点续跑应由使用者的评测 runner 根据样本 ID、项目包摘要、prompt 摘要、模型及 Harness 配置识别结果；不要仅凭同名结果文件就跳过更新后的样本。

## 发布范围

本次工作是整理并发布现有数据和部署配方，未重新运行全部网页交互实验，也未在发布过程中重新构建并测试全部 Docker 镜像。网页产物、样本方向及英文评测输入沿用现有正式数据；不要将打包成功等同于在所有新环境上的浏览器兼容性保证。
