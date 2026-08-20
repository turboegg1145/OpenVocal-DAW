"""
Self-test script for UTAU MCP Server via stdio JSON-RPC.
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
    print("=== STARTING UTAU MCP SERVER SELF-TEST ===")
    proc = subprocess.Popen(
        [sys.executable, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 1. Test initialize
    init_res = send_rpc(proc, "initialize", req_id=1)
    print("[TEST 1/4] Initialize:", init_res["result"]["serverInfo"]["name"], init_res["result"]["serverInfo"]["version"])
    assert init_res["result"]["serverInfo"]["name"] == "utau-mcp-server"

    # 2. Test tools/list
    tools_res = send_rpc(proc, "tools/list", req_id=2)
    tools = tools_res["result"]["tools"]
    print(f"[TEST 2/4] Tools Listed: {len(tools)} tools ({', '.join(t['name'] for t in tools)})")
    assert len(tools) == 5

    # 3. Test tool: utau_inspect_voicebank
    vb_res = send_rpc(proc, "tools/call", {"name": "utau_inspect_voicebank", "arguments": {}}, req_id=3)
    text = vb_res["result"]["content"][0]["text"]
    data = json.loads(text)
    print(f"[TEST 3/4] utau_inspect_voicebank: Total Aliases = {data.get('total_aliases')}, WAVs = {data.get('total_wav_samples')}")

    # 4. Test tool: utau_render_phrase
    notes = [
        {"lyric": "す", "pitch": 71, "ticks": 480, "vel": 110},
        {"lyric": "の", "pitch": 74, "ticks": 480, "vel": 115},
        {"lyric": "う", "pitch": 76, "ticks": 960, "vel": 120}
    ]
    phrase_res = send_rpc(proc, "tools/call", {
        "name": "utau_render_phrase",
        "arguments": {"notes_list": notes, "bpm": 128.0, "output_path": "mcp_test_phrase.wav"}
    }, req_id=4)
    p_data = json.loads(phrase_res["result"]["content"][0]["text"])
    print(f"[TEST 4/4] utau_render_phrase: Duration = {p_data.get('duration_sec')}s, Peak = {p_data.get('peak')}")
    assert p_data.get("status") == "success"

    proc.stdin.close()
    proc.terminate()
    print("\n=== ALL 4 UTAU MCP SERVER TESTS PASSED PERFECTLY! ===")

if __name__ == "__main__":
    run_tests()
