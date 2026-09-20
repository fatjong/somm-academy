#!/usr/bin/env python3
"""
產生預錄語音包
==============================================================
讀 voice-lines.json，用 zh-TW-HsiaoChenNeural 把每一句合成成音檔，
輸出到 voice/ 目錄，並寫出 voice/manifest.json。

這是在你自己電腦上跑的一次性工具，不會被部署到網站上。
網站本身仍然是純前端，只是多了一個 voice/ 資料夾。

用法
--------------------------------------------------------------
    pip install edge-tts
    python make-voice.py

    # 只重做某幾句
    python make-voice.py sys_intro low off

    # 想改語氣
    python make-voice.py --rate="-4%" --pitch="+10Hz"

輸出
--------------------------------------------------------------
    voice/sys_intro.mp3
    voice/low.mp3
    ...
    voice/manifest.json

把整個 voice/ 資料夾放到 index.html 旁邊即可。網頁會自動偵測並改用
預錄檔，找不到才退回瀏覽器語音。

關於 edge-tts
--------------------------------------------------------------
edge-tts 走的是 Microsoft Edge 朗讀功能的介面，免費、不需金鑰，但屬於
非公開介面，微軟隨時可能變動或停用。正式課程長期使用的話，建議改用
Azure Speech 官方服務（見檔案末端的 azure_synth 函式），穩定且有 SLA。
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINES_FILE = HERE / "voice-lines.json"
OUT_DIR = HERE / "voice"


def load_lines():
    if not LINES_FILE.exists():
        sys.exit(f"找不到 {LINES_FILE}")
    data = json.loads(LINES_FILE.read_text(encoding="utf-8"))
    lines = data.get("lines") or []
    if not lines:
        sys.exit("voice-lines.json 裡沒有 lines")
    return data, lines


async def synth_one(text, path, voice, rate, pitch):
    import edge_tts

    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(str(path))


async def main_async(args):
    data, lines = load_lines()
    voice = args.voice or data.get("voice") or "zh-TW-HsiaoChenNeural"
    rate = args.rate or data.get("rate") or "-4%"
    pitch = args.pitch or data.get("pitch") or "+10Hz"

    wanted = set(args.ids) if args.ids else None
    todo = [l for l in lines if not wanted or l["id"] in wanted]
    if not todo:
        sys.exit("指定的 id 都不在 voice-lines.json 裡")

    OUT_DIR.mkdir(exist_ok=True)
    print(f"語音 {voice}　語速 {rate}　音調 {pitch}")
    print(f"輸出到 {OUT_DIR}\n")

    ok, fail = 0, 0
    for i, line in enumerate(todo, 1):
        lid, text = line["id"], line["text"].strip()
        out = OUT_DIR / f"{lid}.mp3"
        if out.exists() and not args.force and not wanted:
            print(f"  [{i:2}/{len(todo)}] {lid:<12} 已存在，略過")
            continue
        try:
            await synth_one(text, out, voice, rate, pitch)
            size = out.stat().st_size
            if size < 500:
                raise RuntimeError(f"檔案只有 {size} bytes，可能失敗")
            print(f"  [{i:2}/{len(todo)}] {lid:<12} {size/1024:6.1f} KB")
            ok += 1
        except Exception as e:
            print(f"  [{i:2}/{len(todo)}] {lid:<12} 失敗：{e}")
            fail += 1

    manifest = {
        "voice": voice,
        "rate": rate,
        "pitch": pitch,
        "format": "mp3",
        "lines": [{"id": l["id"], "text": l["text"]} for l in lines],
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    print(f"\n完成：成功 {ok}，失敗 {fail}")
    print(f"已寫出 {OUT_DIR / 'manifest.json'}")
    if fail:
        print("\n失敗多半是網路問題，重跑一次通常就好（已完成的會略過）。")
    else:
        print("\n把整個 voice/ 資料夾和 index.html 一起推上去即可。")


def azure_synth(text, out_path, key, region,
                voice="zh-TW-HsiaoChenNeural", rate="-4%", pitch="+10Hz"):
    """
    Azure Speech 官方版本。需要金鑰，但穩定且有服務保證。
    金鑰只在你自己電腦上使用，不會進到網站裡。

        pip install requests
        azure_synth("測試", Path("voice/test.mp3"), "你的金鑰", "eastasia")
    """
    import requests

    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-TW">'
        f'<voice name="{voice}"><prosody rate="{rate}" pitch="{pitch}">{text}</prosody>'
        f"</voice></speak>"
    )
    r = requests.post(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "somm-tutor",
        },
        data=ssml.encode("utf-8"),
        timeout=30,
    )
    r.raise_for_status()
    Path(out_path).write_bytes(r.content)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="產生預錄語音包")
    ap.add_argument("ids", nargs="*", help="只重做這幾個 id，留空表示全部")
    ap.add_argument("--voice", help="覆寫語音名稱")
    ap.add_argument("--rate", help="語速，例如 -4%%")
    ap.add_argument("--pitch", help="音調，例如 +10Hz")
    ap.add_argument("--force", action="store_true", help="已存在也重新產生")
    args = ap.parse_args()

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        sys.exit("請先安裝：pip install edge-tts")

    asyncio.run(main_async(args))
