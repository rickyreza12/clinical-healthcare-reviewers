from backend.policy.indexer import load_chunks, source_fingerprint


def test_policy_chunk_fingerprint_is_stable_and_changes_with_content(tmp_path):
    chunk_file = tmp_path / "chunks.jsonl"
    chunk_file.write_text('{"chunk_id":"sop-01","text":"policy"}\n', encoding="utf-8")

    chunks = load_chunks(chunk_file)
    assert source_fingerprint(chunks) == source_fingerprint(chunks)
    assert source_fingerprint(chunks) != source_fingerprint([{**chunks[0], "text": "changed"}])
