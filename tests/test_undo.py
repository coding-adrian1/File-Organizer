from organizer.core import plan_organization, apply_plan
from organizer.manifest import write_manifest, latest_manifest, undo_manifest


def test_undo_restores_files_to_original_location(tmp_path):
    (tmp_path / "photo.jpg").write_text("data")
    results = apply_plan(plan_organization(tmp_path))
    write_manifest(tmp_path, results)

    manifest = latest_manifest(tmp_path)
    undo_results = undo_manifest(manifest)

    assert undo_results[0].status == "moved"
    assert (tmp_path / "photo.jpg").exists()
    assert not (tmp_path / "Images" / "photo.jpg").exists()


def test_undo_skips_files_that_moved_again_since(tmp_path):
    (tmp_path / "photo.jpg").write_text("data")
    results = apply_plan(plan_organization(tmp_path))
    write_manifest(tmp_path, results)

    # Simulate the user manually moving the organized file elsewhere.
    moved_file = tmp_path / "Images" / "photo.jpg"
    moved_file.rename(tmp_path / "Images" / "renamed.jpg")

    manifest = latest_manifest(tmp_path)
    undo_results = undo_manifest(manifest)

    assert undo_results[0].status == "skipped"


def test_latest_manifest_returns_none_when_no_history(tmp_path):
    assert latest_manifest(tmp_path) is None


def test_manifest_file_is_consumed_after_undo(tmp_path):
    (tmp_path / "photo.jpg").write_text("data")
    results = apply_plan(plan_organization(tmp_path))
    manifest_path = write_manifest(tmp_path, results)

    undo_manifest(manifest_path)
    assert not manifest_path.exists()
