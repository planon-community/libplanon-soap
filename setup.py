import setuptools

setuptools.setup(name='libplanon',
      version='1.0.0',
      description='Python module for interacting with Planon SOAP web services',
      url='',
      author='Dartmouth College Business Transformation Team',
      author_email='businesstransformation@groups.dartmouth.edu',
      packages=['libplanon'],
      license='MIT',
      install_requires = ["requests", "zeep"],
      zip_safe=False)
