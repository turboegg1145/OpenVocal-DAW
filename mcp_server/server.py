"""
OpenVocal-DAW: OpenUtau MCP Server (JSON-RPC 2.0 over Stdio)
Provides standardized tools for OpenUtau (.ustx) vocal generation, multi-track assembly,
neural DiffSinger expression curve tuning, and acoustic synthesis.
"""

import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openutau_tools import (
    tool_openutau_build_ustx,
    tool_openutau_inspect_project,
    tool_openutau_tune_expression,
    tool_openutau_convert_blueprint,
    tool_openutau_synthesize_preview
)

SERVER_INFO = {
    "name": "openutau-mcp-server",
    "version": "2.0.0",
    "description": "Modern OpenUtau (.ustx) Project Generation, DiffSinger Tuning & Vocal Production MCP Server"
}

TOOLS_MANIFEST = [
    {
        "name": "openutau_build_ustx",
        "description": "Build a native modern OpenUtau project file (.ustx) with multi-track layout, phoneticizers, and singer bindings.",
        "inputSchema": {
            "type": "object",
            "required": ["title", "bpm", "tracks_config", "output_ustx_path"],
            "properties": {
                "title": {"type": "string", "description": "Song project title"},
                "bpm": {"type": "number", "description": "Tempo in BPM"},
                "tracks_config": {
                    "type": "array",
                    "description": "List of track dicts: [{'name': 'Lead', 'singer': 'Kasane Teto [UTAU]', 'notes': [...]}]",
                    "items": {"type": "object"}
                },
                "output_ustx_path": {"type": "string", "description": "Output path for the .ustx YAML file"}
            }
        }
    },
    {
        "name": "openutau_inspect_project",
        "description": "Inspect and parse an existing OpenUtau .ustx project file, returning tracks, singers, notes, and metadata.",
        "inputSchema": {
            "type": "object",
            "required": ["ustx_path"],
            "properties": {
                "ustx_path": {"type": "string", "description": "Path to the .ustx project file"}
            }
        }
    },
    {
        "name": "openutau_tune_expression",
        "description": "Configure expression curves for DiffSinger/neural voices (Dynamics dyn, Tension tns, Breathiness bre) and vibrato.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dynamics_points": {"type": "array", "description": "Time-value points for Dynamics curve"},
                "tension_points": {"type": "array", "description": "Time-value points for Tension curve"},
                "breathiness_points": {"type": "array", "description": "Time-value points for Breathiness curve"},
                "vibrato_depth": {"type": "integer", "default": 25, "description": "Vibrato depth in cents"},
                "vibrato_period": {"type": "integer", "default": 175, "description": "Vibrato period in ticks"}
            }
        }
    },
    {
        "name": "openutau_convert_blueprint",
        "description": "Convert an entire song_blueprint.json into a clean, ready-to-open OpenUtau .ustx project.",
        "inputSchema": {
            "type": "object",
            "required": ["blueprint_path", "output_ustx_path"],
            "properties": {
                "blueprint_path": {"type": "string", "description": "Path to song_blueprint.json"},
                "output_ustx_path": {"type": "string", "description": "Output path for the .ustx project"}
            }
        }
    },
    {
        "name": "openutau_synthesize_preview",
        "description": "Acoustically synthesize a vocal preview WAV directly from notes with 25ms cosine-squared crossfading.",
        "inputSchema": {
            "type": "object",
            "required": ["notes_list"],
            "properties": {
                "notes_list": {
                    "type": "array",
                    "description": "Array of note dicts: [{'lyric': 'す', 'pitch': 71, 'ticks': 480, 'vel': 100}]",
                    "items": {"type": "object"}
                },
                "bpm": {"type": "number", "default": 128.0, "description": "Tempo in BPM"},
                "output_path": {"type": "string", "default": "export/openutau_preview.wav", "description": "Output WAV path"}
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
            if tool_name == "openutau_build_ustx":
                res = tool_openutau_build_ustx(
                    title=args["title"],
                    bpm=args["bpm"],
                    tracks_config=args["tracks_config"],
                    output_ustx_path=args["output_ustx_path"]
                )
            elif tool_name == "openutau_inspect_project":
                res = tool_openutau_inspect_project(args["ustx_path"])
            elif tool_name == "openutau_tune_expression":
                res = tool_openutau_tune_expression(
                    dynamics_points=args.get("dynamics_points"),
                    tension_points=args.get("tension_points"),
                    breathiness_points=args.get("breathiness_points"),
                    vibrato_depth=args.get("vibrato_depth", 25),
                    vibrato_period=args.get("vibrato_period", 175)
                )
            elif tool_name == "openutau_convert_blueprint":
                res = tool_openutau_convert_blueprint(
                    blueprint_path=args["blueprint_path"],
                    output_ustx_path=args["output_ustx_path"]
                )
            elif tool_name == "openutau_synthesize_preview":
                res = tool_openutau_synthesize_preview(
                    notes_list=args["notes_list"],
                    bpm=args.get("bpm", 128.0),
                    output_path=args.get("output_path", "export/openutau_preview.wav")
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
