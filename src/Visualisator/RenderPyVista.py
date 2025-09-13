import io

import imageio
import pyvista
import pyvista as pv


class Visualizer:
    def __init__(self, poly_data: pyvista.PolyData, frames, angle, window_size=(1024, 1024)):
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
            self.plotter.camera.azimuth += self.angle
            images.append(self.render_frame())
        return images

    def gen_gif(self):
        if not self.poly_data.n_points:
            return None

        try:
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

            if not images:
                print("No images captured")
                return None

            buffer = io.BytesIO()

            # Use ffmpeg writer for MP4 - this fixes the format issue
            writer = imageio.get_writer(
                buffer,
                format='FFMPEG',
                fps=30,
                codec='libx264',
                quality=7,
                pixelformat='yuv420p'
            )

            for image in images:
                writer.append_data(image)
            writer.close()

            buffer.seek(0)
            return buffer

        except Exception as e:
            print(f"Error in gen_gif: {e}")
            return None
        finally:
            if self.plotter is not None:
                try:
                    self.plotter.close()
                except:
                    pass