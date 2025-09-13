import pickle
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from io import BytesIO

import pyvista
import vtkmodules.util.pickle_support  # For pickle vtkPolyData
from vtkmodules.vtkCommonDataModel import vtkPolyData

from src.DebugPrinter import DPrint
from src.Visualisator.MeshBuilderVTK import MeshBuilderVTK
from src.Visualisator.RenderPyVista import Visualizer

@dataclass
class ProcessedModel:
    filename: str = ''
    volume_mm3: float = 0.0
    image = None


def build(full_filename):
    mesh: vtkPolyData = MeshBuilderVTK(full_filename).build_mesh()
    return mesh

@dataclass
class HandledModel:
    filename: str
    volume_mm3: int
    image: None | BytesIO

class HandlerModel:
    def __init__(
            self,
            full_filename: str,
            frames: int,
            dprint: DPrint,
    ):
        self.filename = full_filename.split('/')[-1]
        self.full_filename = full_filename
        self.dprint = DPrint(f'HANDLER "{self.filename}"', base=dprint)

        self.pyvista_mesh: pyvista.PolyData | None = None
        self.anim_frames = frames
        self.anim_angle = 360 / self.anim_frames
        self.image = None

    def _build(self):
        self.dprint('Building...')
        self.pyvista_mesh = pyvista.wrap(build(self.full_filename))

        if self.pyvista_mesh.n_points == 0:
            return

        self.dprint(f'Was read, volume: {self.pyvista_mesh.volume} mm3')

    def _visualize(self):
        if self.pyvista_mesh is None or self.pyvista_mesh.n_points == 0:
            return

        self.dprint('Capturing...')

        visualizer = Visualizer(poly_data=self.pyvista_mesh, frames=self.anim_frames, angle=self.anim_angle)
        self.image = visualizer.gen_gif()
        self.dprint(f'Was captured.')

    def process(self):
        self._build()
        self._visualize()

        return HandledModel(self.full_filename, self.pyvista_mesh.volume, self.image) if self.pyvista_mesh.n_points > 0 else None
