<!--
 * @Copyrights: ©2021 @Laffery
 * @Date: 2021-05-09 13:24:34
 * @LastEditor: Laffery
 * @LastEditTime: 2021-06-19 13:18:39
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
            name: string(种名),
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
        match: bool (是否匹配)
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
        problem: string (异常种类) 
    }
