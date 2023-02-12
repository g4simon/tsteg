import numpy as np
import itertools
from PIL import Image
import os
from core.module import IDENTIFIER
from core.default_methods import DEFAULT_METHODS



PLANE_DICT=dict(zip([''.join(i) for i in itertools.product('rgba','01234567')],range(32)))

class METHODS(object):
	'''
	Container for METHID
	'''
	def __init__(self, **kwargs):
		for (k, v) in kwargs.items():
			if v is not None:
				setattr(self, k, v)

	def Get_Methods(self):
		"""
		根据已知策略生成一个迭代器，当-a参数（all）设置时，返回默认迭代器
		返回迭代器格式
		[(像素方向,颜色通道,比特通道,有效位,颜色/比特优先级,[条件参数]),.....,....]
		[('xy','rgb','1024','LSB','COLOR',['r1', 'r0', 'r2', 'r4', 'g1', 'g0', 'g2', 'g4', 'b1', 'b0', 'b2', 'b4']).......]

		"""
		if hasattr(self,'TRYALL') and self.TRYALL:
			return(self.Default_Methods())
		result=[]
		if self.PRIORITY =='COLOR' or  self.PRIORITY =='AUTO':
			for bits_order in self.BITS_ORDERS:
				for colors_order in self.COLORS_ORDERS:
					temp=[''.join(i) for i in itertools.product(colors_order,bits_order)]
					result+=[(self.XY,''.join(colors_order),''.join(bits_order),self.SIGNIFICANTBIT,'cf',temp)]
		else:
			for bits_order in self.BITS_ORDERS:
				for colors_order in self.COLORS_ORDERS:
					temp=[''.join(i)[::-1] for i in itertools.product(bits_order,colors_order)]
					result+=[(self.XY,''.join(colors_order),''.join(bits_order),self.SIGNIFICANTBIT,'bf',temp)]
		if self.DEBUG:
			max_len=len(result) if self.SIGNIFICANTBIT !='ALL' else len(result)*2
			self.DISPLAY.Show_Debug(f'共有{max_len}种策略待检测......')
		return(result)


	def Default_Methods(self):
		result=[]
		for method in DEFAULT_METHODS:
			tempmethod={}
			if ',' not in method:
				self.DISPLAY.Show_Error(f'默认策略读取失败，请检查TSTEG版本和core/defalut_methods.py文件')
				exit(1)
			for item in method.split(','):
				if set(item.lower()).issubset(set('rgba')):
					if len(set(item))==len(item):
						tempmethod['COLORS_ORDER']=tuple(item.lower())
					else:
						self.DISPLAY.Show_Error(f'默认策略读取失败，请检查TSTEG版本和core/defalut_methods.py文件')
						exit(1)
				elif set(item).issubset(set('01234567')):
					if len(set(item))==len(item):
						tempmethod['BITS_ORDER']=tuple(item)
					else:
						self.DISPLAY.Show_Error(f'默认策略读取失败，请检查TSTEG版本和core/defalut_methods.py文件')
						exit(1)
				elif item.upper() in ['LSB','MSB']:
					tempmethod['SIGNIFICANTBIT']=item.upper()
				elif item.lower()=='cf':
					tempmethod['PRIORITY']='cf'
				elif item.lower()=='bf':
					tempmethod['PRIORITY']='bf'
				elif item in ['xy', 'xY', 'Xy', 'XY','x','X','y','Y','yx','yX','Yx','YX']:
					tempmethod['XY']=item
				if 'PRIORITY' not in tempmethod.keys():
					tempmethod['PRIORITY']='cf' 
			if tempmethod['PRIORITY']=='cf':
				temp=[''.join(i) for i in itertools.product(tempmethod['COLORS_ORDER'],tempmethod['BITS_ORDER'])]
			else:
				temp=[''.join(i)[::-1] for i in itertools.product(tempmethod['BITS_ORDER'],tempmethod['COLORS_ORDER'])]
			result+=[(tempmethod['XY'],''.join(tempmethod['COLORS_ORDER']),''.join(tempmethod['BITS_ORDER']),tempmethod['SIGNIFICANTBIT'],tempmethod['PRIORITY'],temp)]
		return(result)

class EXTRACTOR:
	def __init__(self,**kwargs):
		'''
		'''
		#读配置
		for (k, v) in kwargs.items():
			if v is not None:
				setattr(self, k, v)
        #读图片
		imgarr=np.array(Image.open(self.filename).convert("RGBA"))
		#维度为(纵坐标，横坐标，R7...R0 G7...G0 B7...B0 A7....A0)
		imgarr=np.array([imgarr>>i &1 for i in range(8)]).transpose(1,2,3,0)
		self.ImgArr=imgarr.reshape(*imgarr.shape[:-2],-1)
		self.IDENTIFIER=IDENTIFIER(**vars(self))

		
	def FormartIdentifier(self,bytes_str,method):
		self.IDENTIFIER.make_tmp_file(bytes_str)
		result=self.IDENTIFIER.check_all()
		if result:
			if len(result.keys())==1 and 'hexdump' in result.keys():
				return
			self.DISPLAY.Show_Method(method,True)
			self.DISPLAY.Show_Result(result)
		
		if hasattr(self,'METHOD') and hasattr(self,'OUTPUTFILE'):
			open(self.OUTPUTFILE,'wb').write(bytes_str)


		return()

	def ExtractBytes(self,method):
		"""
		根据配置条件进行解码尝试
		"""
		asix , color,bits,significantbit , priority , bitorder =method

		TempArr=self.ImgArr[:,:,:]
		if 'Y' in asix:
			TempArr=TempArr[::-1,:,:]
		if 'X' in asix:
			TempArr=TempArr[:,::-1,:]
		if asix.lower()=='yx' or asix.lower()=='y':
			TempArr=TempArr.transpose(1,0,2)
		TempSlice=[PLANE_DICT[i]for i in bitorder]
		TempArr=TempArr[:,:,TempSlice]
		FlatArray=TempArr.ravel()
		#如果设置了--limit 0，就取一维的全部数据
		TempLimit=self.LIMIT if self.LIMIT else FlatArray.shape[0]//8
		FlatArray=FlatArray[:TempLimit*8]
		Tag=np.zeros(TempLimit,np.uint8)
		if significantbit in ['ALL','LSB']:
			self.DISPLAY.Show_Method((asix,color,bits,'lsb',priority))
			for i in range(8):
				Tag |= FlatArray[7-i::8] << i
			self.FormartIdentifier(Tag.tobytes(),(asix,color,bits,'lsb',priority))
		if significantbit in ['ALL','MSB']:
			self.DISPLAY.Show_Method((asix,color,bits,'msb',priority))
			for i in range(8):
				Tag |= FlatArray[i::8] << i	
			self.FormartIdentifier(Tag.tobytes(),(asix,color,bits,'msb',priority))


		return()

	def ExtractAll(self):
		"""
		"""
		for method in self.METHODS.Get_Methods():
			self.ExtractBytes(method)
			#self.FormartIdentifier(bytes_str)
		return()



#test
