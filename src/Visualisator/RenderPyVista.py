import io

import imageio
import pyvista
import pyvista as pv


class Visualizer:
    def __init__(self, poly_data: pyvista.PolyData, frames, angle, window_size=(2048, 2048)):
        self.poly_data = poly_data
        self.frames = frames
        self.angle = angle
        self.window_size = window_size
        self.plotter = pv.Plotter(off_screen=True, polygon_smoothing=True, lighting='three lights')
        self.reader = None

    def render_frame(self):
        self.plotter.background_color = 'grey'
        self.plotter.render()
        img = self.plotter.screenshot()
        return img

    def rotate_and_capture(self):
        images = []
        self.plotter.window_size = self.window_size
        for i in range(self.frames):
            self.plotter.camera.azimuth += self.angle  # Incrementally rotate the camera around the z-axis
            images.append(self.render_frame())
        return images

    def gen_gif(self):
        if not self.poly_data.n_points:
            return None

        pv_mesh = pv.wrap(self.poly_data)
        self.plotter.add_mesh(
            pv_mesh,
            color='orange',
            lighting=True,
            smooth_shading=False,
            diffuse=1,
            pbr=True,
            metallic=1,
            roughness=0.5,
        )

        images = self.rotate_and_capture()
        self.plotter.close()

        buffer = io.BytesIO()
        buffer.name = 'model_mesh.mp4'
        writer = imageio.get_writer(buffer, fps=30, format='mp4')
        for image in images:
            writer.append_data(image)
        writer.close()

        buffer.seek(0)
        return buffer
