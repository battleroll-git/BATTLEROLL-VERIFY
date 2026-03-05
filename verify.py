#!/usr/bin/env python3
import hashlib
import hmac
import json
import sys
import argparse
from decimal import Decimal, ROUND_HALF_UP


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def hmac_sha256(key, message):
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()


def compute_client_seed(bet_ids):
    return sha256(":".join(sorted(bet_ids)))


def compute_result(server_seed, client_seed, nonce, green_chance):
    result_hash = hmac_sha256(server_seed, f"{client_seed}:{nonce}")
    rnd = int(result_hash[:8], 16) % 1_000_000
    threshold = int((green_chance * 1_000_000 / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    winner = "green" if rnd < threshold else "blue"
    winning_number = (Decimal(rnd) / 1_000_000 * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
  
    return winner, str(winning_number), result_hash


def verify(data):
    pf = data["provably_fair"]
    result = data["result"]

    server_seed = pf["server_seed"]
    client_seed = pf["client_seed"]
    nonce = pf["nonce"]
    green_chance = Decimal(result["green_team_chance"])

    hash_ok = sha256(server_seed) == pf["server_seed_hash"]

    client_seed_ok = None
    if "bet_ids_sorted" in data:
        client_seed_ok = compute_client_seed(data["bet_ids_sorted"]) == client_seed

    winner, winning_number, _ = compute_result(server_seed, client_seed, nonce, green_chance)
    result_ok = winner == result["winner"] and winning_number == result["winning_number"]

    return {
        "hash_ok": hash_ok,
        "client_seed_ok": client_seed_ok,
        "result_ok": result_ok,
        "winner": winner,
        "winning_number": winning_number,
    }


def fmt(ok):
    if ok is None:
        return "—"
    return "✅" if ok else "❌"


def print_result(r):
    print()
    print(f"Server Seed Hash {fmt(r['hash_ok'])}")
    print(f"Client Seed {fmt(r['client_seed_ok'])}")
    print(f"Результат {fmt(r['result_ok'])}  winner={r['winner']}, number={r['winning_number']}")
    all_ok = r["hash_ok"] and r["result_ok"] and (r["client_seed_ok"] is not False)
    print()
    print(f"Итог:{'✅ ЧЕСТНО' if all_ok else '❌ ПРОВЕРКА НЕ ПРОЙДЕНА'}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Provably Fair верификация")
    parser.add_argument("file", nargs="?", help="JSON файл из Battle Info")
    parser.add_argument("--server-seed")
    parser.add_argument("--server-seed-hash")
    parser.add_argument("--client-seed")
    parser.add_argument("--nonce", type=int)
    parser.add_argument("--green-chance")
    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)
        print_result(verify(data))

    elif all([args.server_seed, args.server_seed_hash, args.client_seed,
              args.nonce is not None, args.green_chance]):
        green_chance = Decimal(args.green_chance)
        hash_ok = sha256(args.server_seed) == args.server_seed_hash
        winner, winning_number, _ = compute_result(
            args.server_seed, args.client_seed, args.nonce, green_chance
        )
        print_result({
            "hash_ok": hash_ok,
            "client_seed_ok": None,
            "result_ok": None,
            "winner": winner,
            "winning_number": winning_number,
        })

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
