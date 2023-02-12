import os
import re
import itertools
from core.display import Display
from core.extractor import METHODS,EXTRACTOR



#def Iterator_Permutations(inputstr):
#	return([x for i in range(1,len(inputstr)+1) for x in itertools.permutations(inputstr,i)])

#def Iterator_Combinations(inputstr):
#	return([x for i in range(1,len(inputstr)+1) for x in itertools.combinations(inputstr,i)])



class CONFIGURE(object):
	'''
	Container for CONFIGURE
	'''
	def __init__(self, **kwargs):
		'''
		用途：
		初始化策略，并对输入进行解析

		输入值：
		@filename           string   待解析文件名
		@COLORS             string   颜色通道参数
		@LIMIT              int      解码字节长度, 0 = 不限制 (default: 1024)
		@XY                 string   像素解压顺序(default: 'ALL').大写表示逆序，如: ALL,xy,yx,XY,YX,xY,Xy...
		@BITS @BITPLANE     string   bit有效位顺序,可以使用逗号进行分隔指定范围。
		@BITCOUNT           string   bit有效位数量,可以使用逗号进行分隔指定范围。
		@SIGNIFICANTBIT     string   lsb/msb，有效位填充顺序，选择范围为:ALL,LSB,MSB
		@PRIORITY           string   维度优先级，选择范围为:AUTO,COLOR,BIT
		@X @FORMARTDETECTER string   文件格式解析工具，默认为'file'命令，可选值：file,binwalk.
		@TRYALL             string   使用已知策略进行解析。
		@METHOD             string   根据指定策略解码.
		@OUTPUTFILE	        string   指定METHOD参数后,指定输出文件.
		@VERBOSE            string   查看更多输出.
		@DEBUG              bool     debug标记
		@DISPLAY			obj      打印类
		@BINDIR				string   输出二进制文件的文件夹

		
		@BITS_ORDERS        tuple in list  比特通道策略，一个策略是一个tuple
		@COLORS_ORDERS      tuple in list  颜色通道策略，一个策略是一个tuple


		返回值：
		None
		'''
		self.BINDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin") + os.sep

		for (k, v) in kwargs.items():
			setattr(self, k, v)
		self.DISPLAY=Display(**vars(self))

		if hasattr(self,'BITS'):#BITS 转化为BITPLANE,便于后续代码的理解
			setattr(self,'BITPLANE',self.BITS)
			delattr(self,'BITS')
		if hasattr(self,'X'):#X 转化为FORMARTDETECTER,便于后续代码的理解
			setattr(self,'FORMARTDETECTER',self.X)
			delattr(self,'X')
		if hasattr(self,'METHOD'):
			if self.METHOD:
				self.Method_Parser(self.METHOD)
				return
		if hasattr(self,'TRYALL'):
			if self.TRYALL:
				return

		self.Configration_Parser()


