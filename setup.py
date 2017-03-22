from setuptools import setup

setup(name="convertcloud",
      version="0.0.1",
      description="Simple pointcloud converter",
      author="alvcap",
      author_email="kape013@gmail.com",
      url='https://github.com/alvcap/pointcloud-converter',
      packages=["converter"],
      provides=["converter"],
      license="GNU General Public License v3",

      entry_points={'console_scripts':
          ['convertcloud = converter.converter:main']
                    },
      classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Topic :: Office/Business :: Financial"
      ]
      )
