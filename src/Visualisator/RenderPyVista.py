import io
import tempfile
import os

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

            # Try different approaches for creating MP4
            buffer = io.BytesIO()

            try:
                # Method 1: Try with mp4 format directly
                writer = imageio.get_writer(
                    buffer,
                    format='mp4',
                    fps=30,
                    quality=7,
                    pixelformat='yuv420p'
                )

                for image in images:
                    writer.append_data(image)
                writer.close()

            except Exception as e1:
                print(f"Method 1 failed: {e1}")
                buffer = io.BytesIO()

                try:
                    # Method 2: Try with ffmpeg-imageio plugin
                    writer = imageio.get_writer(
                        buffer,
                        format='ffmpeg',
                        fps=30,
                        codec='libx264',
                        quality=7,
                        pixelformat='yuv420p'
                    )

                    for image in images:
                        writer.append_data(image)
                    writer.close()

                except Exception as e2:
                    print(f"Method 2 failed: {e2}")

                    try:
                        # Method 3: Create temporary file and read it back
                        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                            temp_filename = temp_file.name

                        writer = imageio.get_writer(
                            temp_filename,
                            fps=30,
                            quality=7,
                            pixelformat='yuv420p'
                        )

                        for image in images:
                            writer.append_data(image)
                        writer.close()

                        # Read the file back into buffer
                        with open(temp_filename, 'rb') as f:
                            buffer.write(f.read())

                        # Clean up temporary file
                        os.unlink(temp_filename)

                    except Exception as e3:
                        print(f"Method 3 failed: {e3}")

                        # Method 4: Fall back to GIF if MP4 fails
                        try:
                            buffer = io.BytesIO()
                            writer = imageio.get_writer(
                                buffer,
                                format='gif',
                                duration=1 / 30,
                                loop=0
                            )

                            for image in images:
                                writer.append_data(image)
                            writer.close()

                        except Exception as e4:
                            print(f"All methods failed. Last error: {e4}")
                            return None

            buffer.seek(0)
            return buffer

        except Exception as e:
            print(f"Error in gen_gif: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if self.plotter is not None:
                try:
                    self.plotter.close()
                except:
                    pass
