# Cloudflare批量自动解析

## 概述

这个Python工具通过Cloudflare API实现多域名的自动化添加。它允许批量域名配置、DNS记录管理以及按照特定比例分配IP地址。

## 功能特点

- **批量域名管理**：一次操作添加和配置多个域名到Cloudflare
- **DNS记录管理**：清除现有记录并创建标准化的A记录
- **IP轮换分配**：根据可配置的比例将IP分配给域名
- **SSL配置**：自动将SSL设置配置为"灵活"模式
- **代理支持**：为每个域名提供可选的CDN代理配置

## 环境要求

- Python 3.x
- `requests`库

## 文件结构

- `1.txt` - 包含域名列表及可选代理设置
- `2.txt` - 包含要分配给域名的IP地址列表

## 配置说明

**域名文件格式：**
domain1.com,true domain2.com,false domain3.com
第二个参数（可选）表示是否启用Cloudflare代理。

**IP文件格式：**
192.168.1.1 192.168.1.2


运行脚本时，系统会提示您指定每个IP地址应分配给多少个域名。

## 输出结果

脚本会生成一个日志文件（`解析信息.txt`），其中包含每个操作的域名信息、分配的IP、名称服务器和时间戳。

## 注意事项

- 需要在脚本中更新Cloudflare邮箱和API密钥
- 脚本默认为`@`、`*`和`www`子域名创建A记录
- 脚本在操作之间包含10秒延迟，以避免API速率限制

## 安全提示

请妥善保管您的API凭据。切勿在公共代码库中分享您的API密钥。
