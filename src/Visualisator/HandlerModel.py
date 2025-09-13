import pickle
import traceback
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
    """Build mesh from file"""
    try:
        mesh: vtkPolyData = MeshBuilderVTK(full_filename).build_mesh()
        return mesh
    except Exception as e:
        print(f"Error building mesh: {e}")
        return None


@dataclass
class HandledModel:
    filename: str
    volume_mm3: float
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
        """Build mesh from file"""
        try:
            self.dprint('Building mesh from file...')

            # Перевіряємо чи існує файл
            import os
            if not os.path.exists(self.full_filename):
                self.dprint.error(f'File does not exist: {self.full_filename}')
                return False

            vtk_mesh = build(self.full_filename)
            if vtk_mesh is None:
                self.dprint.error('Failed to build VTK mesh')
                return False

            self.pyvista_mesh = pyvista.wrap(vtk_mesh)

            if self.pyvista_mesh is None:
                self.dprint.error('Failed to wrap VTK mesh with PyVista')
                return False

            if self.pyvista_mesh.n_points == 0:
                self.dprint.error('Mesh has no points')
                return False

            self.dprint.success(
                f'Mesh built successfully. Points: {self.pyvista_mesh.n_points}, Volume: {self.pyvista_mesh.volume:.2f} mm³')
            return True

        except Exception as e:
            self.dprint.error(f'Error building mesh: {str(e)}')
            self.dprint.error(f'Traceback: {traceback.format_exc()}')
            return False

    def _visualize(self):
        """Create visualization from mesh"""
        try:
            if self.pyvista_mesh is None or self.pyvista_mesh.n_points == 0:
                self.dprint.error('No valid mesh to visualize')
                return False

            self.dprint('Creating visualization...')

            visualizer = Visualizer(
                poly_data=self.pyvista_mesh,
                frames=self.anim_frames,
                angle=self.anim_angle
            )

            self.image = visualizer.gen_gif()

            if self.image is None:
                self.dprint.error('Visualization failed - no image generated')
                return False

            self.dprint.success('Visualization created successfully')
            return True

        except Exception as e:
            self.dprint.error(f'Error creating visualization: {str(e)}')
            self.dprint.error(f'Traceback: {traceback.format_exc()}')
            return False

    def process(self):
        """Process the model file and create visualization"""
        try:
            self.dprint('Starting model processing...')

            # Build mesh
            if not self._build():
                self.dprint.error('Failed to build mesh')
                return None

            # Create visualization
            if not self._visualize():
                self.dprint.error('Failed to create visualization')
                return None

            if self.pyvista_mesh is None:
                self.dprint.error('No mesh available')
                return None

            result = HandledModel(
                filename=self.full_filename,
                volume_mm3=self.pyvista_mesh.volume,
                image=self.image
            )

            self.dprint.success('Model processing completed successfully')
            return result

        except Exception as e:
            self.dprint.error(f'Error processing model: {str(e)}')
            self.dprint.error(f'Traceback: {traceback.format_exc()}')
            return None
