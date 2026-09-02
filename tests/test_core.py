from organizer.core import plan_organization, apply_plan


def test_plan_sorts_files_into_correct_categories(tmp_path):
    (tmp_path / "photo.jpg").write_text("x")
    (tmp_path / "notes.pdf").write_text("x")
    (tmp_path / "song.mp3").write_text("x")

    plans = plan_organization(tmp_path)
    categories = {p.source.name: p.category for p in plans}

    assert categories["photo.jpg"] == "Images"
    assert categories["notes.pdf"] == "Documents"
    assert categories["song.mp3"] == "Audio"


def test_unknown_extension_goes_to_other(tmp_path):
    (tmp_path / "mystery.xyz").write_text("x")
    plans = plan_organization(tmp_path)
    assert plans[0].category == "Other"


def test_file_with_no_extension_goes_to_other(tmp_path):
    (tmp_path / "README").write_text("x")
    plans = plan_organization(tmp_path)
    assert plans[0].category == "Other"


def test_hidden_files_skipped_by_default(tmp_path):
    (tmp_path / ".env").write_text("x")
    (tmp_path / "visible.txt").write_text("x")

    plans = plan_organization(tmp_path)
    names = [p.source.name for p in plans]

    assert ".env" not in names
    assert "visible.txt" in names


def test_hidden_files_included_when_requested(tmp_path):
    (tmp_path / ".env").write_text("x")
    plans = plan_organization(tmp_path, include_hidden=True)
    assert any(p.source.name == ".env" for p in plans)


def test_subdirectories_are_left_alone(tmp_path):
    sub = tmp_path / "already_organized"
    sub.mkdir()
    (sub / "photo.jpg").write_text("x")

    plans = plan_organization(tmp_path)
    assert plans == []


def test_empty_directory_produces_no_plans(tmp_path):
    assert plan_organization(tmp_path) == []


def test_duplicate_filenames_get_unique_destinations(tmp_path):
    docs_dir = tmp_path / "Documents"
    docs_dir.mkdir()
    (docs_dir / "report.pdf").write_text("existing file")  # already occupies the target name
    (tmp_path / "report.pdf").write_text("new file")

    plans = plan_organization(tmp_path)
    assert plans[0].destination.name == "report (1).pdf"


def test_apply_plan_actually_moves_files(tmp_path):
    (tmp_path / "photo.jpg").write_text("data")
    plans = plan_organization(tmp_path)
    results = apply_plan(plans)

    assert results[0].status == "moved"
    assert (tmp_path / "Images" / "photo.jpg").exists()
    assert not (tmp_path / "photo.jpg").exists()


def test_rerunning_organize_on_already_sorted_folder_is_a_noop(tmp_path):
    (tmp_path / "photo.jpg").write_text("data")
    apply_plan(plan_organization(tmp_path))

    # Second pass over the top-level directory should find nothing loose left.
    second_pass = plan_organization(tmp_path)
    assert second_pass == []
