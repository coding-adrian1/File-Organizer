from organizer.rename import plan_rename, apply_rename


def test_sequential_rename_pattern(tmp_path):
    (tmp_path / "b.jpg").write_text("x")
    (tmp_path / "a.jpg").write_text("x")

    plans = plan_rename(tmp_path, "photo_{n:03d}{ext}")
    names = [p.destination.name for p in plans]

    # sorted() means a.jpg comes first regardless of creation order
    assert names == ["photo_001.jpg", "photo_002.jpg"]


def test_rename_with_start_offset(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    plans = plan_rename(tmp_path, "img_{n}{ext}", start=10)
    assert plans[0].destination.name == "img_10.jpg"


def test_rename_preserves_original_name_placeholder(tmp_path):
    (tmp_path / "vacation.jpg").write_text("x")
    plans = plan_rename(tmp_path, "2026_{name}{ext}")
    assert plans[0].destination.name == "2026_vacation.jpg"


def test_apply_rename_actually_renames_files(tmp_path):
    (tmp_path / "a.jpg").write_text("data")
    plans = plan_rename(tmp_path, "photo_{n:03d}{ext}")
    apply_rename(plans)

    assert (tmp_path / "photo_001.jpg").exists()
    assert not (tmp_path / "a.jpg").exists()


def test_rename_collisions_get_deduped(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    (tmp_path / "b.jpg").write_text("x")

    # Pattern collapses both files to the same name on purpose.
    plans = plan_rename(tmp_path, "same{ext}")
    names = sorted(p.destination.name for p in plans)

    assert names == ["same-1.jpg", "same.jpg"]
