from app import rag


def test_builds_store_from_example_when_local_cv_is_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "cv_example.txt").write_text("Example CV content", encoding="utf-8")

    monkeypatch.setattr(rag, "maak_embeddings", lambda chunks: [[1.0, 0.0] for _ in chunks])

    store = rag.laad_of_bouw_store()

    assert store[0]["chunk"] == "Example CV content"
    assert (data_dir / "cv_store.json").exists()