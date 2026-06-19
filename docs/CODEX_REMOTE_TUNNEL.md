# Codex Remote Tunnel Setup

在实验室服务器（`/home/zc/wmt26`）上运行 OpenAI Codex CLI，并通过 Windows 本机 Clash 代理访问 OpenAI。

实际链路：

```text
服务器 Codex -> 服务器 127.0.0.1:17890 -> SSH 反向隧道 -> Windows Clash 127.0.0.1:7897 -> OpenAI
```

## Windows 端（本机）

在 PowerShell 中运行：

```powershell
ssh -N -T WMT-codex-tunnel
```

该窗口必须保持打开。它会将服务器上的 `127.0.0.1:17890` 反向转发到本机 Clash 混合代理 `127.0.0.1:7897`。

## 服务器端

只测试代理是否可用：

```bash
codex-proxy-test
```

启动 Codex：

```bash
codex-wmt
```

可以像普通 `codex` 一样传递参数：

```bash
codex-wmt --help
```

## 为什么不会影响 Claude Code

代理变量只在 `codex-wmt` 和 `codex-proxy-test` 进程内部设置，不会写入 `.bashrc` 或其他 shell 启动文件。Claude Code 在独立的终端中运行，不继承这些变量，因此仍使用原来的 API 环境。

## 正确习惯

- Claude Code 和 Codex 使用不同的终端。
- 不要在运行 Claude Code 的终端里手动 `export` Codex 代理变量。
- 不要让 Claude Code 和 Codex 同时修改同一个项目文件。

## 故障排查

如果 `codex-proxy-test` 失败，请检查：

1. Windows 上运行 `ssh -N -T WMT-codex-tunnel` 的 PowerShell 窗口是否仍然打开。
2. Windows 上 Clash Verge 是否正在运行，且混合代理端口为 `127.0.0.1:7897`。
3. 服务器上 `127.0.0.1:17890` 是否被其他进程占用。
