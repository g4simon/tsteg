#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: g4_simon
# @Date:   2022-05-26 12:10:55
# @Last Modified by:   g4_simon
# @Last Modified time: 2022-10-08 13:27:18
# @email: g4_simon@foxmail.com
# 菜，轻喷
# 为方便用户使用，在参数上“尽量”和zsteg保持一致，至于为什么叫tsteg，咱也不知道，咱也不敢问。
# 目前只完成了lsb的部分，wbstego和其他隐写还在继续做(wbstego可能要鸽了，不太会)
# 强烈感谢@cheyenne @阿狸 师傅们对算法和脚本思路的无私帮助

DEBUG=False


import argparse
from core.tsteg import CONFIGURE,TSTEG


if __name__ == "__main__":
	#Entrypoint
	Parser = argparse.ArgumentParser(#description='最痛苦的是什么呢，你恰巧有那么一点天赋，够你去觊觎天才们那片殿堂，却不够你进入。你在门前徘徊，隐隐约约看到殿堂内透出的光，却敲不开那扇门。你颓然而坐，以为这就是人世间最大的遗憾，却隐隐约约听到殿堂内传来一声叹息：我好菜啊',
						)
	
	Parser.add_argument('filename',
						help='path to file.')
	Parser.add_argument('-c','--colors',
						dest='COLORS',
						default='rgb',
						help='颜色通道（R/G/B/A）或者任意组合，可以用逗号进行分隔。如：r,g,b,a,rg,bgr,rgba,...')
	Parser.add_argument('-l','--limit',
						dest='LIMIT',
						type=int,
						default=1024,
						help='解码字节长度, 0 = 不限制 (default: 1024)')
	Parser.add_argument('-o','--order',
						dest='XY',
						default='xy',
						help='像素解压顺序 (default: \'ALL\').大写表示逆序，如: ALL,xy,yx,XY,YX,xY,Xy...')
	
	Config_Planes=Parser.add_mutually_exclusive_group()
	Config_Planes.add_argument('-bc','--bitcount',
						dest='BITCOUNT',
						default='1,2,3,4',
						help='每像素最低有效位数，如3相当于-bp参数的210，也可以使用逗号进行分隔，如\'1,3,5\'或使用范围\'1-8\'. 对应zsteg的-b参数，为符合zsteg用户习惯，保留\'00001110\'的掩码形式表示.')
	Config_Planes.add_argument('-bp','--bitplane',
						dest='BITS',
						help='bit有效位顺序,可以使用逗号进行分隔指定范围，如\'013,123,02,31\'，或使用范围\'0-3\'(可能策略数量过多)，也可以使用单个字符串代表有效位顺序，如乱序\'1024\'.')
	
	Config_SignificantBit = Parser.add_mutually_exclusive_group()
	Config_SignificantBit.add_argument('--lsb',
						dest='SIGNIFICANTBIT',
						action='store_const',
						const='LSB',
						default='ALL',
						help='解码时先填充最低字节.该选项默认开启.')
	Config_SignificantBit.add_argument('--msb',
						dest='SIGNIFICANTBIT',
						action='store_const',
						const='MSB',
						help='解码时先填充最高字节.该选项默认开启.')

	Config_Priority = Parser.add_mutually_exclusive_group()
	Config_Priority.add_argument('--cf','--colorfirst',
						dest='PRIORITY',
						action='store_const',
						default='COLOR',
						const='COLOR',
						help='颜色维度优先，如颜色通道\'RGB\'像素通道\'210\',解码时按照 r2r1r0 g2g1g0 b2b1b0顺序进行解码.该选项默认开启.')
	Config_Priority.add_argument('--bf','--bitfirst',
						dest='PRIORITY',
						action='store_const',
						const='BIT',
						help='bit维度优先，如颜色通道\'RGB\'像素通道\'210\',解码时按照 r2g2b2 r1g1b1 r0g0b0顺序进行解码.该选项默认不开启. ')
	
	Parser.add_argument('-fd','--formartdetecter',
						dest='X',
						action='store',
						default='file',
						help='文件格式解析工具，默认为\'file\'命令，可选值：file,binwalk.'
						)

	Parser.add_argument('-a','--all',
						dest='TRYALL',
						action='store_true',
						default=False,
						help='使用所有已知方法.')

	Parser.add_argument('-E','--extract',
						dest='METHOD',
						action='store',
						default=None,
						help='根据指定策略解码,使用逗号对策略参数进行分隔，如:rgb,210,lsb.')
	
	Parser.add_argument('-O','--output',
						dest='OUTPUTFILE',
						action='store',
						default=None,
						help='使用-E参数时,指定输出文件.')
	Parser.add_argument('-sl', '--stringlength',
						dest='STRINGLENGTH',
						action='store',
						type=int,
						default=15,
						help='检测字符串长度(default:15).')	
	Parser.add_argument('--force',
						dest='FORCE',
						action='store_true',
						default=False,
						help='强制模式，不管有没有检测到信息，都显示结果.')	
	Parser.add_argument('-v', '--verbose',
						dest='VERBOSE',
						action='store_true',
						default=False,
						help='Run verbosely.')	
	Parser.add_argument('-V','--version', action='version', version="""TSTEG 1.0 -- A tool for lsb stego detect.目前是测试版本,有bug请直接跟我反馈。""")

	args = Parser.parse_args()
	args.DEBUG=DEBUG
	configration=CONFIGURE(**vars(args))
	TSTEG(**vars(configration))


	#Extractor(args).ExtractAll()

