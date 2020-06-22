"""
学习目标:m3u8文件的下载 合成,实现免费视频的下载保存.
为了不给人家站点造成压力(善待别人就是善待自己),所以选择了**站点的视频来练习(不要在意视频内容)
"""

import requests, re
#python 3.7+ 需要pip install pycryptodome
from Crypto.Cipher import AES  
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# 解除InsecureRequestWarning错误提示
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) 

url = 'https://www.selala2.com/index.php?s=/vod-play-id-70052-sid-1-pid-.html'
headers = {
	'Origin': 'https://www.selala2.com',
	'Referer': 'https://www.selala2.com/index.php?s=/vod-play-id-69958-sid-1-pid-.html',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}
r = requests.get(url, headers, timeout=10).text
urls = re.findall('<source src= "(.*?)" type=',r)

key = urls[0][:-10]+'500kb/hls/key.key' # key.key文件 链接
key = requests.get(key,verify=False).content # 取得key.key文件内容 下面要用到所以用二进制的所以用content

res = urls[0][:-10]+'500kb/hls/index.m3u8'  # index.m3u8文件 链接
try:
	#取分割小文件名
	name = requests.get(res, verify=False).text
	name = name.replace('\n','')
	names = re.findall(',(.*?)#EXTINF',name) # 取得ts文件信息
	print('总共有%s个文件' % str(len(names)-1))
	y = 0
	for i in names:
		if i != 'URI="key.key"':
			y += 1
			print('正在下载第%s个文件' % y)
			ts = res[:-10]+i # 取得单个ts文件地址
			# 开始解密下载
			#  # 解密，new有三个参数，
			# 第一个是秘钥（key）的二进制数据，
			# 第二个使用下面这个就好
			# 第三个IV在m3u8文件里URI后面会给出，如果没有，可以尝试把秘钥（key）赋值给IV
			sprytor = AES.new(key, AES.MODE_CBC, IV=key)
			ts = requests.get(ts, verify=False).content
			# 密文长度不为16的倍数,则添加b"0"知道长度为16的倍数 (本练习站点刚好16位不需用到)
			#while len(ts) % 16 != 0:
			#	ts += b"0"
			print('正在解密'+i)
			# 写入mp4文件
			with open('123.mp4', 'ab') as f:
				# decrypt方法的参数需要为16的倍数，如果不是，需要在后面补二进制"0"
				f.write(sprytor.decrypt(ts))
				print("保存成功:"+i)
	print('下载完成!')
except:
	raise '获取ts文件失败'

"""
待解决问题:运行后,经常会假死,需要回车继续运行
"""
