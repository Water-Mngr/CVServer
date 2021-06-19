<!--
 * @Copyrights: ©2021 @Laffery
 * @Date: 2021-05-09 13:24:34
 * @LastEditor: Laffery
 * @LastEditTime: 2021-06-19 16:02:11
-->
# API

> 🔌 API document of server

## Plant-identify

1. Url: **/id**

    Method: **POST**

    Body: 
        
        {
            image: image file
        }

    Return: 
    
        JSON {
            name: string(种名),
            intro: string(植物介绍), 
            advice: int(浇水建议天数，注意是该种植物的浇水建议，而不是当前盆栽的浇水建议),
            image: string(植物参考图片url)
        }

## Plant-distinguish

Url: **/compare**

Method: **POST**

Body: 
    
    {
        src: image file, // 想要分辨的源图像
        dst: image file // 想要与之分辨的目标图像
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
        image: image file
    }

Return: 

    JSON: { 
        problem: string (异常种类) 
    }

## Water Advice

Url: **/water**

Method: **POST**

Body: 

    {
        name: string (植物名称),
        date: string (上次浇水日期，格式为yy-mm-dd)
    }

Return: 

    JSON: { 
        advice: int (距离下次浇水天数，小于等于0说明需要浇水)
    }