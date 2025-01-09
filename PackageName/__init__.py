from ovito.io import FileWriterInterface
from ovito.data import DataObject
from ovito.pipeline import Pipeline


class CustomFileWriter(FileWriterInterface):

    def exportable_type(self):
        pass

    def supports_trajectories(self):
        pass

    def write(
        self,
        *,
        filename: str,
        frame: int,
        pipeline: Pipeline,
        object_ref: DataObject.Ref,
        **kwargs,
    ):
        pass
