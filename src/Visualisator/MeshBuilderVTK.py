import vtk


class MeshBuilderVTK:
    def __init__(self, model_full_filename):
        self.model_full_filename = model_full_filename

        ext = model_full_filename.split('.')[-1]
        self.mesh_reader = vtk.vtkSTLReader if ext == 'stl' else vtk.vtkOBJReader

    def build_mesh(self):
        vtk.vtkAlgorithmOutput().SetGlobalWarningDisplay(False)

        reader = self.mesh_reader()
        reader.SetFileName(self.model_full_filename)

        reader.Update()
        model_vtk_mesh = reader.GetOutput()
        del reader
        return model_vtk_mesh
