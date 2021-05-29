import os
import re
import subprocess
import sys
import zipfile

import click
import requests
import xml.etree.ElementTree as ET

allure_version = '2.13.8'


class XmlVersion(object):
    """
    Class for working with versions from xml file.
    """
    def __init__(self, file):
        self.__tree = ET.fromstring(file)

    def get_version(self):
        """

        :returns: Release version in string format.
        """
        return {child.tag: child.text for child in self.__tree.iter("release")}["release"]

    def get_supported_versions(self):
        """

        :returns: Release versions in list format.
        """
        return {child.tag: [version.text for version in child] for child in self.__tree.iter("versions")}["versions"]


class File(object):

    def __init__(self, stream):
        self.content = stream.content
        self.__stream = stream
        self.__temp_name = "driver"

    @property
    def filename(self) -> str:
        try:
            filename = re.findall("filename=(.+)", self.__stream.headers["content-disposition"])[0]
        except KeyError:
            filename = f"{self.__temp_name}.zip"
        except IndexError:
            filename = f"{self.__temp_name}.exe"

        if '"' in filename:
            filename = filename.replace('"', "")

        return filename


class Archive(object):

    def __init__(self, path: str):
        self.file_path = path

    def unpack(self, directory):
        if self.file_path.endswith(".zip"):
            return self.__extract_zip(directory)

    def __extract_zip(self, to_directory):
        archive = zipfile.ZipFile(self.file_path)
        try:
            archive.extractall(to_directory)
        except Exception as e:
            if e.args[0] not in [26, 13] and e.args[1] not in ['Text file busy', 'Permission denied']:
                raise e
        return archive.namelist()


def get_allure_realise_version():
    """

    :returns: Release version in string format from request.
    """
    response = requests.get(
        f'https://repo1.maven.org/maven2/io/qameta/allure/allure-commandline/maven-metadata.xml',
        stream=True)
    return XmlVersion(response.text).get_version()


def get_supported_versions():
    """

    :returns: Release versions in list format from request.
    """
    response = requests.get(
        f'https://repo1.maven.org/maven2/io/qameta/allure/allure-commandline/maven-metadata.xml',
        stream=True)
    return XmlVersion(response.text).get_supported_versions()


def is_allure_version_old(current_version: str, release_version: str):
    """

    :prop: current_version: Allure current version.
    :prop: release_version: Allure release version from repository.
    """
    if int(current_version.replace(".", "")) < int(release_version.replace(".", "")):
        return True
    else:
        return False


def download(version=allure_version):
    """

    :prop: version: Allure version for downloading.
    """
    supported_versions = get_supported_versions()
    if version in supported_versions:
        response = requests.get(
            f'https://repo1.maven.org/maven2/io/qameta/allure/allure-commandline/{version}'
            f'/allure-commandline-{version}.zip',
            stream=True)
        return File(response)
    else:
        raise ValueError(f"Version {version} is not supported.\nSupported versions are : {get_supported_versions()}")


def save_file(file: File, directory: str):
    os.makedirs(directory, exist_ok=True)

    archive_path = f"{directory}{os.sep}{file.filename}"
    with open(archive_path, "wb") as code:
        code.write(file.content)
    return Archive(archive_path)


is_windows = sys.platform.startswith('win')
dir_name = os.path.dirname(sys.path[0])
root_path = os.path.join(dir_name, ".dist")
allure_report_dir = "allure-report"

binary_name = "allure"
if is_windows:
    binary_name = f"{binary_name}.bat"

binary_path = f'{root_path}/allure-{allure_version}/bin/{binary_name}'


def run(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout, stderr)


def check_allure_binary():
    if not os.path.exists(binary_path):
        realise_version = get_allure_realise_version()
        is_version_old = is_allure_version_old(allure_version, realise_version)
        file = download(version="2.14.1") if is_version_old else download()
        archive = save_file(file, root_path)
        archive.unpack(root_path)


@click.group()
@click.version_option("1.0.0")
def main():
    """Python Allure CLI"""
    pass


@main.command()
@click.argument('dir', required=True)
def generate(**kwargs):
    """generate report"""
    check_allure_binary()
    run([binary_path, 'generate', f"{kwargs['dir']}", '-o', allure_report_dir, '--clean'])


@main.command()
@click.argument('dir', required=True)
def serve(**kwargs):
    """serve report"""
    check_allure_binary()
    run([binary_path, 'serve', f"{kwargs['dir']}", '-o', allure_report_dir, '--clean'])


@main.command()
@click.argument('dir', required=False)
def open(**kwargs):
    """serve report"""
    report_dir = kwargs['dir']
    if not report_dir:
        report_dir = os.path.join(dir_name, allure_report_dir)

    check_allure_binary()
    run([binary_path, 'open', report_dir])


if __name__ == "__main__":
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("Allure")
    main()
