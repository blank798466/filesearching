# coding=utf-8
"""
@project: search
@author: Zheng Jiangwei
@file: search.py
@time: 2018-10-24 10:56:10
@github: https://github.com/blank798466
"""
import os  # 引入操作系统模块
import shutil  # 强制递归删除文件夹
import zipfile  # 用于压缩zip文件
import requests  # 获取json数据
import flask  # get/post接口请求
from flask import request  # request请求
from flask import jsonify  # json格式转换


class FileSearching(object):
    """
        文件检索微服务
        按照不同条件检索 文件系统里面的文件

        Attributes:
            path: 记录需要检索的文件源路径.
            service_name: 当前服务的名字,也就是压缩包的命名规则
            dirs: 文件夹路径
            files: 文件路径
            errors: 非正确路径
    """
    def __init__(self, path, service_name):
        self.path = path  # 总路径
        self.service_name = service_name  # 服务名

        dirs, files, errors = self.is_file_path()
        self.dirs = dirs  # 文件夹路径
        self.files = files  # 文件路径
        self.errors = errors  # 非正确路径

    @staticmethod
    def human_readable(plain_size):
        """
        将原始大小转换为带有对应单位的可视大小

        :param plain_size: 原始文件夹的大小,int类型
        :return: 带有单位的大小,str类型
        """
        code = 1024
        # plain_size = float(plain_size)
        if plain_size <= code:
            return str(plain_size) + 'B'
        if plain_size <= code ** 2:
            return str(plain_size / code) + 'K'
        if plain_size <= code ** 3:
            return str(plain_size / code / code) + 'M'
        if plain_size <= code ** 4:
            return str(plain_size / code / code / code) + 'G'

    def is_file_path(self):
        """
        判断url是文件路径还是文件夹路径

        :return:
            paths: 文件夹路径数组,list类型
            files: 文件路径数组,list类型
        """
        dirs = []
        files = []
        errors = []
        for path in self.path:
            if os.path.isdir(path):
                dirs.append(path)
            elif os.path.isfile(path):
                dirs.append(path)
            else:
                errors.append(path)
        return dirs, files, errors

    def get_total_size(self):
        """
        输入多个文件名,返回文件一共占用多大存储,

        :return:
            total_size: 多个文件夹的总存储大小
        """
        total_size = 0

        for path in self.dirs:
            for root, filename, pathname in os.walk(path):
                # print '/'.join([root, str(filename), str(pathname)])
                for name in pathname:
                    url = os.path.join(root, name)
                    # print url
                    total_size += os.path.getsize(url)

        for path in self.files:
            total_size += os.path.getsize(path)

        return self.human_readable(total_size)

    def get_zip_url(self):
        """
        输入多个文件名,返回文件一共占用多大存储
        输入多个文件名,程序能够把多个文件名压缩到一个zip中.然后把这个zip文件的地址返回
        输入多个文件名,如果这些文件加起来大于20M,这按照20M为最大压缩文件,压缩成多个zip文件,并把这些zip文件的地址返回

        :return:
            total_size: 多个文件夹的总存储大小
            zip_url: zip文件的地址, list数组类型,至少为一个
        """
        total_size = 0  # 压缩包总大小
        zip_urls = []  # 压缩包或分卷压缩的压缩包路径
        max_size = 20 * 1024 * 1024  # 最大压缩包大小

        '''压缩文件夹'''
        zip_name = self.service_name + '.zip'  # 新建压缩包,放文件进去,若压缩包已经存在,将覆盖.可选择用a模式,追加.
        azip = zipfile.ZipFile(zip_name, 'w')

        for path in self.dirs:
            for root, filename, pathname in os.walk(path):
                # print '/'.join([root, str(filename), str(pathname)])
                for name in pathname:
                    url = os.path.join(root, name)  # 将当前路径与当前路径下的文件名组合，就是当前文件的绝对路径
                    # print url
                    total_size += os.path.getsize(url)
                    azip.write(url)

        for path in self.files:
            total_size += os.path.getsize(path)
            azip.write(path)

        azip.close()

        '''分卷压缩'''
        tmp_file = os.path.join(os.getcwd(), zip_name)  # 临时存储的压缩包路径
        zip_file = os.path.join(os.getcwd(), self.service_name)  # 存储压缩包和分卷压缩的文件夹路径

        # 创建存储压缩文件的文件夹
        if os.path.exists(zip_file):
            # os.removedirs(zip_file)  # 删除空文件夹
            shutil.rmtree(zip_file)  # 强制删除文件夹
        os.mkdir(zip_file)

        os.system("mv %s %s" % (tmp_file, zip_file))  # 移动临时压缩包到文件夹
        print os.listdir(zip_file)

        # 分卷压缩判断
        zip_url = os.path.join(zip_file, zip_name)  # 最终存储的压缩包路径
        if os.path.getsize(zip_url) <= max_size:
            zip_urls.append(zip_url)  # 直接进行压缩
        else:
            os.system("zip -s %s %s --out %s/ziptest.zip" %
                      (self.human_readable(max_size), zip_url, zip_file))  # 分卷压缩
            os.remove(zip_url)  # 删除总压缩包
            # 递归将分卷压缩包路径存储进zip_url中
            names = os.listdir(zip_file)
            for name in names:
                zip_urls.append(os.path.join(zip_file, name))

        return self.human_readable(total_size), zip_urls

    def get_error_url(self):
        """
        获取错误url
        """
        return self.errors


# 构建web框架
server = flask.Flask(__name__)


@server.route('/search', methods=['get'])
def search():
    path_url = request.values.get('path_url')
    s_name = request.values.get('service_name')
    is_zip = request.values.get('is_zip')
    res = FileSearching(path=[path_url], service_name=s_name)
    if is_zip == '0':
        return jsonify({'zip_size': res.get_total_size(), 'error_urls': res.get_error_url()})
    elif is_zip == '1':
        res_zip = res.get_zip_url()
        return jsonify({'zip_size': res_zip[0], 'zip_urls': res_zip[1], 'error_urls': res.get_error_url()})


if __name__ == '__main__':
    server.run(debug=True, port=8888, host='127.0.0.1')  # 指定端口、host,0.0.0.0代表不管几个网卡，任何ip都可以访问
    # test
    # 访问http://127.0.0.1:8888/search?path_url=/home/sev1/IdeaProjects/FileSearch-master&service_name=zjw&is_zip=0
    # 则可显示对应输出数据
