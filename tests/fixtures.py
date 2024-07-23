import shutil
from datetime import datetime
from pathlib import Path
from typing import Generator, List
from zipfile import ZipFile

import pytest

from darwin.config import Config
from darwin.dataset.release import Release, ReleaseStatus


@pytest.fixture
def darwin_path(tmp_path: Path) -> Path:
    return tmp_path / "darwin-test"


@pytest.fixture
def darwin_config_path(darwin_path: Path) -> Path:
    return darwin_path / "config.yaml"


@pytest.fixture
def darwin_datasets_path(darwin_path: Path) -> Path:
    return darwin_path / "datasets"


@pytest.fixture
def team_slug_darwin_json_v2() -> str:
    return "v7-darwin-json-v2"


@pytest.fixture
def dataset_name() -> str:
    return "test_dataset"


@pytest.fixture
def dataset_slug() -> str:
    return "test-dataset"


@pytest.fixture
def release_name() -> str:
    return "latest"


@pytest.fixture
def team_dataset_path(
    darwin_datasets_path: Path, team_slug_darwin_json_v2: str, dataset_name: str
) -> Path:
    return darwin_datasets_path / team_slug_darwin_json_v2 / dataset_name


@pytest.fixture
def team_extracted_dataset_path(darwin_datasets_path: Path):
    with ZipFile("./tests/data.zip", "r") as zipObj:
        zipObj.extractall(path=darwin_datasets_path)
    return darwin_datasets_path


@pytest.fixture
def team_dataset_release_path(team_dataset_path: Path, release_name: str) -> Path:
    return team_dataset_path / "releases" / release_name


@pytest.fixture
def split_name() -> str:
    return "test_split"


@pytest.fixture
def split_path(team_dataset_release_path: Path, split_name: str) -> Path:
    return team_dataset_release_path / "lists" / split_name


@pytest.fixture
def annotations_path(team_dataset_release_path: Path) -> Path:
    return team_dataset_release_path / "annotations"


@pytest.fixture
def file_read_write_test(darwin_path: Path, annotations_path: Path, split_path: Path):
    # Executed before the test
    annotations_path.mkdir(parents=True)
    split_path.mkdir(parents=True)

    # Useful if the test needs to reuse attrs
    yield

    # Executed after the test
    shutil.rmtree(darwin_path)


@pytest.fixture
def local_config_file(
    team_slug_darwin_json_v2: str, darwin_datasets_path: Path
) -> Generator[Config, None, None]:
    darwin_path = Path.home() / ".darwin"
    backup_darwin_path = Path.home() / ".darwin_backup"
    config_path = darwin_path / "config.yaml"

    # Executed before the test
    if darwin_path.exists():
        shutil.move(str(darwin_path), str(backup_darwin_path))
    darwin_path.mkdir()

    config = Config(config_path)
    config.put(["global", "api_endpoint"], "http://localhost/api")
    config.put(["global", "base_url"], "http://localhost")
    config.put(["teams", team_slug_darwin_json_v2, "api_key"], "mock_api_key")
    config.put(
        ["teams", team_slug_darwin_json_v2, "datasets_dir"], str(darwin_datasets_path)
    )

    # Useful if the test needs to reuse attrs
    yield config

    # Executed after the test
    shutil.rmtree(darwin_path)
    if backup_darwin_path.exists():
        shutil.move(backup_darwin_path, darwin_path)


@pytest.fixture
def pending_release() -> Release:
    return Release(
        dataset_slug="dataset_slug",
        team_slug="team_slug",
        version="1",
        name="name",
        status=ReleaseStatus("pending"),
        url=None,
        export_date=datetime.now(),
        image_count=1,
        class_count=1,
        available=False,
        latest=False,
        format="json",
    )


@pytest.fixture
def releases_api_response() -> List[dict]:
    return [
        {
            "name": "release_1",
            "status": ReleaseStatus("complete"),
            "version": 1,
            "format": "darwin_json_2",
            "metadata": {
                "num_images": 1,
                "annotation_classes": [{"id": 1, "name": "test_class"}],
            },
            "inserted_at": "2024-06-28T12:29:02Z",
            "latest": True,
            "download_url": "download_url",
        },
        {
            "name": "release_2",
            "status": ReleaseStatus("pending"),
            "version": 2,
            "format": "darwin_json_2",
            "metadata": {},
            "inserted_at": "2024-06-28T12:32:33Z",
            "latest": False,
            "download_url": None,
        },
    ]
