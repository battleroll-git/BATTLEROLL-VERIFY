# Provably Fair - легит чек

Скрипт для самостоятельной верификации результатов игры.  


## Зачем это нужно

Каждый раунд завершается публикацией `server_seed` - случайного числа, которое сервер сгенерировал **до** начала ставок. До этого момента был виден только его хеш (`server_seed_hash`). Это значит: сервер физически не мог подобрать seed под нужный результат - хеш уже был зафиксирован.

Этот скрипт позволяет убедиться в этом самостоятельно, не доверяя никому на слово.


## Как работает алгоритм

```
client_seed = SHA-256( sorted(bet_ids).join(':') )
result_hash = HMAC-SHA256( server_seed, client_seed + ':' + nonce )

rnd = int(result_hash[:8], 16) % 1_000_000
winner = green если rnd меньше чем green_chance * 10_000
```


**Три шага проверки:**

1. `SHA-256(server_seed)` должен совпасть с `server_seed_hash`, опубликованным до раунда - значит seed не менялся
2. `client_seed` воспроизводится из ID ставок участников - результат зависит от игроков, а не только от сервера
3. Итоговый победитель и выигрышное число вычисляются заново и сравниваются с записанными


## Использование

**Python 3.8+, зависимостей нет.**

```bash
# Из файла Battle Info (скачивается кнопкой в Legit Check)
python verify.py battle_42.json

# Вручную
python verify.py \
  --server-seed      2d433a24b7cc... \
  --server-seed-hash 5aa93a7836f3... \
  --client-seed      e9b582f9fd14... \
  --nonce            10 \
  --green-chance     76.92
```


**Вывод:**

```
  Server Seed Hash ✅
  Client Seed ✅
  Результат ✅ winner=green, number=49.60

  Итог: ✅ ЧЕСТНО
```


## Формат JSON-файла

```json
{
  "provably_fair": {
    "server_seed":      "2d433a24...",
    "server_seed_hash": "5aa93a78...",
    "client_seed":      "e9b582f9...",
    "result_hash":      "cbff24eb...",
    "nonce":            10
  },
  "result": {
    "winner":            "green",
    "winning_number":    "49.60",
    "green_team_chance": "76.92"
  },
  "bet_ids_sorted": ["0e0472c8-...", "14a1e702-...", "..."]
}
```
