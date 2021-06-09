<!--
 * @Copyrights: ©2021 @Laffery
 * @Date: 2021-05-09 13:24:34
 * @LastEditor: Laffery
 * @LastEditTime: 2021-06-09 15:25:22
-->
# API

> 🔌 API document of server

## Plant-identify

1. Url: **/id**

    Method: **POST**

    Body: 
        
        {
            image: file with extension png, jpg, jpeg or bmp
        }

    Return: 
    
        JSON { 
            sec_name: string(科名), 
            gen_name: string(属名), 
            kind_name: string(种名),
            intro: string(植物介绍), 
            advice: string(浇水建议),
            image: bytes[](植物参考图片)
        }

## Plant-distinguish

Url: **/compare**

Method: **POST**

Body: 
    
    {
        src: file with extension png, jpg, jpeg or bmp, // 想要分辨的源图像
        dst: file with extension png, jpg, jpeg or bmp // 想要与之分辨的目标图像
    }

如拍的照片为src，要与dst比较

Return: 

    JSON: { 
        similarity: float (相似度，＞ 1可认定为同一植物)
    }

## Plant-exception-detection

Url: **/detect**

Method: **POST**

Body: 

    {
        image: file with extension png, jpg, jpeg or bmp
    }

Return: 

    JSON: { 
        problems: string (异常种类) 
    }
