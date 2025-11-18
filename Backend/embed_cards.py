#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate embeddings for selected fields in card_data/cardgorilla_top100_detailed.json
and store them locally as JSONL.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pymilvus import model  # requires `pip install "pymilvus[model]"`


CARD_JSON = Path("card_data/cardgorilla_top100_detailed.json")
OUTPUT_JSONL = Path("card_data/card_embeddings.jsonl")


def load_cards() -> List[dict]:
    data = json.loads(CARD_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Card JSON should contain a list of records.")
    return data


def extract_field_texts(card: dict) -> dict:
    benefits = card.get("description_text", {}).get("benefits_text", []) or []
    benefits_joined = "; ".join(benefits)
    return {
        "name": card.get("name", "") or "",
        "issuer": card.get("issuer", "") or "",
        "event_text": card.get("event_text", "") or "",
        "benefits_text": benefits_joined,
    }


def main():
    cards = load_cards()
    embedding_model = model.DefaultEmbeddingFunction()

    # Prepare flattened payload for batch embedding
    field_keys = ["benefits_text", "name", "event_text", "issuer"]
    flat_inputs = []
    index_map = []  # (card_idx, field_key)
    field_texts_per_card = []

    for idx, card in enumerate(cards):
        texts = extract_field_texts(card)
        field_texts_per_card.append(texts)
        for key in field_keys:
            flat_inputs.append(texts[key])
            index_map.append((idx, key))

    embeddings = embedding_model.encode_documents(flat_inputs)

    # Assign embeddings to each card/field
    field_embeddings = [
        {key: None for key in field_keys} for _ in range(len(cards))
    ]
    for (card_idx, key), vector in zip(index_map, embeddings):
        field_embeddings[card_idx][key] = vector.tolist()

    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSONL.open("w", encoding="utf-8") as f:
        for card, texts, emb_map in zip(cards, field_texts_per_card, field_embeddings):
            benefits_list = card.get("description_text", {}).get("benefits_text", []) or []
            benefits_joined = "; ".join(benefits_list)
            row = {
                "rank": card.get("rank"),
                "name": texts["name"],
                "issuer": texts["issuer"],
                "event_text": texts["event_text"],
                "benefits_text": benefits_list,
                "benefits_text_joined": benefits_joined,
                "embeddings": emb_map,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"✅ Generated {len(cards)} embeddings to {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()