#	def __getitem__(self,key):
#		return(self.__getattribute__(key))

	def Configration_Parser(self):
		# 检测配置策略是否合法
		## 查看PRIORITY是否合法
		if hasattr(self,'PRIORITY'):
			if self.PRIORITY not in ['AUTO','COLOR','BIT']:
				self.DISPLAY.Show_Alert(f'错误的PRIORITY:{self.PRIORITY},使用默认值：\'AUTO\'')
				self.PRIORITY='AUTO'


		## 如果同时配置了BITCOUNT和BITS参数，则仅按照BITS处理。
		if hasattr(self,'BITCOUNT') and hasattr(self,'BITPLANE'):
			if self.BITCOUNT is not None and self.BITPLANE is not None:
				delattr(self,'BITCOUNT')
			elif self.BITCOUNT is None and self.BITPLANE is None:
				self.BITCOUNT='1,2,3,4'

		## 解析BITPLANE参数，转化为BITS_ORDERS
		if hasattr(self,'BITPLANE'):
			if self.BITPLANE:
				self.BITS_ORDERS=self.Bitplane_Parser(self.BITPLANE)
				if self.BITS_ORDERS is None and self.BITPLANE is not None:
					self.DISPLAY.Show_Alert(f'错误的\'BITPLANE\'/\'-bp\'参数，{self.BITPLANE}，使用\'0-3\'作为替代')
					self.BITPLANE='0-3'
					self.BITS_ORDERS=self.Bitplane_Parser(self.BITPLANE)
				self.DISPLAY.Show_Debug(f'从BITPLANE获取{len(self.BITS_ORDERS)}种策略，BIT_ORDERS:{self.BITS_ORDERS}')

		
		## 解析BITCOUNT，转化为BITS_ORDERS
		if hasattr(self,'BITCOUNT'):
			if self.BITCOUNT:
				self.BITS_ORDERS=self.Bitcount_Parser(self.BITCOUNT)
				if self.BITS_ORDERS is None and self.BITCOUNT is not None:
					self.DISPLAY.Show_Alert(f'错误的\'BITCOUNT\'/\'-bc\'参数，{self.BITCOUNT}，使用\'1,2,3,4\'作为替代')
					self.BITCOUNT='1,2,3,4'
					self.BITS_ORDERS=self.Bitcount_Parser(self.BITCOUNT)
				elif self.BITCOUNT is None:
					self.DISPLAY.Show_Alert(f'未定义\'BITCOUNT\'/\'-bc\'参数，使用\'1,2,3,4\'作为替代')
					self.BITCOUNT='1,2,3,4'
					self.BITS_ORDERS=self.Bitcount_Parser(self.BITCOUNT)

				self.DISPLAY.Show_Debug(f'''从BITCOUNT获取{len(self.BITS_ORDERS)}种策略，BIT_ORDERS:{self.BITS_ORDERS}''')
			
		## 解析COLORS，转化为COLORS_ORDERS
		if hasattr(self,'COLORS'):
			self.COLORS_ORDERS=self.Colors_Parser(self.COLORS)
			if self.COLORS_ORDERS is None and self.COLORS is not None:
				self.DISPLAY.Show_Alert(f'错误的\'COLORS\'/\'-c\'参数，{self.COLORS}，使用\'rgb\'作为替代')
				self.COLORS='rgb'
				self.COLORS_ORDERS=self.Colors_Parser(self.COLORS)
			elif self.COLORS is None:
				self.DISPLAY.Show_Alert(f'未定义\'COLORS\'/\'-c\'参数，使用\'rgb\'作为替代')
				self.COLORS='rgb'
				self.COLORS_ORDERS=self.Colors_Parser(self.COLORS)

			self.DISPLAY.Show_Debug(f'''从RGBA获取{len(self.COLORS_ORDERS)}种策略，COLORS_ORDERS:{self.COLORS_ORDERS}''')
		

	def Bitcount_Parser(self,bitcount_string,ALL_BITS=[str(i) for i in range(8)]):
		'''
		用途：
		用于解析-bc ,--bitcount的参数值，返回对应策略列表

		输入值：
		@bitcount_string   string   参数-bc ,--bitcount 的相应字符串，返回对应的策略列表
		@ALL_BITS          string in list    所有通道位数，默认是8位,按照顺序从低到高
		
		返回值：
		策略列表，里面每一个元组都是比特通道的相应顺序，如检测1024、0123、0通道的策略列表格式为：
		[('1','0','2','4'),('0','1','2','3'),('0',)]
		'''
		if bitcount_string is not None:  #为空直接返回空
			if bitcount_string in [str(i) for i in range(1,len(ALL_BITS)+1)]: #如果范围是1至ALL_BITS长度+1的字符串，直接返回正序和倒序的列表
				result=[ tuple(ALL_BITS)[:ALL_BITS.index(bitcount_string)],tuple(ALL_BITS)[-(1+len(ALL_BITS)-ALL_BITS.index(bitcount_string))::-1]]
			elif ',' in bitcount_string:  #如果有逗号，根据逗号依次解析
				result=[]
				for s in bitcount_string.split(','):
					temp=self.Bitcount_Parser(bitcount_string=s,ALL_BITS=ALL_BITS)
					if temp:
						result+=temp
			elif 8>=len(bitcount_string)>=2 and set(bitcount_string).issubset(set('01')): #如果长度超过2且均为01组合，掩码模式，补齐位数之后直接返回正序和倒序列表
				while len(bitcount_string)<len(ALL_BITS):
					bitcount_string='0'+bitcount_string
				t=tuple([i for i in ALL_BITS if bitcount_string[len(bitcount_string)-ALL_BITS.index(i)-1]=='1'])
				result=[t,t[::-1]]
				self.DISPLAY.INFO(f'检测到\'BITCOUNT\'/\'-bc\'参数使用了掩码模式，掩码为{bitcount_string}')
			elif '-' in bitcount_string and len(bitcount_string)==3 and bitcount_string[0] in ALL_BITS and bitcount_string[2] in ALL_BITS: #如果含有- 说明是范围模式，根据范围分别解析
				if bitcount_string[0]==bitcount_string[2]:
					result=self.Bitcount_Parser(bitcount_string=bitcount_string[0],ALL_BITS=ALL_BITS)
				else:
					step=-1 if ALL_BITS.index(bitcount_string[0])>ALL_BITS.index(bitcount_string[2]) else 1
					result=[]
					for i in range(ALL_BITS.index(bitcount_string[0]),ALL_BITS.index(bitcount_string[2])+step,step):
						result+=self.Bitcount_Parser(bitcount_string=ALL_BITS[i],ALL_BITS=ALL_BITS)
			else:#如果都不是以上情况直接返回None
				return
			return list(set(result))

	def Colors_Parser(self,colors_string,ALL_COLORS=['r','g','b','a']):
		'''
		用途：
		用于解析-c ,--colors的参数值，返回对应策略列表

		输入值：
		@colors_string   string   参数-c ,--colors 的相应字符串，返回对应的策略列表
		@ALL_COLORS      string in list  所有通道，默认是 rgba

		返回值：
		策略列表，里面每一个元组都是颜色通道的相应顺序，全排列，如检测rg通道的策略列表格式为：
		[('r',), ('r', 'g'), ('g',), ('g', 'r')]
		'''
		if colors_string is not None:
			colors_string=colors_string.lower().lstrip(',').rstrip(',')
			if set(colors_string).issubset(set(ALL_COLORS)) and len(set(colors_string))==len(colors_string): #如果取值范围是在颜色通道范围之内，并且不包含重复值
				result=[x for i in range(1,len(colors_string)+1) for x in itertools.permutations(colors_string,i)]
			elif ',' in colors_string: #如果有逗号，根据逗号依次解析
				result=[]
				for s in colors_string.split(','):
					temp = self.Colors_Parser(s,ALL_COLORS=ALL_COLORS)
					if temp:
						result+=temp
			else:#如果不是以上情况直接返回None
				return
			return list(set(result))


	def Bitplane_Parser(self,bitplane_string,ALL_BITS=[str(i) for i in range(8)]):
		'''
		用途：
		用于解析-bp ,--bitplane的参数值，返回对应策略列表

		输入值：
		@bitplane_string   string   参数-bp ,--bitplane 的相应字符串，返回对应的策略列表
		@ALL_BITS          string in list    所有通道位数，默认是8位,按照顺序从低到高

		返回值：
		策略列表，里面每一个元组都是比特通道的相应顺序，如检测1024、0123、0通道的策略列表格式为：
		[('1','0','2','4'),('0','1','2','3'),('0',)]
		'''

		if bitplane_string is not None:
			bitplane_string=bitplane_string.lstrip(',').rstrip(',')
			if set(bitplane_string).issubset(ALL_BITS) and len(set(bitplane_string))==len(bitplane_string):#如果取值范围是在bit通道范围之内，并且不包含重复值
				result=[tuple([i for i in bitplane_string]),tuple([i for i in bitplane_string[::-1]])] #返回正序和倒序序列
			elif ',' in bitplane_string:
				result=[]
				for s in bitplane_string.split(','):
					temp = self.Bitplane_Parser(s,ALL_BITS=ALL_BITS)
					if temp:
						result+=temp
			elif '-' in bitplane_string and len(bitplane_string)==3 and bitplane_string[0] in ALL_BITS and bitplane_string[2] in ALL_BITS: #如果含有- 说明是范围模式，根据范围分别解析
				if bitplane_string[0]==bitplane_string[2]:
					result=self.Bitplane_Parser(bitplane_string[0],ALL_BITS=ALL_BITS)
				else:
					step=-1 if ALL_BITS.index(bitplane_string[0])>ALL_BITS.index(bitplane_string[2]) else 1
					result=[]
					if step*(ALL_BITS.index(bitplane_string[2])-ALL_BITS.index(bitplane_string[0]))>5:
						self.DISPLAY.Show_Error(f'\'BITPLANE\'/\'-bp\'参数{bitplane_string}使用范围过大，极大降低解码效率，请重新选择')
						exit(1)
					s=''.join([ALL_BITS[i] for i in range(ALL_BITS.index(bitplane_string[0]),ALL_BITS.index(bitplane_string[2])+step,step)])
					result=[x for i in range(1,len(s)+1) for x in itertools.permutations(s,i)]
			else:#如果不是以上情况直接返回None
				return
			return list(set(result))


	def Method_Parser(self,method):
		if ',' not in method:
			self.DISPLAY.Show_Error(f'错误的-e参数：{method}')
			exit(1)
		for item in method.split(','):
			if set(item.lower()).issubset(set('rgba')):
				if len(set(item))==len(item):
					self.COLORS_ORDERS=[tuple(item.lower())]
				else:
					self.DISPLAY.Show_Error(f'错误的-e参数：{method},colorplane参数有重复值')
			elif set(item).issubset(set('01234567')):
				if len(set(item))==len(item):
					self.BITS_ORDERS=[tuple(item)]
				else:
					self.DISPLAY.Show_Error(f'错误的-e参数：{method},bitplane参数有重复值')
			elif item.upper() in ['LSB','MSB']:
				self.SIGNIFICANTBIT=item.upper()
			elif item.lower()=='cf':
				self.PRIORITY='COLOR'
			elif item.lower()=='pf':
				self.PRIORITY='BIT'
			elif item in ['xy', 'xY', 'Xy', 'XY','x','X','y','Y','yx','yX','Yx','YX']:
				self.XY=item





class TSTEG:
	'''
	'''
	def __init__(self,**kwargs):
		for (k, v) in kwargs.items():
			if v is not None:
				setattr(self, k, v)
		self.METHODS=METHODS(**vars(self))
		#print(dir(self))
		self.EXTRACTOR=EXTRACTOR(**vars(self))
		#print(dir(self))
		self.EXTRACTOR.ExtractAll()



#test
#import time
#a='xxxx'
#print(f"hahaha {a} ",end='\r')
#time.sleep(1)
#print(f'xxxxxxxxx')




#hasattr(xxxxxxx)

