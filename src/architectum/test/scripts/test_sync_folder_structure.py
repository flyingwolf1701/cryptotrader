import os
import shutil
import pytest

from architectum.scripts.sync_folder_structure import list_directories, calculate_drift

@pytest.fixture
def temp_test_src(tmp_path):
    return tmp_path

def test_list_directories_only_folders(temp_test_src):
    # Create folders and files
    (temp_test_src / "folder1").mkdir()
    (temp_test_src / "folder2").mkdir()
    (temp_test_src / "file1.py").write_text("print('Hello')")

    dirs = list_directories(str(temp_test_src))

    # Should only include folders, not files
    assert "folder1" in dirs
    assert "folder2" in dirs
    assert "file1.py" not in dirs

def test_calculate_drift_detects_missing_and_extra(temp_test_src):
    # Create real src structure
    real_src = temp_test_src / "real_src"
    (real_src / "folderA").mkdir(parents=True)
    (real_src / "folderB").mkdir(parents=True)

    # Create architectum structure
    arch_src = temp_test_src / "arch_src" / "src"
    (arch_src / "folderA").mkdir(parents=True)  # folderA matches
    (arch_src / "folderC").mkdir(parents=True)  # folderC extra

    missing, extra = calculate_drift(str(real_src), str(temp_test_src / "arch_src"))

    assert "folderB" in missing
    assert "folderC" in extra
    assert "folderA" not in missing
    assert "folderA" not in extra
