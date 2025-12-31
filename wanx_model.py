import dashscope
from dashscope import ImageSynthesis

def generate_wanx_image(prompt, api_key):
    """
    调用通义万相模型生成图片
    """
    # 必须设置 API KEY
    dashscope.api_key = api_key
    
    try:
        # 调用通义万相 API
        rsp = ImageSynthesis.call(
            model=ImageSynthesis.Models.wanx_v1,  # 指定模型版本
            prompt=prompt,                        # 提示词
            n=1,                                  # 生成数量
            size='1024*1024'                      # 图片分辨率
        )
        
        # 解析返回结果
        if rsp.status_code == 200:
            # 获取图片 URL
            if rsp.output and rsp.output.results:
                return rsp.output.results[0].url
            else:
                return None
        else:
            # 如果报错，返回错误信息
            return f"Error: {rsp.code}, {rsp.message}"
            
    except Exception as e:
        return f"调用失败: {str(e)}"