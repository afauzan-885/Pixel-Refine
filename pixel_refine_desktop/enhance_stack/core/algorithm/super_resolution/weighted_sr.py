import taichi as ti
import numpy as np

# Initialize Taichi safely
try:
    if not ti.lang.impl.get_runtime().prog:
        try:
            ti.init(arch=ti.vulkan)
        except Exception:
            ti.init()
except Exception:
    try:
        ti.init(arch=ti.vulkan)
    except Exception:
        ti.init()


@ti.data_oriented
class TaichiWSR:
    def __init__(self, lr_shape, hr_shape, num_frames, scale=2, alpha=0.7, beta=0.01, btv_window=2):
        self.scale = scale
        self.lr_h, self.lr_w = lr_shape
        self.hr_h, self.hr_w = hr_shape
        self.num_frames = num_frames
        self.alpha = alpha
        self.beta = beta  # Step size (learning rate)
        self.btv_window = btv_window

        # HR Fields
        self.hr_image = ti.field(dtype=ti.f32, shape=(self.hr_h, self.hr_w))
        self.hr_grad = ti.field(dtype=ti.f32, shape=(self.hr_h, self.hr_w))
        self.temp_hr = ti.field(dtype=ti.f32, shape=(self.hr_h, self.hr_w))

        # LR Fields
        self.lr_frames = ti.field(dtype=ti.f32, shape=(num_frames, self.lr_h, self.lr_w))
        self.sim_lr = ti.field(dtype=ti.f32, shape=(num_frames, self.lr_h, self.lr_w))
        self.lr_error = ti.field(dtype=ti.f32, shape=(num_frames, self.lr_h, self.lr_w))
        
        # Spatial Weight Maps (computed externally based on ghosting / tile rejection)
        self.weight_maps = ti.field(dtype=ti.f32, shape=(num_frames, self.lr_h, self.lr_w))

        # Sub-pixel motion vectors (dy, dx in HR pixel units)
        self.shifts = ti.Vector.field(2, dtype=ti.f32, shape=(num_frames,))

    def set_lr_data(self, lr_np, weight_maps_np, shifts_np):
        self.lr_frames.from_numpy(lr_np.astype(np.float32))
        self.weight_maps.from_numpy(weight_maps_np.astype(np.float32))
        self.shifts.from_numpy(shifts_np.astype(np.float32))

    def set_initial_hr(self, hr_np):
        self.hr_image.from_numpy(hr_np.astype(np.float32))

    def get_hr_image(self):
        return self.hr_image.to_numpy()

    @ti.func
    def get_pixel_bilinear(self, y: ti.f32, x: ti.f32):
        # Bilinear interpolation with boundary clamping
        y_clamped = ti.max(0.0, ti.min(float(self.hr_h) - 1.0 - 1e-4, y))
        x_clamped = ti.max(0.0, ti.min(float(self.hr_w) - 1.0 - 1e-4, x))
        
        y0 = int(ti.floor(y_clamped))
        x0 = int(ti.floor(x_clamped))
        y1 = y0 + 1
        x1 = x0 + 1
        
        dy = y_clamped - float(y0)
        dx = x_clamped - float(x0)
        
        val00 = self.hr_image[y0, x0]
        val01 = self.hr_image[y0, x1]
        val10 = self.hr_image[y1, x0]
        val11 = self.hr_image[y1, x1]
        
        return (1.0 - dy) * ((1.0 - dx) * val00 + dx * val01) + dy * ((1.0 - dx) * val10 + dx * val11)

    @ti.func
    def get_pixel_bilinear_temp(self, y: ti.f32, x: ti.f32):
        # Bilinear interpolation with boundary clamping on temp_hr
        y_clamped = ti.max(0.0, ti.min(float(self.hr_h) - 1.0 - 1e-4, y))
        x_clamped = ti.max(0.0, ti.min(float(self.hr_w) - 1.0 - 1e-4, x))
        
        y0 = int(ti.floor(y_clamped))
        x0 = int(ti.floor(x_clamped))
        y1 = y0 + 1
        x1 = x0 + 1
        
        dy = y_clamped - float(y0)
        dx = x_clamped - float(x0)
        
        val00 = self.temp_hr[y0, x0]
        val01 = self.temp_hr[y0, x1]
        val10 = self.temp_hr[y1, x0]
        val11 = self.temp_hr[y1, x1]
        
        return (1.0 - dy) * ((1.0 - dx) * val00 + dx * val01) + dy * ((1.0 - dx) * val10 + dx * val11)

    @ti.kernel
    def simulate_lr_frames(self):
        # D * H * F * X
        # Simulate local Gaussian PSF blur (5x5, std=1.0)
        for k, y_lr, x_lr in self.sim_lr:
            shift = self.shifts[k]
            cy = float(y_lr * self.scale) + shift[0]
            cx = float(x_lr * self.scale) + shift[1]

            val = 0.0
            weight_sum = 0.0
            
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    dist2 = float(dy*dy + dx*dx)
                    w = ti.exp(-dist2 / 2.0)
                    
                    val += w * self.get_pixel_bilinear(cy + float(dy), cx + float(dx))
                    weight_sum += w
            
            self.sim_lr[k, y_lr, x_lr] = val / weight_sum

    @ti.kernel
    def compute_lr_error(self):
        # L2 norm error terbobot spasial: W_k^2 * (sim_lr - lr_frames)
        for k, y_lr, x_lr in self.lr_error:
            diff = self.sim_lr[k, y_lr, x_lr] - self.lr_frames[k, y_lr, x_lr]
            w = self.weight_maps[k, y_lr, x_lr]
            self.lr_error[k, y_lr, x_lr] = (w * w) * diff

    @ti.kernel
    def reset_grad(self):
        for i, j in self.hr_grad:
            self.hr_grad[i, j] = 0.0

    @ti.kernel
    def backproject_frame_accumulate(self, k: ti.i32):
        shift = self.shifts[k]
        
        # Step 1 & 2: D^T (Upsample) and H^T (Blur with 5x5 Gaussian PSF)
        for i_hr, j_hr in self.temp_hr:
            val = 0.0
            lr_y_center = i_hr // self.scale
            lr_x_center = j_hr // self.scale
            
            for dy_lr in range(-2, 3):
                for dx_lr in range(-2, 3):
                    ly = lr_y_center + dy_lr
                    lx = lr_x_center + dx_lr
                    
                    if 0 <= ly < self.lr_h and 0 <= lx < self.lr_w:
                        upsampled_y = ly * self.scale
                        upsampled_x = lx * self.scale
                        
                        dist_y = abs(i_hr - upsampled_y)
                        dist_x = abs(j_hr - upsampled_x)
                        
                        if dist_y <= 2 and dist_x <= 2:
                            dist2 = float(dist_y*dist_y + dist_x*dist_x)
                            w = ti.exp(-dist2 / 2.0)
                            val += w * self.lr_error[k, ly, lx]
            self.temp_hr[i_hr, j_hr] = val / 6.0

        # Step 3: F_k^T (Shift Back)
        for i_hr, j_hr in self.hr_grad:
            target_y = float(i_hr) + shift[0]
            target_x = float(j_hr) + shift[1]
            self.hr_grad[i_hr, j_hr] += self.get_pixel_bilinear_temp(target_y, target_x)

    def backproject_data_gradient(self):
        self.reset_grad()
        for k in range(self.num_frames):
            self.backproject_frame_accumulate(k)

    @ti.kernel
    def apply_btv_regularization(self, lam: ti.f32):
        # Asymmetric BTV gradient to avoid double counting
        for i, j in self.hr_image:
            btv_grad = 0.0
            for dy in range(0, self.btv_window + 1):
                for dx in range(-self.btv_window, self.btv_window + 1):
                    if dy > 0 or (dy == 0 and dx >= 0):
                        if dy != 0 or dx != 0:
                            power = abs(dy) + abs(dx)
                            weight = ti.pow(self.alpha, float(power))

                            y_fwd = ti.max(0, ti.min(self.hr_h - 1, i + dy))
                            x_fwd = ti.max(0, ti.min(self.hr_w - 1, j + dx))

                            y_bwd = ti.max(0, ti.min(self.hr_h - 1, i - dy))
                            x_bwd = ti.max(0, ti.min(self.hr_w - 1, j - dx))

                            diff_fwd = self.hr_image[i, j] - self.hr_image[y_fwd, x_fwd]
                            sgn_fwd = 0.0
                            if diff_fwd > 1e-5:
                                sgn_fwd = 1.0
                            elif diff_fwd < -1e-5:
                                sgn_fwd = -1.0

                            diff_bwd = self.hr_image[i, j] - self.hr_image[y_bwd, x_bwd]
                            sgn_bwd = 0.0
                            if diff_bwd > 1e-5:
                                sgn_bwd = 1.0
                            elif diff_bwd < -1e-5:
                                sgn_bwd = -1.0

                            btv_grad += weight * (sgn_fwd - sgn_bwd)

            self.hr_grad[i, j] += lam * btv_grad

    @ti.kernel
    def update_hr_image(self):
        for i, j in self.hr_image:
            self.hr_image[i, j] = ti.max(0.0, ti.min(1.0, self.hr_image[i, j] - self.beta * self.hr_grad[i, j]))

    def step(self, lam):
        self.simulate_lr_frames()
        self.compute_lr_error()
        self.backproject_data_gradient()
        if lam > 0.0:
            self.apply_btv_regularization(lam)
        self.update_hr_image()
