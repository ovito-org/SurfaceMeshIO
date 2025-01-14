import numpy as np
import pytest
from ovito.io import import_file, export_file
from ovito import Scene
import numpy as np
import tempfile as tf
from pathlib import Path
from SurfaceMeshIO import SurfaceMeshFileWriter


@pytest.fixture(scope="session")
def state_data():
    scene = Scene()
    scene.load(
        "examples/example_01.ovito",
    )
    return scene.pipelines[0].compute()


@pytest.fixture(scope="session")
def npz_ref_file():
    return "examples/example_01.npz"


@pytest.fixture(scope="session")
def npz_data(npz_ref_file):
    return import_file(
        npz_ref_file,
    ).compute()


@pytest.fixture()
def npz_tmp_file():
    fname = Path(tf.gettempdir(), f"{np.random.randint(0, 2**31-1)}.npz")
    yield fname
    if fname.exists():
        fname.unlink()


def test_export(state_data, npz_ref_file, npz_tmp_file):
    mesh = list(state_data.surfaces.keys())[0]
    export_file(state_data, npz_tmp_file, format=SurfaceMeshFileWriter, key=mesh)
    data = np.load(npz_tmp_file)
    ref = np.load(npz_ref_file)

    assert data.keys() == ref.keys()
    for key in data.keys():
        if isinstance(data[key].dtype, np.number):
            assert np.allclose(data[key], ref[key])
        else:
            assert np.all(data[key] == ref[key])


def test_mesh(state_data, npz_data):
    assert state_data.surfaces.keys() == npz_data.surfaces.keys()
    assert len(state_data.surfaces.keys()) == 1


def test_vertex_keys(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    assert (
        state_data.surfaces[mesh].vertices.keys()
        == npz_data.surfaces[mesh].vertices.keys()
    )


def test_faces_keys(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    assert (
        state_data.surfaces[mesh].faces.keys() == npz_data.surfaces[mesh].faces.keys()
    )


def test_regions_keys(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    assert (
        state_data.surfaces[mesh].regions.keys()
        == npz_data.surfaces[mesh].regions.keys()
    )


def test_vertex_values(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    for key in state_data.surfaces[mesh].vertices.keys():
        assert np.allclose(
            state_data.surfaces[mesh].vertices[key],
            npz_data.surfaces[mesh].vertices[key],
        )


def test_face_values(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    for key in state_data.surfaces[mesh].faces.keys():
        assert np.allclose(
            state_data.surfaces[mesh].faces[key],
            npz_data.surfaces[mesh].faces[key],
        )


def test_region_values(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    for key in state_data.surfaces[mesh].regions.keys():
        assert np.allclose(
            state_data.surfaces[mesh].regions[key],
            npz_data.surfaces[mesh].regions[key],
        )


def test_topology(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    assert np.allclose(
        state_data.surfaces[mesh].get_face_vertices(),
        npz_data.surfaces[mesh].get_face_vertices(),
    )


def test_cell(state_data, npz_data):
    mesh = list(state_data.surfaces.keys())[0]
    assert np.allclose(
        state_data.surfaces[mesh].domain[...], npz_data.surfaces[mesh].domain[...]
    )
    assert state_data.surfaces[mesh].domain.pbc == npz_data.surfaces[mesh].domain.pbc
