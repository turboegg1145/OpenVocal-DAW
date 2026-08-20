"""
OpenVocal-DAW: UTAU MCP Server (JSON-RPC 2.0 over Stdio)
Standard Model Context Protocol Server providing native virtual singer vocal synthesis tools.
"""

import sys
import json
import os

# Import tools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utau_tools import (
    tool_inspect_voicebank,
    tool_render_note,
    tool_render_phrase,
    tool_tune_pitch_curve,
    tool_render_full_track
)

SERVER_INFO = {
    "name": "utau-mcp-server",
    "version": "1.0.0",
    "description": "UTAU & OpenUtau Virtual Singer Synthesis & Acoustic Tuning MCP Server"
}

TOOLS_MANIFEST = [
    {
        "name": "utau_inspect_voicebank",
        "description": "Inspect voicebank metadata, phoneme boundaries, oto.ini aliases, and timing parameters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "voicebank_dir": {"type": "string", "description": "Path to voicebank folder (defaults to Kasane Teto)"}
            }
        }
    },
    {
        "name": "utau_render_note",
        "description": "Synthesize a single vocal note with specific pitch, duration, and formant flags (Flags=g0/g-2).",
        "inputSchema": {
            "type": "object",
            "required": ["lyric", "pitch", "duration_ms"],
            "properties": {
                "lyric": {"type": "string", "description": "Phonetic lyric (e.g. 'あ', 'す', 'の')"},
                "pitch": {"type": ["integer", "string"], "description": "MIDI note number (e.g. 68) or tone string (e.g. 'G#4')"},
                "duration_ms": {"type": "integer", "description": "Note duration in milliseconds"},
                "velocity": {"type": "integer", "default": 100, "description": "Note velocity (0-127)"},
                "flags": {"type": "string", "default": "g0", "description": "UTAU engine formant flags (e.g. 'g0', 'g-2')"},
                "output_path": {"type": "string", "description": "Optional output WAV file path"}
            }
        }
    },
    {
        "name": "utau_render_phrase",
        "description": "Synthesize a connected vocal phrase with 25ms cosine-squared crossfading and beat grid timing.",
        "inputSchema": {
            "type": "object",
            "required": ["notes_list"],
            "properties": {
                "notes_list": {
                    "type": "array",
                    "description": "Array of note objects: [{'lyric': 'す', 'pitch': 71, 'ticks': 480, 'vel': 100}]",
                    "items": {"type": "object"}
                },
                "bpm": {"type": "number", "default": 128.0, "description": "Tempo in BPM"},
                "flags": {"type": "string", "default": "g0", "description": "Engine formant flag"},
                "output_path": {"type": "string", "default": "export/phrase.wav", "description": "Output WAV path"}
            }
        }
    },
    {
        "name": "utau_tune_pitch_curve",
        "description": "Generate micro-tuned pitch bend, portamento, and vibrato (VBR) parameters for expressive singing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pbs_ms": {"type": "integer", "default": -25, "description": "Pitch bend start time shift in ms"},
                "pbw_ms": {"type": "string", "default": "25,25", "description": "Pitch bend width in ms"},
                "pby_cents": {"type": "string", "default": "0,0", "description": "Pitch bend vertical cents offset"},
                "pbm_interpolation": {"type": "string", "default": "AA#", "description": "Curve interpolation Mode (s-curve/linear)"},
                "vbr_depth": {"type": "integer", "default": 160, "description": "Vibrato depth (cents)"},
                "vbr_period": {"type": "integer", "default": 25, "description": "Vibrato period/frequency"}
            }
        }
    },
    {
        "name": "utau_render_full_track",
        "description": "Compile an entire song blueprint (JSON) into a pristine 24-bit master vocal track.",
        "inputSchema": {
            "type": "object",
            "required": ["blueprint_path", "output_wav_path"],
            "properties": {
                "blueprint_path": {"type": "string", "description": "Path to song_blueprint.json"},
                "output_wav_path": {"type": "string", "description": "Output 24-bit WAV file path"},
                "flags": {"type": "string", "default": "g0", "description": "Engine formant flags"}
            }
        }
    }
]


def handle_rpc_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True}
                },
                "serverInfo": SERVER_INFO
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS_MANIFEST
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            if tool_name == "utau_inspect_voicebank":
                res = tool_inspect_voicebank(args.get("voicebank_dir"))
            elif tool_name == "utau_render_note":
                res = tool_render_note(
                    lyric=args["lyric"],
                    pitch=args["pitch"],
                    duration_ms=args["duration_ms"],
                    velocity=args.get("velocity", 100),
                    flags=args.get("flags", "g0"),
                    voicebank_dir=args.get("voicebank_dir"),
                    output_path=args.get("output_path")
                )
            elif tool_name == "utau_render_phrase":
                res = tool_render_phrase(
                    notes_list=args["notes_list"],
                    bpm=args.get("bpm", 128.0),
                    flags=args.get("flags", "g0"),
                    output_path=args.get("output_path", "export/phrase.wav")
                )
            elif tool_name == "utau_tune_pitch_curve":
                res = tool_tune_pitch_curve(
                    pbs_ms=args.get("pbs_ms", -25),
                    pbw_ms=args.get("pbw_ms", "25,25"),
                    pby_cents=args.get("pby_cents", "0,0"),
                    pbm=args.get("pbm_interpolation", "AA#"),
                    vbr_depth=args.get("vbr_depth", 160),
                    vbr_period=args.get("vbr_period", 25)
                )
            elif tool_name == "utau_render_full_track":
                res = tool_render_full_track(
                    blueprint_path=args["blueprint_path"],
                    output_wav_path=args["output_wav_path"],
                    flags=args.get("flags", "g0")
                )
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": f"Tool execution failed: {str(e)}"}
            }

    elif method == "notifications/initialized" or method == "ping":
        return None

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not supported: {method}"}
        }


def main():
    # Stdio loop for JSON-RPC 2.0
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            req = json.loads(line)
            resp = handle_rpc_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {str(e)}"}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
