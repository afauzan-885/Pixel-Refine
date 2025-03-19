<p align="center"><img src="UI/resources/image/Logo_Pixel_Refine.png" width="200" alt="Logo Pixel Refine"></p>

## Introduction

Pixel Refine is designed to reduce noise in images. Inspired by the image processing techniques used in Google Pixel cameras, Raw+ Kandao, Burst.photo, and PhotoAcute 3.

This app was created to address the shortcomings of stock smartphone camera processing (old smartphones), Raw+ Kandao (which limits to 16 images), Burst.photo (which was exclusive to the MacOS ecosystem), and PhotoAcute 3 (a great software that has been discontinued).

This app is expected to bridge the gap between professional cameras (DSLR or Mirrorless) and the computational photography capabilities of smartphone cameras.

## Supported Image Formats

| Format Gambar                | Status             |
| ---------------------------- | ------------------ |
| **JPG**                    | ✅ Supported        |
| **TIFF**                   | ✅ Supported        |
| **PNG**                    | ✅ Supported        |
| **DNG**                    | ❌ Not Supported   |

> Note: Support for DNG formats may be added in future updates..

## Sample Images

Below are some sample images processed (left: Original, Right: Processed):

<p align="center">
  <img src="sample/afternoon atmosphere iso40 (1per110).jpg" width="400" alt="Afternoon Atmosphere">
</p>

<p align="center">
  <img src="sample/Extreme low light iso 4000 1,3ss.jpg" width="400" alt="Extreme Low Light">
</p>

<p align="center">
  <img src="sample/moonlight iso1000 (1per25).jpg" width="400" alt="Moonlight">
</p>

<p align="center">
  <img src="sample/traditional market at dawn iso 400 (1per35).jpg" width="400" alt="Traditional Market at Dawn">
</p>

## Algorithms

Following is a list of algorithms used in the process:

### **1. Alignment**
- **Farneback Optical Flow**:
  - Very precise at the pixel level and works well in low light conditions.
  - Fairly fast and able to handle local motion within the frame.
  - Weak against significant differences between frames.
- **AKAZE**:
  - Advanced algorithm that excels at handling large differences between images.
  - Ideal for images with high deformation or significant variations.
- **ORB (Oriented FAST and Rotated BRIEF)**:
  - Very fast and suitable for most conditions.
  - Not as robust when handling large differences between images.

### **2. Super Resolution**
- **Interpolation**: Increases image resolution based on interpolation technique, slightly improves image detail.

### **3. Denoising**
- **Average**: Reduces noise by averaging pixel values across multiple frames.
- **Median**: Uses the median of pixel values for better noise reduction while preserving edges.
- **Similarity**: Special algorithm designed to enhance detail while suppressing noise based on pixel similarity to prevent motion artifacts, highly robust to large movements.

**(This program is still under development and has many flaws)**
