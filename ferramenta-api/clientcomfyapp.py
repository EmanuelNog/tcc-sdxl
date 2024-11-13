import argparse
import pathlib
import sys
import time

import requests

OUTPUT_DIR = pathlib.Path("/tmp/comfyui")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def main(args: argparse.Namespace):
    url = f"https://{args.modal_workspace}--comfy-ui-api-comfyui-api{'-dev' if args.dev else ''}.modal.run/"
    data = { "prompt": args.prompt }
    #if args.prompt is None: #has bug didn't care to fix
    #    data = { "prompt": "demo"}
    
    print(f"Sending request to {url} with prompt: {data['prompt']}")
    print("Waiting for response...")
    start_time = time.time()
    res = requests.post(url, json=data)
    if res.status_code == 200:
        end_time = time.time()
        print(
            f"Image finished generating in {round(end_time - start_time, 1)} seconds!"
        )
        filename = OUTPUT_DIR / f"{slugify(args.prompt[0:-4])}.png"
        filename.write_bytes(res.content)
        print(f"saved to '{filename}'")
    else:
        if res.status_code == 404:
            print(f"Workflow API not found at {url}")
        res.raise_for_status()


def parse_args(arglist: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--modal-workspace",
        type=str,
        required=False,
        default="emanuelnog",
        help="Name of the Modal workspace with the deployed app. Run `modal profile current` to check.",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=False,
        help="Prompt for the image generation model.",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="use this flag when running the ComfyUI server in development mode with `modal serve`",
    )

    return parser.parse_args(arglist[1:])


def slugify(s: str) -> str:
    return s.lower().replace(" ", "-").replace(".", "-").replace("/", "-")[:32]


if __name__ == "__main__":
    args = parse_args(sys.argv)
    main(args)
