# Convertcloud

Simple pointcloud format converter. Supported conversions, from and to:

.pcd (ascii)
.ply (ascii)
.xyz (ascii)
.zdf (ascii)

Use from shell: 
```sh
$ convertcloud original.format1 converted.format2 
 
```

Use from python:
```python
import convertcloud

cvc = convertcloud.Converter()
cvc.load_points("original.format1")
cvc.convert("converted.format2")
```

