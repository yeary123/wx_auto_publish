# 在 mypackage/__init__.py 中  
  
# 导入模块  
from .base import config  
from .base import logs
  
# 定义 __all__ 列表  
__all__ = ['base.config', 'base.logs']