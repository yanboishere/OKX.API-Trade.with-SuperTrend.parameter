为了使用Cython加速TA-Lib库中的函数运行，我们需要按照以下步骤进行：

1. 安装Cython和TA-Lib库

```
pip install cython
pip install TA-Lib
```

2. 创建一个名为`talib_ext.pyx`的文件，用于定义Cython扩展模块

```
import numpy as np
cimport numpy as np
cimport talib

DTYPE = np.double
ctypedef np.double_t DTYPE_t

def sma(np.ndarray[DTYPE_t, ndim=1] prices, int period):
    cdef np.ndarray[DTYPE_t, ndim=1] output = np.empty_like(prices)
    talib.SMA(prices, period, output)
    return output
```

3. 创建`setup.py`文件，用于构建和安装Cython扩展模块

```
from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    name='TALibExt',
    ext_modules=cythonize('talib_ext.pyx'),
    include_dirs=[numpy.get_include()],
)
```

4. 编译并安装Cython扩展模块

```
python setup.py build_ext --inplace
python setup.py install
```

5. 在主程序中导入Cython扩展模块，并调用其中的函数来替代原生的TA-Lib函数

```
from talib_ext import sma

# 计算SMA指标
sma_values = sma(close_prices, period)
```
