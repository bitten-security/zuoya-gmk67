# Zuoya GMK67 Control

Open-source replacement for the vendor driver of the **Zuoya GMK67** keyboard (USB `05AC:024F`).

> Unofficial. Not affiliated with Zuoya. Made by reverse engineering; **use at your own risk**.
> English first, Português abaixo.

![icon](gmk67/icon.png)

## Features

- **Effects**: effect, color (or rainbow), brightness, speed, direction.
- **Per-key lighting** with a virtual keyboard (click, Ctrl-click, drag to select).
- **Key functions**: any key can become another key or a media function (volume, play/pause, calculator…).
- **Macros**: text macros (`Hello{ENTER}`) bound to a key. The keyboard memory is small (174 bytes).
- **WIN / MAC layout** (swaps Win and Alt).
- **Profiles**, English / Português, system tray, start with Windows.
- **6 themes**: Dark, Light, Midnight, Neon, Forest, Sunset (selector in the header).
- Knob shows the Windows volume and mute state; connection indicators (USB / 2.4G) with the USB polling rate (read-only).

### Limits

- Lighting, keys and macros work **over the USB cable only** (the 2.4G dongle does not accept the commands).
- Battery level cannot be read; the polling rate cannot be changed.
- Writing key functions replaces the whole key table. The vendor app also rewrites its own table when it starts.

## Install (Windows)

Download `GMK67Control-Setup.exe` (installer) or `GMK67Control.exe` (portable) from the
[Releases](../../releases) page. macOS builds are experimental (see below).

## Install (macOS, experimental)

The macOS port builds in CI (`.github/workflows/release.yml`) as `GMK67Control-mac-arm64.dmg`
(Apple silicon) and `-x86_64.dmg` (Intel). **It has never been run on a real Mac by the author.** The app is only ad-hoc
signed, so macOS blocks the first launch: right-click → Open, or `xattr -dr com.apple.quarantine "GMK67 Control.app"`.
macOS may ask for **Input Monitoring** permission (System Settings → Privacy & Security) to talk to the keyboard.
Not available on macOS: USB polling-rate display. Volume display uses `osascript`. Please open an issue with results.

## Run from source

```bash
pip install -r requirements.txt
python run.py
```

Build the portable exe: `powershell -File build_exe.ps1`. Protocol notes: [docs/PROTOCOL.md](docs/PROTOCOL.md).

## License

GPL-3.0, see [LICENSE](LICENSE).

---

## Português

Substituto de código aberto para o driver oficial do teclado **Zuoya GMK67**.

> Não oficial e sem vínculo com a Zuoya. Feito por engenharia reversa; **use por sua conta e risco**.

**Recursos:** efeitos de luz (cor, brilho, velocidade, direção), luz por tecla com teclado virtual, funções por
tecla (inclusive multimídia), macros de texto, layout WIN/MAC, perfis, idioma PT/EN, bandeja do sistema, início com o
Windows, 6 temas de cores e o knob mostrando o volume do Windows.

**Limites:** luz, teclas e macros só funcionam pelo **cabo USB**; a bateria não pode ser lida e a taxa de polling não
pode ser alterada. Gravar funções de tecla substitui a tabela inteira de teclas do teclado.

**Instalar:** baixe o instalador na página de [Releases](../../releases). Versão para Mac em breve.
