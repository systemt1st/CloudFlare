# https://github.com/systemt1st
# -*- coding:utf-8 -*-
import time
import requests
import json
import datetime




def get_domains(filename):
    with open(filename, 'r') as file:
        domains = []
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 1:
                domains.append((parts[0], 'true'))
            elif len(parts) == 2:
                domains.append((parts[0], parts[1]))
            else:
                print(f"警告：域名文件中的无效行：{line.strip()}")
    return domains


def get_ips(filename):
    with open(filename, 'r') as file:
        ips = [line.strip() for line in file.readlines()]
    return ips


def get_zone_id(domain, headers):
    url = f'https://api.cloudflare.com/client/v4/zones?name={domain}'
    response = requests.get(url, headers=headers)
    result = response.json()
    if result['success'] and result['result']:
        return result['result'][0]['id']
    return None


def delete_all_dns_records(zone_id, headers):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    response = requests.get(url, headers=headers)
    records = response.json()['result']

    for record in records:
        record_id = record['id']
        delete_url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
        r = requests.delete(delete_url, headers=headers)
        if r.status_code == 200:
            print(f"删除记录 {record['name']} 成功")
        else:
            print(f"删除记录 {record['name']} 失败: {r.json()}")

# 禁用自动 HTTPS 重写
def disable_https_rewrites(zone_id, headers):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/automatic_https_rewrites'
    data = {'value': 'off'}
    response = requests.patch(url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        print(f"自动 HTTPS 重写已禁用。")
    else:
        print(f"禁用自动 HTTPS 重写失败: {response.json()}")


def main():
    print("Systemt1st \n")
    # email = input('请输入Cloudflare账号邮箱: ')
    # api = input('请输入Cloudflare API密钥: ')
    # domains_per_ip = int(input('请输入每多少个域名绑定一个IP: '))
    # domains_file = input('请输入域名文件路径: ')
    # ips_file = input('请输入IP地址文件路径: ')

    email = 'xxx@gmail.com'
    api = 'xxx'
    domains_per_ip = int(input('请输入每多少个域名绑定一个IP: '))
    domains_file = '1.txt'
    ips_file = '2.txt'

    domain_list = get_domains(domains_file)
    ip_list = get_ips(ips_file)

    if not domain_list or not ip_list:
        print("域名或IP地址文件为空，请检查文件内容。")
        exit()

    headers = {'X-Auth-Email': email,
               'X-Auth-Key': api,
               'Content-Type': 'application/json'}

    ip_index = 0
    for i, (domain, proxied) in enumerate(domain_list):
        proxied = proxied.strip().lower() == 'true'
        if i % domains_per_ip == 0 and i != 0:
            ip_index += 1
            if ip_index >= len(ip_list):
                ip_index = 0

        vps = ip_list[ip_index]
        names = ['@','*','www']
        # names = ['@','www']
        # names = ['*']

        zone_id = get_zone_id(domain, headers)
        if zone_id is None:
            r = requests.get('https://api.cloudflare.com/client/v4/accounts?page=1&per_page=20&direction=desc',
                             headers=headers)
            account_id = r.json()['result'][0]['id']
            data1 = {'name': domain, 'account': {'id': account_id, 'name': email}, 'jump_start': False}
            url1 = 'https://api.cloudflare.com/client/v4/zones'
            r = requests.post(url1, headers=headers, data=json.dumps(data1))
            r_result = r.json()

            if not r_result['success']:
                print(f"添加域名 {domain} 失败: {r_result['errors']}")
                continue

            zone_id = r_result['result']['id']
            ns1 = r_result['result']['name_servers'][0]
            ns2 = r_result['result']['name_servers'][1]
        else:
            print(f"域名 {domain} 已存在，获取现有域名信息")
            url_ns = f'https://api.cloudflare.com/client/v4/zones/{zone_id}'
            r = requests.get(url_ns, headers=headers)
            r_result = r.json()
            ns1 = r_result['result']['name_servers'][0]
            ns2 = r_result['result']['name_servers'][1]

        # 删除所有DNS记录
        delete_all_dns_records(zone_id, headers)

        # 添加新的DNS记录
        for name in names:
            data2 = {'type': 'A',
                     'name': name,
                     'content': vps,
                     'ttl': 1,
                     'priority': 0,
                     'proxied': proxied
                     }
            url2 = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
            r = requests.post(url2, data=json.dumps(data2), headers=headers)

        print(f'恭喜! {domain} 添加成功.')

        # 修改SSL模式
        url3 = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ssl'
        r = requests.patch(url3, data=json.dumps({'value': 'flexible'}), headers=headers)

        # # 禁用自动 HTTPS 重写
        # disable_https_rewrites(zone_id, headers)

        print(f'ip: {vps}')
        print(f'nameserver1: {ns1}')
        print(f'nameserver2: {ns2}')
        print('--------------------------------------')
        d = datetime.datetime.now()
        with open('解析信息.txt', 'a') as f:
            f.write(f'域名：{domain}\n')
            f.write(f'ip: {vps}\n')
            f.write(f'email: {email}\n')
            f.write(f'ns1: {ns1}\n')
            f.write(f'ns2: {ns2}\n')
            f.write(f'添加日期: {d}\n')
            f.write('============================\n')

        time.sleep(10)


if __name__ == '__main__':
    main()
