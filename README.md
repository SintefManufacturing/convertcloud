# Convertcloud

Simple pointcloud format converter. Supported conversions, from and to:

.pcd (ascii)
.ply (ascii)
.xyz (ascii)
.zdf (ascii)

Use from shell: 
```sh
$ cvc original.format1 converted.format2 
 
```

Use from python:
```python
import convertcloud as cvc

conv = cvc.Converter()
conv.load_points("original.format1")
conv.convert("converted.format2")
```

