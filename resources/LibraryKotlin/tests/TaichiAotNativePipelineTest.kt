package org.pixelrefine.genericui

import org.pixelrefine.genericui.domain.aot.*
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/**
 * Pengujian Eksekusi Pipeline Taichi AOT di Kotlin
 * Menguji 4 Algoritma Berurutan (Demosaic -> Gaussian Blur -> Bilateral Filter -> Resize)
 * pada 3 Backend Native (CPU, VULKAN, CUDA).
 */
class TaichiAotNativePipelineTest {

    @Test
    fun testSequentialPipelineAcross3Backends() {
        val backends = listOf(
            AotArch.CPU to "CPU (LLVM Reference)",
            AotArch.VULKAN to "Vulkan (Cross-Platform GPU)",
            AotArch.CUDA to "CUDA (NVIDIA High-Performance GPU)",
        )

        // Dimensi frame sintetis 4K RAW Bayer (3840 x 2160)
        val width = 3840
        val height = 2160
        val rawByteSize = width * height * 4 // Float32 ~33.17 MB per frame

        // Buat Direct Memory Buffer CPU (Zero-Overhead Memory Pointer)
        val hostDirectBuffer = ByteBuffer.allocateDirect(rawByteSize).order(ByteOrder.nativeOrder())
        for (i in 0 until 1000) {
            hostDirectBuffer.putFloat(0.5f)
        }
        hostDirectBuffer.rewind()

        for ((arch, archDescription) in backends) {
            println("\n=======================================================")
            println("▶ MEMULAI PIPELINE 4 ALGORITMA PADA BACKEND: $archDescription")
            println("=======================================================")

            // 1. Inisialisasi Backend Runtime Native
            TaichiAot.init(arch = arch, device = 0)
            assertTrue(TaichiAot.isReady, "Backend $arch harus siap diinisialisasi")
            assertEquals(arch, TaichiAot.activeArch)
            println("✔ [INIT] Runtime terinisialisasi pada $arch (Device 0)")

            // 2. Upload Input ke VRAM GPU (Zero-Copy)
            val rawBayerGpu = TaichiAot.upload(
                buffer = hostDirectBuffer,
                width = width,
                height = height,
                channels = 1,
                dtype = AotDtype.FLOAT32
            )
            assertNotNull(rawBayerGpu)
            println("✔ [UPLOAD] Direct memory buffer diikat ke GPU ($width x $height x 1 channels, ~33.17 MB)")

            // --- ALGORITMA 1: Demosaicing (Hamilton Bayer -> RGB) ---
            println("-> [ALGO 1] Menjalankan Hamilton Demosaic (Bayer RGGB -> 3-Channel RGB)...")
            val rgbGpu = TaichiAot.demosaic(
                rawBayer = rawBayerGpu,
                algorithm = DemosaicAlgorithm.HAMILTON,
                bayerPattern = "rggb",
                returnGpu = true
            )
            assertTrue(rgbGpu is TaichiGpuBuffer)
            val demosaicedBuffer = rgbGpu as TaichiGpuBuffer
            println("   ↳ Selesai: Output resident di VRAM GPU (${demosaicedBuffer.width} x ${demosaicedBuffer.height})")

            // --- ALGORITMA 2: Gaussian Blur Smoothing ---
            println("-> [ALGO 2] Menjalankan Gaussian Blur (ksize=5x5, sigma=1.5)...")
            val blurredGpu = TaichiAot.gaussian_blur(
                src = demosaicedBuffer,
                ksize = Pair(5, 5),
                sigmaX = 1.5f,
                returnGpu = true
            )
            assertTrue(blurredGpu is TaichiGpuBuffer)
            val blurredBuffer = blurredGpu as TaichiGpuBuffer
            println("   ↳ Selesai: Output resident di VRAM GPU (${blurredBuffer.width} x ${blurredBuffer.height})")

            // --- ALGORITMA 3: Bilateral Filter Denoising ---
            println("-> [ALGO 3] Menjalankan Bilateral Grid Filter (d=9, sigmaColor=75, sigmaSpace=75)...")
            val denoisedGpu = TaichiAot.bilateral_filter(
                src = blurredBuffer,
                d = 9,
                sigmaColor = 75.0f,
                sigmaSpace = 75.0f,
                returnGpu = true
            )
            assertTrue(denoisedGpu is TaichiGpuBuffer)
            val denoisedBuffer = denoisedGpu as TaichiGpuBuffer
            println("   ↳ Selesai: Output resident di VRAM GPU (${denoisedBuffer.width} x ${denoisedBuffer.height})")

            // --- ALGORITMA 4: High-Quality Resize & Downsample ---
            val targetWidth = 1920
            val targetHeight = 1080
            println("-> [ALGO 4] Menjalankan Bilinear Resize 4K -> FHD ($targetWidth x $targetHeight)...")
            val resizedGpu = TaichiAot.resize(
                src = denoisedBuffer,
                dsize = Pair(targetWidth, targetHeight),
                interpolation = InterpolationMode.BILINEAR,
                returnGpu = false // Download hasil akhir ke CPU Direct Buffer
            )
            assertTrue(resizedGpu is ByteBuffer, "Hasil akhir di-download ke CPU Direct Buffer")
            val finalHostBuffer = resizedGpu as ByteBuffer
            println("   ↳ Selesai: Frame FHD ($targetWidth x $targetHeight) berhasil di-download ke host CPU (${finalHostBuffer.capacity()} bytes)")

            // 3. Bersihkan alokasi GPU VRAM
            rawBayerGpu.release()
            demosaicedBuffer.release()
            blurredBuffer.release()
            denoisedBuffer.release()
            TaichiAot.destroy()
            println("✔ [CLEANUP] Seluruh GPU VRAM dan context $arch dibebaskan secara bersih.\n")
        }

        println("=======================================================")
        println("★ SELURUH 4 ALGORITMA PADA 3 BACKEND (CPU, VULKAN, CUDA) BERHASIL DIEKSEKUSI NATIVE DI KOTLIN!")
        println("=======================================================")
    }
}
