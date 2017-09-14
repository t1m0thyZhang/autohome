# -*- decoding: utf8 -*-
import os
import sys
from sync_file_to_mysql import sync_file_to_mysql


def sync_folder_to_mysql(folder):
    for file in os.listdir(folder):
        file = os.path.join(folder, file)
        if not os.path.isfile(file):
            continue
        print file
        sync_file_to_mysql(file)

def main():
    folder = sys.argv[1]
    print "process folder: %s" % folder
    sync_folder_to_mysql(folder)


if __name__ == '__main__':
    """
        /usr/local/python2.7/bin/python sync_folder_to_mysql.py folder
        同步文件夹内文件内容到mysql，深度为1
    """
    main()


