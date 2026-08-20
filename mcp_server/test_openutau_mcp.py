"""
Self-test script for Modern OpenUtau MCP Server via stdio JSON-RPC 2.0.
"""

import subprocess
import json
import os
import sys

server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")


def send_rpc(proc, method, params=None, req_id=1):
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()
    resp_line = proc.stdout.readline()
    return json.loads(resp_line)


def run_tests():
    print("=== STARTING MODERN OPENUTAU MCP SERVER SELF-TEST ===")
    proc = subprocess.Popen(
        [sys.executable, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 1. Test initialize
    init_res = send_rpc(proc, "initialize", req_id=1)
    server_name = init_res["result"]["serverInfo"]["name"]
    version = init_res["result"]["serverInfo"]["version"]
    print(f"[TEST 1/5] Initialize: {server_name} v{version}")
    assert server_name == "openutau-mcp-server"

    # 2. Test tools/list
    tools_res = send_rpc(proc, "tools/list", req_id=2)
    tools = tools_res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    print(f"[TEST 2/5] Tools Discovered ({len(tools)}): {', '.join(tool_names)}")
    assert len(tools) == 5

    # 3. Test openutau_build_ustx
    sample_tracks = [
        {
            "name": "Lead Vocal",
            "singer": "Kasane Teto [UTAU]",
            "phoneticizer": "OpenUtau.Core.DefaultPhoneticizer",
            "notes": [
                {"lyric": "す", "pitch": 71, "ticks": 480, "vel": 110},
                {"lyric": "の", "pitch": 74, "ticks": 480, "vel": 115},
                {"lyric": "う", "pitch": 76, "ticks": 960, "vel": 120}
            ]
        }
    ]
    build_res = send_rpc(proc, "tools/call", {
        "name": "openutau_build_ustx",
        "arguments": {
            "title": "Snowgrave_Weird_Route",
            "bpm": 128.0,
            "tracks_config": sample_tracks,
            "output_ustx_path": "export/test_project.ustx"
        }
    }, req_id=3)
    b_data = json.loads(build_res["result"]["content"][0]["text"])
    print(f"[TEST 3/5] openutau_build_ustx: Created '{b_data.get('title')}' with {b_data.get('total_notes')} notes at {b_data.get('ustx_path')}")
    assert b_data.get("status") == "success"

    # 4. Test openutau_inspect_project
    inspect_res = send_rpc(proc, "tools/call", {
        "name": "openutau_inspect_project",
        "arguments": {"ustx_path": "export/test_project.ustx"}
    }, req_id=4)
    i_data = json.loads(inspect_res["result"]["content"][0]["text"])
    print(f"[TEST 4/5] openutau_inspect_project: Version = {i_data.get('ustx_version')}, Tracks = {i_data.get('tracks_count')}, Notes = {i_data.get('total_notes')}")
    assert i_data.get("status") == "success"

    # 5. Test openutau_synthesize_preview
    notes = [
        {"lyric": "す", "pitch": "B4", "ticks": 480, "vel": 110},
        {"lyric": "の", "pitch": "D5", "ticks": 480, "vel": 115},
        {"lyric": "う", "pitch": "E5", "ticks": 960, "vel": 120}
    ]
    synth_res = send_rpc(proc, "tools/call", {
        "name": "openutau_synthesize_preview",
        "arguments": {"notes_list": notes, "bpm": 128.0, "output_path": "export/test_preview.wav"}
    }, req_id=5)
    s_data = json.loads(synth_res["result"]["content"][0]["text"])
    print(f"[TEST 5/5] openutau_synthesize_preview: Duration = {s_data.get('duration_sec')}s, Peak = {s_data.get('peak')}")
    assert s_data.get("status") == "success"

    proc.stdin.close()
    proc.terminate()
    print("\n=== ALL 5 OPENUTAU MCP SERVER TESTS PASSED WITH 100% SUCCESS! ===")


if __name__ == "__main__":
    run_tests()
