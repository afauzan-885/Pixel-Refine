<p align="center"><img src="UI/resources/image/Logo_Pixel_Refine.png" width="200" alt="Logo Pixel Refine"></p>

## Introduction

Pixel Refine is designed to create a program inspired by the image processing techniques used in the Google Pixel camera, Raw+ Kandao, Burst.photo, and PhotoAcute 3.

This application is made to overcome the shortcomings of the Google Pixel's native camera processing (or Android smartphone cameras), Raw+ Kandao (which is limited to a maximum of 16 images), Burst.photo (which is exclusive to the MacOS ecosystem), and PhotoAcute 3 (a great software that has been discontinued).

The processing in this application is expected to bridge the gap between professional cameras (DSLR or Mirrorless) and the computational photography capabilities experienced by smartphone cameras.

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

## Algorithms

Pixel Refine uses several advanced algorithms for image processing. Here is a list of the algorithms used in the process:

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

### **2. **Super Resolution**
- **Interpolation**: Increases image resolution based on interpolation technique, slightly improves image detail.

### **3. Denoising**
- **Average**: Reduces noise by averaging pixel values ​​across multiple frames.
- **Median**: Uses the median of pixel values ​​for better noise reduction while preserving edges.
- **Similarity**: Special algorithm designed to enhance detail while suppressing noise based on pixel similarity to prevent motion artifacts, highly robust to large movements.

**(This program is still under development and has many flaws. Beta release for public testing)**
