import cv2

build_info = cv2.getBuildInformation()
print(build_info)

# Cari kata "OpenMP" dalam output
if "OpenMP:                    YES" in build_info:
    print("OpenCV sudah dikompilasi dengan dukungan OpenMP.")
else:
    print("OpenCV tidak dikompilasi dengan dukungan OpenMP.")
