import torch
import numpy as np
import torch.nn as nn
from torchvision.models import mobilenet_v2

class DecoderBlock(nn.Module):
    """
    Blok Decoder U-Net yang melakukan upsampling, konkatenasi dengan fitur
    dari skip connection, dan beberapa lapisan konvolusi.
    """
    def __init__(self, in_channels, skip_channels, out_channels):
        super().__init__()
        # Lapisan untuk menggabungkan input dari decoder dan encoder
        combined_channels = in_channels + skip_channels
        
        self.conv1 = nn.Conv2d(combined_channels, out_channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu1 = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.relu2 = nn.ReLU(inplace=True)

        # Upsampling bisa menggunakan TransposedConv atau Upsample + Conv
        # Upsample + Conv biasanya lebih stabil dan menghindari artefak checkerboard
        self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)

    def forward(self, x, skip_features):
        x = self.upsample(x)
        x = torch.cat([x, skip_features], dim=1)
        x = self.relu1(self.bn1(self.conv1(x)))
        x = self.relu2(self.bn2(self.conv2(x)))
        return x

class MobileNetV2UNet(nn.Module):
    """
    Arsitektur U-Net yang menggunakan MobileNetV2 sebagai encoder.
    Dirancang untuk tugas menghasilkan alpha map (1 channel output).
    """
    def __init__(self, n_input_channels=6, n_output_channels=1, pretrained=True):
        super().__init__()

        # --- ENCODER ---
        # Muat MobileNetV2 pretrained
        self.mobilenet = mobilenet_v2(pretrained=pretrained)

        # Ubah lapisan konvolusi pertama untuk menerima jumlah channel input yang kita inginkan
        # MobileNetV2 aslinya menerima 3 channel (RGB)
        original_conv1 = self.mobilenet.features[0][0]
        self.mobilenet.features[0][0] = nn.Conv2d(
            n_input_channels, 
            original_conv1.out_channels, 
            kernel_size=original_conv1.kernel_size, 
            stride=original_conv1.stride, 
            padding=original_conv1.padding, 
            bias=False
        )

        # Ambil lapisan-lapisan dari encoder untuk skip connections
        self.encoder_layer0 = self.mobilenet.features[0]   # Output 1/2 size
        self.encoder_layer1 = self.mobilenet.features[1]   # Output 1/2 size
        self.encoder_layer2 = self.mobilenet.features[2:4] # Output 1/4 size
        self.encoder_layer3 = self.mobilenet.features[4:7] # Output 1/8 size
        self.encoder_layer4 = self.mobilenet.features[7:14]# Output 1/16 size
        
        # Titik terdalam dari U-Net (bottleneck)
        self.bottleneck = self.mobilenet.features[14:18]   # Output 1/32 size

        # --- DECODER ---
        # Channel-channel ini harus cocok dengan output dari lapisan encoder MobileNetV2
        # Ukuran channel output MobileNetV2: 16, 24, 32, 96, 320
        self.decoder4 = DecoderBlock(320, 96, 256)
        self.decoder3 = DecoderBlock(256, 32, 128)
        self.decoder2 = DecoderBlock(128, 24, 64)
        self.decoder1 = DecoderBlock(64, 16, 32)
        
        # Lapisan konvolusi akhir untuk menghasilkan output dengan channel yang diinginkan
        self.final_conv = nn.Conv2d(32, n_output_channels, kernel_size=1)
        
        # Aktivasi Sigmoid untuk memastikan output alpha map antara 0 dan 1
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # --- ENCODER PATH ---
        skip0 = self.encoder_layer0(x)                 # 1/2 size
        skip1 = self.encoder_layer1(skip0)             # 1/2 size
        skip2 = self.encoder_layer2(skip1)             # 1/4 size
        skip3 = self.encoder_layer3(skip2)             # 1/8 size
        skip4 = self.encoder_layer4(skip3)             # 1/16 size
        
        bottleneck = self.bottleneck(skip4)            # 1/32 size

        # --- DECODER PATH ---
        d4 = self.decoder4(bottleneck, skip4)          # 1/16 size
        d3 = self.decoder3(d4, skip3)                  # 1/8 size
        d2 = self.decoder2(d3, skip2)                  # 1/4 size
        d1 = self.decoder1(d2, skip1)                  # 1/2 size

        # Final upsampling agar ukurannya sama dengan input
        d0 = nn.functional.interpolate(d1, scale_factor=2, mode='bilinear', align_corners=True)
        
        output = self.final_conv(d0)
        alpha_map = self.sigmoid(output)
        
        return alpha_map

class AlphaGenerator:
    """
    Kelas pembungkus untuk mengelola model MobileNetV2-U-Net.
    Menangani pemuatan model, pra-pemrosesan input, inferensi, dan pasca-pemrosesan output.
    """
    def __init__(self, model_path, device=None):
        """
        Inisialisasi generator.
        
        Args:
            model_path (str): Path ke file model yang sudah dilatih (.pt).
            device (torch.device, optional): Device untuk menjalankan model (CPU atau CUDA). 
                                             Jika None, akan dideteksi otomatis.
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
            
        print(f"AlphaGenerator menggunakan device: {self.device}")

        # Muat arsitektur model (n_input_channels harus sama dengan saat training)
        self.model = MobileNetV2UNet(n_input_channels=6, n_output_channels=1, pretrained=False)
        
        # Muat bobot yang sudah dilatih
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        # Pindahkan model ke device yang dipilih
        self.model.to(self.device)
        
        # Setel model ke mode evaluasi. Ini sangat penting!
        # Menonaktifkan dropout, batch norm updates, dll.
        self.model.eval()

    def _preprocess(self, inputs):
        """Mengubah daftar array NumPy menjadi tensor PyTorch yang siap untuk model."""
        # Tumpuk semua peta input menjadi satu array multi-channel
        # Urutan harus SAMA PERSIS dengan saat training!
        stacked_input = np.stack(inputs, axis=0) # Menghasilkan (C, H, W)
        
        # Konversi ke tensor, tambahkan batch dimension, dan pindahkan ke device
        input_tensor = torch.from_numpy(stacked_input).float().unsqueeze(0).to(self.device)
        return input_tensor

    def _postprocess(self, output_tensor):
        """Mengubah tensor output dari model kembali ke array NumPy."""
        # Hapus batch dan channel dimension, pindahkan ke CPU, dan konversi ke NumPy
        alpha_map = output_tensor.squeeze().cpu().numpy()
        return alpha_map

    def generate(self, smoothed_current_weight, warped_prev_ema, optical_flow, 
                 flow_confidence_map, disocclusion_mask):
        """
        Menghasilkan alpha map menggunakan model ML.

        Returns:
            np.ndarray: Alpha map yang dihasilkan oleh model.
        """
        # Pastikan semua input memiliki tipe data yang benar dan tangani kasus None
        if flow_confidence_map is None:
            flow_confidence_map = np.zeros_like(smoothed_current_weight, dtype=np.float32)

        # Siapkan daftar input sesuai urutan yang diharapkan model
        model_inputs = [
            smoothed_current_weight,
            warped_prev_ema,
            optical_flow[..., 0],
            optical_flow[..., 1],
            flow_confidence_map,
            disocclusion_mask.astype(np.float32)
        ]
        
        # Lakukan pra-pemrosesan
        input_tensor = self._preprocess(model_inputs)

        # Jalankan inferensi (tanpa menghitung gradien untuk efisiensi)
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
            
        # Lakukan pasca-pemrosesan
        alpha_map = self._postprocess(output_tensor)
        
        return alpha_map