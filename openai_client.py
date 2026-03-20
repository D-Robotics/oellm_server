import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List


def build_payload(model: str, prompt: str, system: str, stream: bool, temperature: float, top_p: float) -> Dict[str, Any]:
    messages: List[Dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    return {
        "model": model,
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "top_p": top_p,
    }


def post_json(url: str, payload: Dict[str, Any]):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    return urllib.request.urlopen(req, timeout=600)


def do_non_stream(base_url: str, payload: Dict[str, Any]) -> int:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    try:
        with post_json(url, payload) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code}")
        try:
            print(e.read().decode("utf-8", errors="ignore"))
        except Exception:
            pass
        return 1
    except Exception as e:
        print(f"Request failed: {e}")
        return 1

    try:
        obj = json.loads(body)
    except Exception:
        print("Invalid JSON response:")
        print(body)
        return 1

    try:
        answer = obj["choices"][0]["message"]["content"]
    except Exception:
        print("Unexpected response:")
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return 1

    print(answer)
    return 0


def do_stream(base_url: str, payload: Dict[str, Any]) -> int:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    try:
        with post_json(url, payload) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    print()
                    return 0
                try:
                    obj = json.loads(data)
                except Exception:
                    continue

                if "error" in obj:
                    print("\nServer error:")
                    print(json.dumps(obj, ensure_ascii=False, indent=2))
                    return 1

                try:
                    delta = obj["choices"][0]["delta"].get("content", "")
                except Exception:
                    delta = ""
                if delta:
                    print(delta, end="", flush=True)
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code}")
        try:
            print(e.read().decode("utf-8", errors="ignore"))
        except Exception:
            pass
        return 1
    except Exception as e:
        print(f"Request failed: {e}")
        return 1

    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple OpenAI-compatible chat client")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Server base URL")
    parser.add_argument("--model", default="oellm-local", help="Model name")
    parser.add_argument("--prompt", required=True, help="User prompt")
    parser.add_argument("--system", default="", help="Optional system prompt")
    parser.add_argument("--stream", action="store_true", help="Use SSE streaming mode")
    parser.add_argument("--temperature", type=float, default=1.0, help="Sampling temperature")
    parser.add_argument("--top-p", type=float, default=1.0, help="Sampling top_p")
    args = parser.parse_args()

    payload = build_payload(
        model=args.model,
        prompt=args.prompt,
        system=args.system,
        stream=args.stream,
        temperature=args.temperature,
        top_p=args.top_p,
    )

    if args.stream:
        return do_stream(args.base_url, payload)
    return do_non_stream(args.base_url, payload)


if __name__ == "__main__":
    sys.exit(main())

