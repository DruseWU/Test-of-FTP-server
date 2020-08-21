from ftplib import FTP
import time
import pytest
import os
import csv
import datetime
from math import ceil

HOST = 'speedtest.tele2.net'
file_to_download = ['5MB.zip','512KB.zip','50MB.zip','2MB.zip','3MB.zip','20MB.zip','200MB.zip','1MB.zip','1KB.zip','10MB.zip','100KB.zip','100MB.zip']

def download_file_from_FTP(filename, downloading_path, ftp_object):
    """
    Function download file with name = filename to path = downloading_path
    """
    with open(downloading_path + filename, 'wb') as downloading_file:
        downloading_startime = time.time()
        server_feedback = ftp_object.retrbinary('RETR ' + filename, downloading_file.write)
        downloading_time = time.time() - downloading_startime
        file_size = os.path.getsize(downloading_path + filename)
    downloading_speed = file_size / downloading_time
    return server_feedback, downloading_speed

def upload_file_on_FTP(filename, filepath, ftp_object):
    """
        Function upload file with name = filename from path = filepath
    """
    with open(filepath + filename, 'rb') as uploading_file:
        uploading_startime = time.time()
        server_feedback = ftp_object.storbinary('STOR ' + 'upload/' + filename, uploading_file)
        uploading_time = time.time() - uploading_startime
        file_size = os.path.getsize(filepath + filename)
    uploading_speed = ceil(file_size / uploading_time)
    return server_feedback, uploading_speed

def csv_writer(data):
    """
    Fuction write download and upload speed data to file speed_test.csv
    """
    with open('speed_test.csv', "a", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)

@pytest.fixture(scope = 'module')
def server_connection(request):
    """
    Fixture to connect to server during testing
    """
    ftp = FTP(HOST)
    ftp.login()

    def fin():
        ftp.close()

    request.addfinalizer(fin)
    return ftp

def setup_module():
    """
    This function write date of test to speed_test.csv when test starts
    """
    now = datetime.datetime.now()
    with open('speed_test.csv', "a", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['Test ' + now.strftime("%d-%m-%Y %H:%M")])

@pytest.fixture(scope = 'module')
def temporary_directory(tmpdir_factory):
    """
    Function to create temporary directory for downloaded files
    """
    filepath = tmpdir_factory.mktemp('downloads')
    return filepath.strpath + '/'

def test_connecting_to_sever(server_connection):
    ftp = server_connection
    server_feedback = ftp.getwelcome()
    assert '220' in server_feedback

def test_dowloading_file(server_connection, temporary_directory):
    ftp = server_connection
    downloading_path = temporary_directory
    filename = '100KB.zip'
    server_feedback, downloading_speed = download_file_from_FTP(filename,downloading_path,ftp)
    assert '226' in server_feedback

def test_uploading_file(server_connection, temporary_directory):
    ftp = server_connection
    filepath = temporary_directory
    filename = '100KB.zip'
    server_feedback, uploading_speed = upload_file_on_FTP(filename, filepath, ftp)
    assert '226' in server_feedback

@pytest.mark.parametrize('filename',file_to_download)
def test_downloading_speed(server_connection,filename,temporary_directory):
    ftp = server_connection
    downloading_path = temporary_directory
    server_feedback, downloading_speed = download_file_from_FTP(filename,downloading_path,ftp)
    csv_writer([[filename, downloading_speed,'download']])
    assert '226' in server_feedback

@pytest.mark.parametrize('filename',file_to_download)
def test_uploading_speed(server_connection,filename,temporary_directory):
    ftp = server_connection
    filepath = temporary_directory
    server_feedback, uploading_speed = upload_file_on_FTP(filename,filepath,ftp)
    csv_writer([[filename, uploading_speed, 'upload']])
    assert '226' in server_feedback