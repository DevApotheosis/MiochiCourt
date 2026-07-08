from setuptools import setup, Extension

fast_search_module = Extension(
    'fast_search',
    sources=['src/core/fast_search.c'],
    include_dirs=['src/core'],
    extra_compile_args=['/O2', '/W3'],
)

setup(
    name='fast_search',
    version='1.0',
    description='Fast search and evidence management module',
    ext_modules=[fast_search_module],
)