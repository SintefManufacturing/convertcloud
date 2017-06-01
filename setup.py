from setuptools import setup

setup(name="convertcloud",
      version="0.0.1",
      description="Pointcloud format converter",
      author="Alvaro Capellan",
      author_email="capellan.alvaro@gmail.com",
      url="https://github.com/alvcap/convertcloud",
      packages=["convertcloud"],
      provides=["convertcloud"],
      license="GNU General Public License v3",

      entry_points={"console_scripts":
          ["convertcloud = convertcloud.convertcloud:main"]
                    },
      classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Topic :: Scientific/Engineering"
      ]
      )
