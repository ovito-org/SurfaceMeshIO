import numpy as np
from ovito.data import DataCollection, DataObject, SurfaceMesh
from ovito.io import FileReaderInterface, FileWriterInterface
from ovito.pipeline import Pipeline


class SurfaceMeshFileWriter(FileWriterInterface):

    def exportable_type(self):
        return SurfaceMesh

    def supports_trajectories(self):
        return False

    def write(
        self,
        *,
        filename: str,
        frame: int,
        pipeline: Pipeline,
        object_ref: DataObject.Ref,
        **kwargs,
    ):
        data = pipeline.compute(frame)
        mesh = data.get(object_ref)

        mesh_data = {}

        # Version
        mesh_data["SurfaceMeshFileWriter"] = 1.0

        # Meta data
        mesh_data["Identifier"] = mesh.identifier
        mesh_data["Title"] = mesh.title

        # Cell
        mesh_data["cell/matrix"] = mesh.domain[...]
        mesh_data["cell/pbc"] = mesh.domain.pbc

        # All surface data
        mesh_data["face_vertices"] = mesh.get_face_vertices()
        for key in mesh.vertices.keys():
            mesh_data[f"vertices/{key}"] = mesh.vertices[key]
        for key in mesh.faces.keys():
            mesh_data[f"faces/{key}"] = mesh.faces[key]
        for key in mesh.regions.keys():
            mesh_data[f"regions/{key}"] = mesh.regions[key]

        # Export
        np.savez_compressed(filename, **mesh_data)


class SurfaceMeshFileReader(FileReaderInterface):
    @staticmethod
    def detect(filename: str):
        # Try reading the file and validate the "SurfaceMeshFileWriter" key (could validate version as well)
        try:
            mesh_data = np.load(filename)
            return "SurfaceMeshFileWriter" in mesh_data
        except OSError:
            return False

    def parse(self, data: DataCollection, filename: str, *args, **kwargs):
        # Open file
        mesh_data = np.load(filename)

        # Validate mandatory keys
        if "vertices/Position" not in mesh_data:
            raise KeyError("'vertices/Position' missing in mesh data")
        if "face_vertices" not in mesh_data:
            raise KeyError("'face_vertices' missing in mesh data")
        if "cell/matrix" not in mesh_data or "cell/pbc" not in mesh_data:
            raise KeyError("Cell information missing in mesh data")

        # Create cell
        cell = data.create_cell(mesh_data["cell/matrix"], mesh_data["cell/pbc"])

        # Create surface mesh
        mesh = data.surfaces.create(
            identifier=str(mesh_data["Identifier"]), title=str(mesh_data["Title"])
        )
        # set mesh domain
        mesh.domain = cell

        # set mesh vertices and their properties
        for key in mesh_data:
            if key.startswith("vertices"):
                if key.split("/")[1] == "Position":
                    mesh.create_vertices(mesh_data[key])
                else:
                    mesh.vertices_.create_property(
                        key.split("/")[1], data=mesh_data[key]
                    )

        # read and create faces
        mesh.create_faces(mesh_data["face_vertices"])

        # set face and region properties
        for key in mesh_data:
            if key.startswith("faces"):
                mesh.faces_.create_property(key.split("/")[1], data=mesh_data[key])
            elif key.startswith("regions"):
                mesh.regions_.create_property(key.split("/")[1], data=mesh_data[key])

        if not mesh.connect_opposite_halfedges():
            raise RuntimeWarning("Mesh is not closed!")
