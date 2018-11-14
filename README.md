# 文件检索微服务  
按照不同条件检索文件系统里面的文件  

## 实现功能  
* 判断url是文件路径还是文件夹路径还是错误路径  
* 输入多个文件名,返回文件一共占用多大存储  
* 输入多个文件名,程序能够把多个文件名压缩到一个zip中.然后把这个zip文件的地址返回  
* 输入多个文件名,如果这些文件加起来大于20M,这按照20M为最大压缩文件,压缩成多个zip文件,并把这些zip文件的地址返回  
* 编写接口

## 函数介绍
```human_readable(plain_size)```： 将原始大小转换为带有对应单位的可视大小  

```is_file_path()```： 判断url是文件路径还是文件夹路径还是错误路径  

```get_total_size()```： 输入多个文件名,返回文件一共占用多大存储  

```get_zip_url()```： 输入多个文件名,返回文件一共占用多大存储，程序能够把多个文件名压缩到一个zip中.然后把这个zip文件的地址返回，如果这些文件加起来大于20M,这按照20M为最大压缩文件,压缩成多个zip文件,并把这些zip文件的地址返回

## 技术介绍
* ```import os  # 引入操作系统模块```
* ```import zipfile  # 用于压缩zip文件```
* ```import shutil  # 强制递归删除文件夹```
* ```import requests  # 获取json数据```
* ```import flask  # get/post接口请求```



@project: search    
@file: search.py  
@github: https://github.com/blank798466  
