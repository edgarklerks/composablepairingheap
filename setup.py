from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


def read_requirements_txt():
    fh = parse_requirements("requirements.txt",session=PipSession());
    return [str(ir.req) for ir in fh]


setup(
     name="composablepairingheap",
     version="0.3.3",
     author="Edgar Klerks",
     author_email="edgar.klerks@gmail.com",
     description="A datastructure, which can be composed with another datastructure to yield a hybrid between the two",
     packages=find_packages('src'),
     package_dir={'':'src'},
     url="http://github.com/edgarklerks/composablepairingheap",
     package_data={'':["src/*.md", "src/*.txt","*.txt","*.md"]},
     tests_require=['pytest'],
     test_suite="tests",
     setup_requires=['pytest-runner'],
     cmdclass={'test':PyTest},
     install_requires=read_requirements_txt(),
 )
